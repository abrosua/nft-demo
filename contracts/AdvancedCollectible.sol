// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@chainlink/contracts/src/v0.8/VRFConsumerBaseV2.sol";

// Create an NFT contract
// The tokenURI can be one of the 3 different dogs (randomly selected)

contract AdvancedCollectible is VRFConsumerBaseV2, ERC721, ERC721URIStorage {
    // events for each mapping update
    event AssignBreed(uint256 tokenId, uint256 breedIndex); // tokenIdToBreed
    event RequestCollectible(uint256 requestId, address owner); // requestIdToOwner

    // init variables
    uint256 public tokenCounter;
    VRFCoordinatorV2Interface internal _coordinator;
    enum Breed {
        PUG,
        SHIBA_INU,
        ST_BERNARD
    }
    // string[] _breedURIs;
    mapping(uint256 => Breed) public tokenIdToBreed;
    mapping(uint256 => address) public requestIdToOwner;

    // VRF variables
    uint64 public immutable subscriptionId;
    bytes32 public immutable keyHash;
    uint256 public requestId;
    uint32 _callbackGasLimit = 500000;
    uint16 _minRequestConfirmations = 3; // The default is 3, but you can set this higher.
    uint32 _numWords = 1; // number of random words to retrieve

    constructor(
        address _coordinatorAddress,
        uint64 _subscriptionId,
        bytes32 _keyHash
    )
        // string[] memory _inputBreedURIs
        VRFConsumerBaseV2(_coordinatorAddress)
        ERC721("Puppies Demo", "PUD")
    {
        tokenCounter = 0;
        // init VRF v2 coordinator
        _coordinator = VRFCoordinatorV2Interface(_coordinatorAddress);
        subscriptionId = _subscriptionId;
        keyHash = _keyHash;
        // _breedURIs = _inputBreedURIs; // use the base token later!
    }

    /*
     * To mint a specific collectible for a specific user (address) that calls it!
     */
    function createCollectible() public returns (uint256) {
        requestId = _coordinator.requestRandomWords(
            keyHash,
            subscriptionId,
            _minRequestConfirmations,
            _callbackGasLimit,
            _numWords
        );
        requestIdToOwner[requestId] = msg.sender;
        emit RequestCollectible(requestId, msg.sender);
        return requestId;
    }

    // manually set the token URI for a specific token ID
    function setTokenURI(uint256 tokenId, string memory _tokenURI) public {
        require(
            _isApprovedOrOwner(_msgSender(), tokenId),
            "ERC721: Caller is not approved!"
        );
        _setTokenURI(tokenId, _tokenURI);
    }

    // The following functions are overrides required by Solidity.
    // due to the ERC721URIStorage inherittance

    function _burn(
        uint256 tokenId
    ) internal override(ERC721, ERC721URIStorage) {
        super._burn(tokenId);
    }

    function tokenURI(
        uint256 tokenId
    ) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(
        bytes4 interfaceId
    ) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }

    // override the fulfill random callback
    function fulfillRandomWords(
        uint256 _requestId,
        uint256[] memory _randomWords
    ) internal override {
        require(_randomWords.length > 0, "Random words NOT found!");
        // Pick the random breed type
        uint256 breedIndex = _randomWords[0] % (uint256(type(Breed).max) + 1);
        Breed breed = Breed(breedIndex);
        // string memory breedURI = _breedURIs[breedIndex];
        // Assign the value
        uint256 newTokenId = tokenCounter;
        tokenIdToBreed[newTokenId] = breed;

        // Mint the token
        _safeMint(requestIdToOwner[_requestId], newTokenId);
        // _setTokenURI(newTokenId, breedURI); // automatically set the URI based on breed
        tokenCounter += 1; // update the token counter!
        // Emit event
        emit AssignBreed(newTokenId, breedIndex);
    }
}
