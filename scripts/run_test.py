from tests.unit.test_advanced_collectible import test_can_create_advanced_collectible
from tests.unit.test_multi_collectible import (
    test_deploy_multi_collectible,
    test_mint_multi_collectible,
    test_get_entrance_fee,
)
from tests.unit.test_ipfs import test_can_add_directory_to_ipfs


def main():
    # test_can_create_advanced_collectible()
    # test_can_add_directory_to_ipfs()
    # test_deploy_multi_collectible()
    # test_get_entrance_fee()
    test_mint_multi_collectible()
