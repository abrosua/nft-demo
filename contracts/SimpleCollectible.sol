// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";

contract SimpleCollectible is ERC721, ERC721URIStorage {
    uint256 public tokenCounter;

    constructor() ERC721("Puppies NFT", "PUP") {
        tokenCounter = 0;
    }

    /*
     * To mint a specific collectible for a specific user (address) that calls it!
     */
    function createCollectible(
        string memory inputTokenURI
    ) public returns (uint256) {
        uint256 newTokenId = tokenCounter;
        _safeMint(msg.sender, newTokenId);
        _setTokenURI(newTokenId, inputTokenURI); // manually handle the URI storage
        tokenCounter += 1; // update the token counter!
        return newTokenId;
    }

    // The following functions are overrides required by Solidity.

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
}
