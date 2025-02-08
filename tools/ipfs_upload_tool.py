import os
import io
import mimetypes
import requests
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from a .env file, if available
load_dotenv()

class UploadImageToPinataInput(BaseModel):
    image_url: str = Field(
        ...,
        description="The URL of the image to upload to IPFS via Pinata using JWT authentication",
        example="https://pocketcast.cloud/og.png"
    )
    save_locally: bool = Field(
        default=True,
        description="Whether to save the downloaded image locally"
    )

def create_pinata_upload_tool(image_url: str, save_locally: bool = True) -> dict:
    """
    Downloads an image from a URL and uploads it to IPFS via Pinata using JWT authentication.
    The JWT token is read from the environment variable 'PINATA_JWT'.

    Args:
        image_url (str): The URL of the image to download.
        save_locally (bool): Whether to save the downloaded image locally.

    Returns:
        dict: A response containing the IPFS hash, Pinata gateway URL, and local file path if saved.
    """
    try:
        # Retrieve the JWT token from the environment variable
        jwt_token = os.environ.get("PINATA_JWT")
        if not jwt_token:
            raise Exception("Missing Pinata JWT token in environment variables.")

        # Download the image from the provided URL
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        image_data = response.content

        # Optionally save the downloaded image locally
        local_path = None
        if save_locally:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            local_path = f"downloaded_image_{timestamp}.png"
            with open(local_path, 'wb') as f:
                f.write(image_data)

        # Prepare the file for uploading
        file_name = os.path.basename(image_url) or "file.png"
        mime_type, _ = mimetypes.guess_type(file_name)
        if mime_type is None:
            mime_type = "application/octet-stream"
        files = {
            "file": (file_name, io.BytesIO(image_data), mime_type)
        }

        # Set the Authorization header with the JWT token
        headers = {
            "Authorization": f"Bearer {jwt_token}"
        }

        # Upload the file to Pinata
        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        pinata_response = requests.post(url, files=files, headers=headers)
        pinata_response.raise_for_status()  # Raise an error if the upload fails
        pinata_data = pinata_response.json()

        ipfs_hash = pinata_data.get("IpfsHash")
        ipfs_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}" if ipfs_hash else None

        # Return the response in a structured format
        return {
            'type': 'image',
            'content': f"Image uploaded to IPFS via Pinata using JWT from URL: {image_url}",
            'ipfs_hash': ipfs_hash,
            'ipfs_url': ipfs_url,
            'local_path': local_path
        }

    except Exception as e:
        return {
            'type': 'error',
            'content': f"Failed to upload image to Pinata: {str(e)}"
        }

UPLOAD_IMAGE_TO_PINATA_PROMPT = """
Upload an image stored at the provided URL onto IPFS using Pinata with JWT-based authentication.
Returns the IPFS hash (CID), the Pinata gateway URL, and optionally saves the image locally.
Example:
Input: {
    "image_url": "https://pocketcast.cloud/og.png",
    "save_locally": true
}
"""

# Example usage:
# if __name__ == "__main__":
#     # Example input
#     input_data = UploadImageToPinataInput(
#         image_url="https://pocketcast.cloud/og.png",
#         save_locally=True
#     )
#     result = create_pinata_upload_tool(
#         image_url=input_data.image_url,
#         save_locally=input_data.save_locally
#     )
#     print(result)



