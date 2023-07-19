import json
from pathlib import Path
from brownie import AdvancedCollectible, network
from metadata.sample_metadata import metadata_template_puppies
from scripts.utils import get_breed
from scripts.utils_ipfs import add_to_ipfs


def generate_metadata(token_id: int) -> str:
    """
    To generate the token metadata

    Parameters
    ----------
    token_id: `int`
        The specific token ID.

    Returns
    -------
    `str`: The token metadata filepath.
    """
    advanced_collectible = AdvancedCollectible[-1]
    breed = get_breed(advanced_collectible.tokenIdToBreed(token_id))
    breed_name = " ".join(breed.split("_")).title()
    # generate filenames
    metadata_filepath = (
        f"./metadata/erc721/{network.show_active()}/{token_id}-{breed}.json"
    )
    image_filepath = f"./img/{breed.lower().replace('_', '-')}.png"

    # check if metadata already exists
    metadata = metadata_template_puppies
    if Path(metadata_filepath).exists():
        print(f"Metadata already exists: '{metadata_filepath}'!")
        return metadata_filepath
    # create the image metadata here
    print(f"Creating metadata file: '{metadata_filepath}' ...")
    metadata["name"] = breed_name
    metadata["description"] = f"An adorable {breed_name} pup!"
    metadata["image"] = f"ipfs://{add_to_ipfs(filepath=image_filepath)}"
    # store the metadata
    with open(metadata_filepath, "w") as f:
        json.dump(metadata, f)
    return metadata_filepath


def main():
    generate_metadata(token_id=0)
