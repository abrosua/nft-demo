// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/token/ERC1155/extensions/ERC1155Burnable.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";

import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract MultiCollectible is
    VRFConsumerBaseV2,
    ERC1155,
    Ownable,
    ERC1155Burnable
{
    event RequestCollectible(uint256 requestId, address owner, uint256 amount);
    event MintedCollectible(address owner, uint256 breed, uint256 amount);

    // Contract name and symbol
    string public name;
    string public symbol;

    // init variables
    AggregatorV3Interface internal _dataFeed;
    VRFCoordinatorV2Interface internal _coordinator;
    enum Breed {
        PUG,
        SHIBA_INU,
        ST_BERNARD
    }
    struct BreedInfo {
        string breedName;
        uint256 multiplierPercentage;
        uint256 usdMinimumPrice;
    }
    BreedInfo[3] public listBreedInfo;
    struct OwnerRecord {
        address owner;
        uint256 amount;
    }
    mapping(uint256 => OwnerRecord) public requestIdToOwnerRecord;

    // VRF variables
    uint64 public immutable subscriptionId;
    bytes32 public immutable keyHash;
    uint256 public requestId;
    uint32 _callbackGasLimit = 500000;
    uint16 _minRequestConfirmations = 3; // The default is 3, but you can set this higher.
    uint32 _numWords = 1; // number of random words to retrieve

    constructor(
        string memory _name,
        string memory _symbol,
        address _dataFeedAddress,
        address _coordinatorAddress,
        uint64 _subscriptionId,
        bytes32 _keyHash,
        string memory _baseUri
    ) VRFConsumerBaseV2(_coordinatorAddress) ERC1155(_baseUri) {
        // init. contract info
        name = _name;
        symbol = _symbol;
        // init. chainlink price feed (dynamic data feed address)
        _dataFeed = AggregatorV3Interface(_dataFeedAddress);
        // init VRF v2 coordinator
        _coordinator = VRFCoordinatorV2Interface(_coordinatorAddress);
        subscriptionId = _subscriptionId;
        keyHash = _keyHash;
        // init. list breed info
        listBreedInfo[0] = BreedInfo("PUG", 23, 5);
        listBreedInfo[1] = BreedInfo("SHIBA_INU", 48, 10);
        listBreedInfo[2] = BreedInfo("ST_BERNARD", 100, 20);
    }

    function setURI(string memory newuri) public onlyOwner {
        _setURI(newuri);
    }

    function uri(uint256 tokenId) public view override returns (string memory) {
        return
            string(
                abi.encodePacked(
                    super.uri(0),
                    Strings.toString(tokenId),
                    ".json"
                )
            );
    }

    /*
     * To determine the minimum price for each token ID in Wei
     */
    function getTokenMinimumPrice(
        uint256 _tokenId
    ) public view returns (uint256) {
        (, int answer, , , ) = _dataFeed.latestRoundData();
        uint256 price = uint256(answer * 10000000000);
        uint256 precision = 1 * 10 ** 18;
        BreedInfo memory breedInfo = listBreedInfo[_tokenId];
        return (breedInfo.usdMinimumPrice * precision * precision) / price;
    }

    /*
     * To determine the global minimum price to spend.
     */
    function getEntranceFee() public view returns (uint256) {
        return getTokenMinimumPrice(2);
    }

    /*
     * To mint X amount of randomly selected token!
     * The amount will be based on paid transaction.
     */
    function createCollectible() public payable returns (uint256) {
        require(msg.value >= getEntranceFee(), "Insufficient fee!");
        requestId = _coordinator.requestRandomWords(
            keyHash,
            subscriptionId,
            _minRequestConfirmations,
            _callbackGasLimit,
            _numWords
        );
        requestIdToOwnerRecord[requestId] = OwnerRecord(msg.sender, msg.value);
        emit RequestCollectible(requestId, msg.sender, msg.value);
        return requestId;
    }

    // override the fulfill random callback
    function fulfillRandomWords(
        uint256 _requestId,
        uint256[] memory _randomWords
    ) internal override {
        require(_randomWords.length > 0, "Random words NOT found!");
        // Pick the random breed type and calulate the token amount
        uint256 breedId = _randomWords[0] % (uint256(type(Breed).max) + 1);
        OwnerRecord memory ownerRecord = requestIdToOwnerRecord[_requestId];
        uint256 breedPrice = getTokenMinimumPrice(breedId);
        uint256 tokenAmount = ownerRecord.amount / breedPrice;

        // Mint the token
        _mint(ownerRecord.owner, breedId, tokenAmount, "");
        // Emit event
        emit MintedCollectible(ownerRecord.owner, breedId, tokenAmount);
    }
}
