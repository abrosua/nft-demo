# Simple NFT playground (ERC-721 and ERC-1155)

Works to uncover in this project:
1. Creating a ERC-721 and ERC-1155 contract with Brownie and [OpenZeppelin](https://docs.openzeppelin.com/contracts/4.x/erc20). Deployed on [Sepolia Testnet](https://sepolia.dev/).
2. Generating NFT metadata and pinning files into IPFS ([pinata](https://www.pinata.cloud/))

There are 3 types of NFT collectibles:
1. Simple Collectible (`scripts/simple_collectible/`)
    - A simple ERC-721 where users manually defined the Token URI everytime they mint a token.
    - There is no verification method on this collectible, therefore anyone can mint the token and impose any URI on it freely.
2. Advanced Collectible (`scripts/advanced_collectible/`)
    - An [ERC-721 token](https://sepolia.etherscan.io/address/0x7546E10CD77D82c48E35409a9310999Da1Ad05aE) that will randomly choose an image (in `img/`) using VRF Coordinator V2 everytime a token is minted.
    - The scripts are capable of generating the suitable metadata for each minted token, automatically pin it to IPFS, and set the token URI.
    - Only owner and approved (available in `ERC721URIStorage`) senders that can set the token URI.
3. Multi Collectible (`scripts/advanced_collectible/`)
    - An [ERC-1155 token](https://sepolia.etherscan.io/address/0x7296CD7371abCC79Add2069D06b418a21e750650) that will randomly choose which token will be minted everytime a user tries to create a collectible.
    - All the available assets should be pinned to IPFS before deployment, since the contract does not use URI storage.
    - Token URI will be automatically generated using the initialized base URI and token's contract ID.
    - The mint function, `createCollectible()`, is `payable` and the paid ETH amount will be used to determine the amount of NFT tokens to be minted according to the selected collection ID.
    - The token base URI can be updated after deployment by the owner only.