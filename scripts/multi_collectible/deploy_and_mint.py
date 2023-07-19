import time
import random
from typing import Optional
from brownie import MultiCollectible, network, config
from scripts.utils import (
    get_account,
    get_contract,
    LOCAL_BLOCKCHAIN_ENV,
    OPENSEA_BASE_URL,
)
from scripts.multi_collectible.create_metadata import pin_metadata_to_ipfs
from scripts.vrf_subscription import (
    get_subscription,
    register_consumer,
)


def deploy():
    network_id = network.show_active()
    # pin the assets to IPFS and obtain the base token URI
    base_uri = f"ipfs://{pin_metadata_to_ipfs()}/"
    print(f"The ERC1155 token base URI is available here: '{base_uri}")

    # get the VRF subscription ID
    subscription_id = get_subscription()
    key_hash = config["networks"][network_id]["key_hash"]  # aka Gas Lane
    # deploy the collectible
    multi_collectible = MultiCollectible.deploy(
        get_contract(contract_name="eth_usd_price_feed").address,
        get_contract(contract_name="vrf_coordinator").address,
        subscription_id,
        key_hash,
        base_uri,
        {"from": get_account()},
        publish_source=config["networks"].get(network_id, {}).get("verify", False),
    )
    register_consumer(
        contract_address=multi_collectible.address, subscription_id=subscription_id
    )
    # The NFT token URL
    collection_url = f"{OPENSEA_BASE_URL}/{network_id}/{multi_collectible.address}/"
    print(f"Successfully deployed the ERC1155 collection at '{collection_url}'")
    return multi_collectible


def mint(
    collectible, account, rng: Optional[int] = None, pay_wei: Optional[int] = None
):
    print(f"Minting collectible ...")
    # mint the collectible here
    pay_wei = int(collectible.getEntranceFee() * 1.01) if pay_wei is None else pay_wei
    mint_tx = collectible.createCollectible({"from": account, "value": pay_wei})
    mint_tx.wait(1)
    mint_event = mint_tx.events["RequestCollectible"]
    print(f"User '{mint_event['owner']}' successfully paid {mint_event['amount']} Wei!")

    # handle the VRF fulfill if running on local
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        print(f"Manually fulfilling the VRF random request ...")
        vrf = get_contract(contract_name="vrf_coordinator")
        # random number from 100 to 100,000
        winning_rng = random.randint(100, 100000) if rng is None else rng
        fulfill_tx = vrf.fulfillRandomWordsWithOverride(
            mint_event["requestId"],
            collectible.address,
            [winning_rng],
            {"from": account},
        )
        fulfill_tx.wait(1)
    else:
        print(f"Waiting for the VRF fulfill ...")
        time.sleep(60)
    print(f"Successfully minted the token!")


def main():
    deploy()
    mint(collectible=MultiCollectible[-1], account=get_account())
