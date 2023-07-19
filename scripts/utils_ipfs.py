import os
import json
import requests
from pathlib import Path
from typing import List


def get_all_files(directory: str) -> List[str]:
    """get a list of absolute paths to every file located in the directory"""
    filepaths = []
    for root, _, files_ in os.walk(os.path.abspath(directory)):
        for file in files_:
            filepaths.append(os.path.join(root, file))
    return filepaths


def add_to_ipfs(filepath: str) -> str:
    """
    Handle adding file to IPFS with different IPFS network services.

    Parameters
    ----------
    filepath: `str`
        The path to file/directory that would be pinned.

    Returns
    -------
    `str`: The pinned CID.
    """
    ipfs_network = os.getenv("IPFS_NETWORK", "local").lower()
    if not Path(filepath).exists():
        raise ValueError(f"The input path does not exist! Input: '{filepath}'")
    post_args = {}
    # handle different IPFS network
    if ipfs_network == "local":
        post_args["url"] = "http://127.0.0.1:5001/api/v0/add"
    elif ipfs_network == "infura":
        post_args["url"] = "https://ipfs.infura.io:5001/api/v0/add"
        post_args["auth"] = (
            os.getenv("IPFS_INFURA_KEY"),
            os.getenv("IPFS_INFURA_SECRET"),
        )
    elif ipfs_network == "pinata":
        return _add_file_to_ipfs_pinata(filepath=filepath)
    else:
        raise ValueError(f"Unknown IPFS network option: '{ipfs_network}'!")

    # handle the input file(s) and params
    post_args["params"] = {"cid-version": 1}
    if os.path.isdir(filepath):
        if filepath.endswith("/"):
            filepath = filepath[:-1]
        all_files = get_all_files(filepath)
        post_args["files"] = [
            ("file", (os.path.basename(f), open(f, "rb"))) for f in all_files
        ]
        post_args["params"].update({"wrap-with-directory": True, "pin": True})
    else:
        filename = os.path.basename(filepath)
        post_args["files"] = [("file", (filename, open(filepath, "rb")))]

    # HTTP post request to add the file(s) here
    response = requests.post(**post_args)
    if response.status_code != 200:
        raise ValueError(f"Failed POST - {response.status_code} - {response.text}")
    # print(f"Response [200]: {response.text}")
    pinned_list = response.text.rstrip().split("\n")
    pinned_cid = json.loads(pinned_list[-1])["Hash"]
    return pinned_cid


def _add_file_to_ipfs_pinata(filepath: str):
    """
    Manually handle pinning to IPFS HTTP for Pinata

    Parameters
    ----------
    filepath: `str`
        The path to file/directory that would be pinned.

    Returns
    -------
    `str`: The pinned CID.
    """
    pinata_args = {}
    # add the remaining args here
    pinata_args["url"] = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    pinata_args["headers"] = {"Authorization": f"Bearer {os.getenv('IPFS_PINATA_JWT')}"}
    pinata_args["data"] = {
        "pinataOptions": json.dumps({"cidVersion": 1, "wrapWithDirectory": False})
    }
    # handle the file uploading
    if os.path.isdir(filepath):
        if filepath.endswith("/"):
            filepath = filepath[:-1]
        maindir = os.path.basename(filepath)  # get the lowest directory
        all_files = get_all_files(filepath)
        pinata_args["files"] = [
            ("file", (f"{maindir}/{os.path.basename(f)}", open(f, "rb")))
            for f in all_files
        ]
        pinata_args["data"]["pinataMetadata"] = json.dumps({"name": maindir})
    else:
        filename = os.path.basename(filepath)
        pinata_args["files"] = [("file", (filename, open(filepath, "rb")))]

    # HTTP POST request to pin the file(s) to Pinata
    response = requests.post(**pinata_args)
    if response.status_code != 200:
        raise ValueError(f"Failed POST - {response.status_code} - {response.text}")
    pinned_cid = response.json()["IpfsHash"]
    return pinned_cid


def main():
    file_to_add = "./test.txt"
    # file_to_add = "./img"
    # file_to_add = "./img/pug.png"
    # file_to_add = "./metadata/erc721/sepolia/0-SHIBA_INU.json"
    cid = add_to_ipfs(filepath=file_to_add)
    print(f"Pinned CID: {cid}")
