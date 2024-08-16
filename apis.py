import os
import requests
import io
from PIL import Image
import base64
import requests


def generate_caption_free(img_fname):
    hf_api_key = os.getenv("API_KEY")
    if hf_api_key is None:
        raise Exception("Missing HuggingFace API key.")
    
    API_URL = "https://api-inference.huggingface.co/models/Salesforce/blip-image-captioning-large"
    headers = {"Authorization": f"Bearer {hf_api_key}"}

    with open(img_fname, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)

    output = response.json()
    print(output)
    return output[0]["generated_text"]

def generate_image_SDXL_free(prompt):
    hf_api_key = os.getenv("API_KEY")
    if hf_api_key is None:
        raise Exception("Missing HuggingFace API key.")
    
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {hf_api_key}"}
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)
    img_bytes = response.content
    return Image.open(io.BytesIO(img_bytes))

def generate_image_SDXL_paid(prompt):
    sai_api_key = os.getenv("STABILITY_API_KEY")
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

def openai_caption(img_fname):
    # OpenAI API Key
    oai_api_key = os.getenv("OPENAI_API_KEY")

    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')


    # Getting the base64 string
    base64_image = encode_image(img_fname)

    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {oai_api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": "What's in this image?"
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": "low"
                }
                }
            ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    return response.json()["choices"][0]["message"]["content"]
