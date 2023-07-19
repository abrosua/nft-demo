from brownie import AdvancedCollectible, network, config
from scripts.utils import get_account, get_contract, BREED_TOKEN_URIS
from scripts.advanced_collectible.create_collectible import create_collectible
from scripts.vrf_subscription import (
    get_subscription,
    register_consumer,
)


def deploy():
    network_id = network.show_active()
    # get the VRF subscription ID
    subscription_id = get_subscription()
    key_hash = config["networks"][network_id]["key_hash"]  # aka Gas Lane
    vrf = get_contract("vrf_coordinator")
    # deploy the collectible
    advanced_collectible = AdvancedCollectible.deploy(
        vrf.address,
        subscription_id,
        key_hash,
        # list(BREED_TOKEN_URIS.values()),
        {"from": get_account()},
        publish_source=config["networks"].get(network_id, {}).get("verify", False),
    )
    register_consumer(
        contract_address=advanced_collectible.address, subscription_id=subscription_id
    )
    return advanced_collectible


def deploy_and_create():
    # deploying the collectible
    collectible = deploy()
    # create/mint the first NFT
    create_collectible(collectible=collectible, account=get_account(), is_set_uri=True)


def main():
    deploy_and_create()
