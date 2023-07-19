import os
import json
from pathlib import Path
from brownie import network
from metadata.sample_metadata import metadata_template_puppies_erc1155
from scripts.utils import BREED_NAMES
from scripts.utils_ipfs import add_to_ipfs, get_all_files


def generate_metadata() -> str:
    """
    To generate the tokens metadata for ERC1155 contract.

    Returns
    -------
    `str`: The token metadata filepath.
    """
    metadata_directory = f"./metadata/erc1155/{network.show_active()}"
    for i, breed in enumerate(BREED_NAMES):
        breed_name = " ".join(breed.split("_")).title()
        # generate filenames
        metadata_filepath = os.path.join(metadata_directory, f"{i}.json")
        image_filepath = f"./img/{breed.lower().replace('_', '-')}.png"

        # check if metadata already exists
        metadata = metadata_template_puppies_erc1155
        if Path(metadata_filepath).exists():
            print(f"Metadata already exists: '{metadata_filepath}'!")
            continue
        # create the image metadata here
        print(f"Creating metadata file: '{metadata_filepath}' ...")
        metadata["name"] = breed_name
        metadata["description"] = f"An adorable {breed_name} pup!"
        metadata["image"] = f"ipfs://{add_to_ipfs(filepath=image_filepath)}"
        metadata["attributes"][1]["value"] = int(i + 1)
        # store the metadata
        with open(metadata_filepath, "w") as f:
            json.dump(metadata, f)
    # validate the generated metadata file(s)
    assert len(get_all_files(metadata_directory)) == len(BREED_NAMES)
    return metadata_directory


def pin_metadata_to_ipfs() -> str:
    """
    To pin the whole metadata to IPFS, wrapped in directory.

    Returns
    -------
    `str`: The IPFS CID for the pinned directory.
    """
    directory = generate_metadata()
    return add_to_ipfs(filepath=directory)


def main():
    print(f"Pinned directory to IPFS at: ipfs://{pin_metadata_to_ipfs()}")
