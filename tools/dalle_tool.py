import os
from openai import OpenAI
import requests
from datetime import datetime
from pydantic import BaseModel, Field

class GenerateImageInput(BaseModel):
    prompt: str = Field(
        ...,
        description="The text prompt to generate an image from",
        example="A white siamese cat in cyberpunk style"
    )
    save_locally: bool = Field(
        default=True,
        description="Whether to save the generated image locally"
    )

GENERATE_IMAGE_PROMPT = """
Generate an image using DALLE-3 based on the provided prompt.
Returns the image URL and optionally saves it locally.

Example:
Input: {
    "prompt": "A white siamese cat in cyberpunk style",
    "save_locally": true
}
"""

def create_dalle_tool(prompt: str, save_locally: bool = True) -> dict:
    """Generate images based on user input using DALLE-3"""
    client = OpenAI()
    
    try:
        # Generate image
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        
        result = {'url': image_url}
        
        if save_locally:
            # Download and save image
            img_data = requests.get(image_url).content
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dalle_image_{timestamp}.png"
            
            with open(filename, 'wb') as f:
                f.write(img_data)
            result['local_path'] = filename
        
        # Return in the format expected by the frontend
        return {
            'type': 'image',
            'content': f'Here is your generated image for: "{prompt}"',
            'image_url': image_url
        }
        
    except Exception as e:
        return {
            'type': 'error',
            'content': f'Failed to generate image: {str(e)}'
        }