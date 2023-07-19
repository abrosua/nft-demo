import pytest, random
from brownie import network
from web3 import Web3
from scripts.multi_collectible.deploy_and_mint import deploy, mint, pin_metadata_to_ipfs
from scripts.utils import BREED_NAMES, LOCAL_BLOCKCHAIN_ENV, get_account


def test_deploy_multi_collectible():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("unit testing only for local blockchain!")
    collectible = deploy()
    # Act
    ipfs_cid = pin_metadata_to_ipfs()
    # Assert
    for i in range(len(BREED_NAMES)):
        token_uri_ref = f"ipfs://{ipfs_cid}/{i}.json"
        token_uri_deployed = collectible.uri(int(i), {"from": get_account()})
        print(f"Token URI #{i}: {token_uri_deployed}")
        assert token_uri_ref == token_uri_deployed
    print(f"Passed the test!")


def test_get_entrance_fee():
    """
    To test the entrance fee calculation and the minimum fee/price for each token
    """
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("unit testing only for local blockchain!")
    collectible = deploy()
    # Act #1
    entrance_fee = collectible.getEntranceFee()
    expected_fee_usd = 20  # USD
    # Assert #1
    print(f"Minimum entrance fee at {entrance_fee} Wei")
    assert entrance_fee == Web3.toWei(expected_fee_usd / 2000, "ether")
    # Act & Assert #2
    for i, min_price_usd in enumerate([5, 10, 20]):
        min_price = collectible.getTokenMinimumPrice(i)
        print(f"Token #{i} minimum price at {min_price} Wei")
        assert min_price == Web3.toWei(min_price_usd / 2000, "ether")
    print(f"Passed the test!")


def test_mint_multi_collectible():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("unit testing only for local blockchain!")
    account = get_account()
    number_of_breeds = len(BREED_NAMES)
    random_number = random.randint(100, 100000)  # random number from 100 to 100,000
    # Act
    multi_collectible = deploy()
    payable_value = multi_collectible.getEntranceFee()
    mint(
        collectible=multi_collectible,
        account=account,
        rng=random_number,
        pay_wei=payable_value,
    )
    expected_breed = random_number % number_of_breeds
    expected_amount = (number_of_breeds + 1) / (2**expected_breed)
    # Assert
    user_balance = multi_collectible.balanceOf(account, expected_breed)
    breed_name = BREED_NAMES[expected_breed]
    print(f"User {account} successfully minted {user_balance} of {breed_name}")
    assert user_balance == expected_amount
    print(f"Passed the test!")
