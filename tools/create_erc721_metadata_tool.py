
import os
import requests
import json
import io
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from a .env file, if available
load_dotenv()

class UploadERC721MetadataInput(BaseModel):
    """
    Pydantic model for specifying the ERC-721 metadata parameters.
    """
    name: str = Field(
        ...,
        description="Name of the NFT",
        example="My Awesome NFT"
    )
    description: str = Field(
        ...,
        description="Description of the NFT",
        example="This is an awesome NFT with great utility."
    )
    image_ipfs_url: str = Field(
        ...,
        description="IPFS URI or gateway URL of the NFT image",
        example="ipfs://<CID>"
    )
    attributes: List[dict] = Field(
        default_factory=list,
        description="List of attributes (trait_type and value) for the NFT"
    )

def create_erc721_metadata(
    name: str,
    description: str,
    image_ipfs_url: str,
    attributes: Optional[List[dict]] = None
) -> dict:
    """
    Creates and uploads a standard ERC-721 metadata JSON file to IPFS via Pinata (JWT-based).
    The metadata will be wrapped in a directory so that it can be accessed at /0.
    """
    try:
        # Retrieve the JWT token from the environment variable
        jwt_token = os.environ.get("PINATA_JWT")
        if not jwt_token:
            raise Exception("Missing 'PINATA_JWT' token in environment variables.")

        # Validate and structure inputs via Pydantic
        metadata_input = UploadERC721MetadataInput(
            name=name,
            description=description,
            image_ipfs_url=image_ipfs_url,
            attributes=attributes or []
        )

        # Construct the metadata dict according to ERC-721 standard
        metadata = {
            "name": metadata_input.name,
            "description": metadata_input.description,
            "image": metadata_input.image_ipfs_url,
            "attributes": metadata_input.attributes
        }

        # Convert metadata JSON into a bytes stream (simulate a file)
        json_str = json.dumps(metadata)
        json_bytes = io.BytesIO(json_str.encode("utf-8"))

        # Build the multipart form-data parts:
        # - "file": the actual file; name it "0" so that it becomes accessible via /0
        # - "pinataMetadata": additional metadata about the upload
        # - "pinataOptions": options for the upload (set cidVersion to 1 and wrapWithDirectory to True)
        files = {
            "file": ("0", json_bytes, "application/json"),  # File name "0" is crucial
            "pinataMetadata": (None, json.dumps({
                "name": f"{metadata_input.name} Metadata"
            }), "application/json"),
            "pinataOptions": (None, json.dumps({
                "cidVersion": 1,
                "wrapWithDirectory": True,
            }), "application/json")
        }

        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {
            # Do not manually set Content-Type; let requests handle the multipart boundary.
            "Authorization": f"Bearer {jwt_token}"
        }

        # Upload the file and related metadata/options to Pinata
        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()

        # Parse Pinata response
        pinata_data = response.json()
        ipfs_hash = pinata_data.get("IpfsHash")
        ipfs_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}/0" if ipfs_hash else None

        return {
            "type": "ERC721-metadata",
            "content": "ERC-721 metadata JSON successfully uploaded to IPFS via Pinata",
            "ipfs_hash": ipfs_hash,
            "ipfs_url": ipfs_url,
            "metadata": metadata
        }

    except Exception as e:
        return {
            "type": "error",
            "content": f"Failed to upload ERC-721 metadata to Pinata: {str(e)}"
        }


UPLOAD_ERC721_METADATA_PROMPT = """
Generate an ERC-721 metadata JSON (name, description, image, attributes, etc.) 
and upload that metadata file to IPFS via Pinata using JWT-based authentication.
Returns the IPFS hash (CID), a gateway URL, and includes the metadata uploaded.

Example:
Input: {
    "name": "My Awesome NFT",
    "description": "This is an awesome NFT with great utility.",
    "image_ipfs_url": "ipfs://QmHashOfTheImageOrUseGatewayUrl",
    "attributes": [
        {"trait_type": "Level", "value": 1},
        {"trait_type": "Rarity", "value": "Rare"}
    ]
}
"""

# Example usage (uncomment to test):
if __name__ == "__main__":
    result = create_erc721_metadata(
        name="My Awesome NFT",
        description="This is an awesome NFT with great utility.",
        image_ipfs_url="ipfs://QmHashOfTheImageOrUseGatewayUrl",
        attributes=[
            {"trait_type": "Level", "value": 1},
            {"trait_type": "Rarity", "value": "Rare"}
        ]
    )
    print(result)
