from typing import Optional
from brownie import (
    accounts,
    config,
    network,
    MockV3Aggregator,
    VRFCoordinatorV2Mock,
    LinkToken,
    Contract,
)
from web3 import Web3


DECIMALS = 8
STARTING_PRICE = 200000000000
BASE_FEE = 100000000000000000  # VRF Coordinator mock base fee
GAS_PRICE_LINK = 1000000000  # VRF Coordinator mock gas price link

# chain required for Mocking
LOCAL_BLOCKCHAIN_ENV = [
    "development",  # run using ganache-cli
    "ganache-local",  # ganache UI for mock contract deployment!
]
# chain required for Forking
FORKED_LOCAL_ENV = [
    "mainnet-fork",  # Ganache CLI, ethereum mainnet forked
]
# contract name to mock mapping
CONTRACT_TO_MOCK = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorV2Mock,
    "link_token": LinkToken,
}

# NFT variables
OPENSEA_BASE_URL = "https://testnets.opensea.io/assets"
BREED_TOKEN_URIS = {
    "PUG": "https://ipfs.io/ipfs/Qmd9MCGtdVz2miNumBHDbvj8bigSgTwnr4SbyH6DNnpWdt?filename=0-PUG.json",
    "SHIBA_INU": "https://ipfs.io/ipfs/QmdryoExpgEQQQgJPoruwGJyZmz6SqV4FRTX1i73CT3iXn?filename=1-SHIBA_INU.json",
    "ST_BERNARD": "https://ipfs.io/ipfs/QmbBnUjyHHN7Ytq9xDsYF9sucZdDJLRkWz7vnZfrjMXMxs?filename=2-ST_BERNARD.json",
}
BREED_NAMES = ["PUG", "SHIBA_INU", "ST_BERNARD"]


def get_account(index=None, id=None, use_local=False):
    """
    To get an active account.
    """
    if index is not None:
        # automatically use stored account via indexing
        return accounts[index]
    if id is not None:
        # get from the stored account in brownie
        return accounts.load(id)

    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENV
        or network.show_active() in FORKED_LOCAL_ENV
    ):
        if use_local:  # use brownie LocalAccount!
            local = accounts.add(config["wallets"]["key_playground"])
            if local.balance() == 0:  # fund account if empty
                accounts[0].transfer(local, "10 ether")
            print(
                f"Using permit method - Local balance: "
                f"{Web3.fromWei(local.balance(), 'ether')} ETH"
            )
            return local
        else:
            return accounts[0]
    return accounts.add(config["wallets"]["key_playground"])


def get_contract(contract_name: str):
    """
    This function will grab the contract addresses from the brownie config if defined,
    otherwise, it will deploy a mock version of that contract instead!

    Parameters
    ----------
    contract_name: `str`
        The contract name to grab.

    Returns
    -------
    brownie.network.contract.ProjectContract: The most recently deployed version of
    this contract.
    """
    network_id = network.show_active()
    contract_type = CONTRACT_TO_MOCK[contract_name]
    if network_id in LOCAL_BLOCKCHAIN_ENV:  # use Mock on local!
        if len(contract_type) <= 0:  # contract not ready! Deploying a fresh mock
            deploy_mocks(mock_name=contract_name)
        contract = contract_type[-1]  # get the latest deployed mock
    else:
        contract_address = config["networks"][network_id][contract_name]
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )
    return contract


def deploy_mocks(mock_name: Optional[str] = None):
    """
    To deploy the mock contract(s).

    Parameters
    ----------
    mock_name: `Optional[str]`
        The mock contract name to deploy, if None, deploy all available mocks!
    """
    account = get_account()
    if mock_name is None or mock_name == "eth_usd_price_feed":
        print("Deploying the mock Price Feed ... ")
        MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": account})
    if mock_name is None or mock_name == "vrf_coordinator":
        print(f"Deploying the mock VRF Coordinator V2 ... ")
        VRFCoordinatorV2Mock.deploy(BASE_FEE, GAS_PRICE_LINK, {"from": account})
    if mock_name is None or mock_name == "link_token":
        print(f"Deploying the mock LINK Token ... ")
        LinkToken.deploy({"from": account})


def get_breed(breed_id: int):
    """
    To get the breed name from the breed ID

    Parameters
    ----------
    breed_id: `int`
        The breed ID (0 for pug, 1 for shiba inu and 2 for st bernard).
    """
    return BREED_NAMES[breed_id]
