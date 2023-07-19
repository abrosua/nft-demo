import time, random
from typing import Optional
from brownie import AdvancedCollectible, network
from .create_metadata import generate_metadata
from scripts.utils import (
    get_account,
    get_contract,
    BREED_NAMES,
    OPENSEA_BASE_URL,
    LOCAL_BLOCKCHAIN_ENV,
)
from scripts.utils_ipfs import add_to_ipfs


def create_collectible(
    collectible, account, rng: Optional[int] = None, is_set_uri: bool = False
):
    print(f"Creating collectible ...")
    # create the collectible here
    create_tx = collectible.createCollectible({"from": account})
    create_tx.wait(1)
    request_id = create_tx.events["RequestCollectible"]["requestId"]
    # handle the VRF fulfill if running on local
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        print(f"Manually fulfilling the VRF random request ...")
        vrf = get_contract(contract_name="vrf_coordinator")
        # random number from 100 to 100,000
        winning_rng = random.randint(100, 100000) if rng is None else rng
        fulfill_tx = vrf.fulfillRandomWordsWithOverride(
            request_id, collectible.address, [winning_rng], {"from": account}
        )
        fulfill_tx.wait(1)
    else:
        print(f"Waiting for the VRF fulfill ...")
        time.sleep(60)
    # print(f"Request ID: {request_id}, Token Storage: {collectible.tokenIdToBreed()}")

    # set the Token URI here
    last_token_id = int(collectible.tokenCounter() - 1)
    token_uri = ""
    if is_set_uri:
        print(f"Proceed to set the Token URI for #{last_token_id}")
        token_uri = set_token_uri(
            collectible=collectible, account=account, token_id=last_token_id
        )

    # check the created NFT
    token_url = f"{OPENSEA_BASE_URL}/{network.show_active()}/{collectible.address}/{last_token_id}"
    breed_id = collectible.tokenIdToBreed(last_token_id)
    breed = BREED_NAMES[breed_id]
    print(
        f"Finished! The {breed} NFT is now available in '{token_url}'! "
        f"With Token URI: '{collectible.tokenURI(last_token_id)}'."
    )
    return create_tx, token_uri


def set_token_uri(collectible, account, token_id: int):
    token_metadata = generate_metadata(token_id=token_id)  # create metadata
    token_uri = f"ipfs://{add_to_ipfs(token_metadata)}"  # create token URI
    set_uri_tx = collectible.setTokenURI(token_id, token_uri, {"from": account})
    set_uri_tx.wait(1)
    return token_uri


def main():
    create_collectible(
        collectible=AdvancedCollectible[-1], account=get_account(), is_set_uri=True
    )
