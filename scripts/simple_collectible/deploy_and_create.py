from brownie import SimpleCollectible, network
from scripts.utils import get_account, OPENSEA_BASE_URL


sample_token_uri = "https://ipfs.io/ipfs/Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json"


def deploy_and_create():
    account = get_account()
    simple_collectible = SimpleCollectible.deploy({"from": account})
    create_tx = simple_collectible.createCollectible(
        sample_token_uri, {"from": account}
    )
    create_tx.wait(1)
    last_token_id = simple_collectible.tokenCounter() - 1
    token_url = f"{OPENSEA_BASE_URL}/{network.show_active()}/{simple_collectible.address}/{last_token_id}"
    print(f"Finished! The NFT is now available in '{token_url}'")
    return simple_collectible


def main():
    deploy_and_create()
