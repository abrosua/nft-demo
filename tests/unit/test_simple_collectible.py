import pytest
from brownie import network
from scripts.simple_collectible.deploy_and_create import deploy_and_create
from scripts.utils import LOCAL_BLOCKCHAIN_ENV, get_account


def test_can_create_simple_collectible():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("unit testing only for local blockchain!")
    # Act
    simple_collectible = deploy_and_create()
    # Assert
    assert simple_collectible.tokenCounter() == 1
    assert simple_collectible.ownerOf(0) == get_account()
