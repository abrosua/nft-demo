import pytest
from brownie import network
from scripts.advanced_collectible.deploy_and_create import (
    deploy,
    create_collectible,
)
from scripts.utils import BREED_NAMES, LOCAL_BLOCKCHAIN_ENV, get_account


def test_can_create_advanced_collectible():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("unit testing only for local blockchain!")
    account = get_account()
    number_of_breeds = len(BREED_NAMES)
    random_number = 777
    # Act
    advanced_collectible = deploy()
    _, token_uri = create_collectible(
        collectible=advanced_collectible,
        account=account,
        rng=random_number,
        is_set_uri=True,
    )
    # Assert
    assert advanced_collectible.tokenCounter() == 1
    assert advanced_collectible.ownerOf(0) == account
    assert advanced_collectible.tokenIdToBreed(0) == random_number % number_of_breeds
    assert advanced_collectible.tokenURI(0) == token_uri
