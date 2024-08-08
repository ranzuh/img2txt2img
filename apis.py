import os
import requests
import io
from PIL import Image
import base64


hf_api_key = os.getenv("API_KEY")
sai_api_key = os.getenv("STABILITY_API_KEY")

def generate_caption(img_fname):
    if hf_api_key is None:
        raise Exception("Missing HuggingFace API key.")
    
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    headers = {"Authorization": f"Bearer {hf_api_key}"}

    with open(img_fname, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)

    output = response.json()
    return output[0]["generated_text"]

def generate_image_SDXL_free(prompt):
    if hf_api_key is None:
        raise Exception("Missing HuggingFace API key.")
    
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {hf_api_key}"}
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)
    img_bytes = response.content
    return Image.open(io.BytesIO(img_bytes))

def generate_image_SDXL_paid(prompt):
    if sai_api_key is None:
        raise Exception("Missing Stability API key.")

    response = requests.post(
        "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
        headers={"Authorization": f"Bearer {sai_api_key}"},
        json={
            "text_prompts": [{"text": prompt}],
            "cfg_scale": 7,
            "width": 1024,
            "height": 1024, #1344x768
            "samples": 1,
            "steps": 40,
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()
    return Image.open(io.BytesIO(base64.b64decode(data["artifacts"][0]["base64"])))
