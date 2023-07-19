import os
import requests
from pathlib import Path
from scripts.utils_ipfs import add_to_ipfs, get_all_files


def test_can_add_file_to_ipfs():
    # Arrange
    test_file = "./test.txt"
    test_read = Path(test_file).open("r").read()
    # Act
    test_cid = add_to_ipfs(test_file)
    print(f"Test CID: {test_cid}")
    ipfs_cat = requests.post(
        "http://127.0.0.1:5001/api/v0/cat", params={"arg": test_cid}
    )
    # Assert
    assert test_read == ipfs_cat.text
    print(f"Passed the test!")


def test_can_add_directory_to_ipfs():
    # Arrange
    test_directory = "./img"
    test_files = get_all_files(directory=test_directory)
    # Act
    test_folder_cid = add_to_ipfs(test_directory)
    print(f"Test CID: {test_folder_cid}")
    # Assert
    for i, f in enumerate(test_files):
        fname = os.path.basename(f)
        ipfs_cat_img = requests.post(
            "http://127.0.0.1:5001/api/v0/cat",
            params={"arg": f"{test_folder_cid}/{fname}"},
        )
        ipfs_read = ipfs_cat_img.content
        file_read = Path(f).open("rb").read()
        assert file_read == ipfs_read
        print(f"Successfully pinned image #{i+1}: {fname}")
    print(f"Passed the test!")
