import pytest
from brownie import network
from scripts.advanced_collectible.deploy_and_create import deploy_and_create
from scripts.utils import LOCAL_BLOCKCHAIN_ENV, get_account


def test_can_create_advanced_collectible_integration():
    # Arrange
    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        pytest.skip("integration testing only for PERSISTENT chain!")
    # Act
    advanced_collectible = deploy_and_create()
    # Assert
    assert advanced_collectible.tokenCounter() == 1
    assert advanced_collectible.ownerOf(0) == get_account()
