from fasthtml.common import *
from PIL import Image
from io import BytesIO
from apis import generate_caption, generate_image_SDXL_free, generate_image_SDXL_paid
import os

paid = False
generate_image = generate_image_SDXL_paid if paid else generate_image_SDXL_free

os.makedirs("uploads", exist_ok=True)
os.makedirs("gens", exist_ok=True)

images = os.listdir("uploads")
gen_images = os.listdir("gens")

css = Style(
"""
body { padding: 2rem; }
.container { max-width: 800px; margin: 0 auto; }
img { margin-bottom: 1rem; }
""")

aria_busy_args = dict(hx_on__before_request="this.setAttribute('aria-busy', 'true')",
        hx_on__after_request="this.setAttribute('aria-busy', 'false')")

app, rt = fast_app(hdrs=[picolink, css])

@app.get("/")
def home():
    return Titled("Image generation App", ImageUpload(), Div(id="captionsection"), Div(id="gensection"), id="home")

def ImageUpload(): 
    return Article(
        H2('Step 1: Upload an Image'),
        Form(hx_encoding='multipart/form-data')(
            Input(type='file', id='imageup', accept='image/*', hx_post="/upload", hx_trigger="change", hx_target="#preview")
        ),
        Div(id="preview")
    )

def GeneratedCaption(caption):
    return Article(
        H2('Step 2: Generated Caption'),
        P(caption),
        Input(type="hidden", id="captiontext", value=caption),
        Button('Generate New Image', hx_post="/genimage", hx_target="#gensection", hx_include="#captiontext", **aria_busy_args),
    )

def GeneratedImage(fname):
    return Article(
        H2('Step 3: Generated Image'),
        Img(src=fname, alt='Generated image'),
        Button('Start Over', hx_get="/", hx_target="#home", hx_swap="outerHTML"),
    )

@app.post("/upload")
async def upload(imageup: UploadFile):
    bytes = await imageup.read()
    img = Image.open(BytesIO(bytes))
    fname = f"uploads/{len(images)+1}.jpg"
    images.append(fname)
    img.save(fname)
    return Figure(Img(id="preview-image", src=fname, alt="preview image")), Button(
        "Generate Caption", hx_get=f"/gencaption/{len(images)}", hx_target="#captionsection", **aria_busy_args)

@threaded
@app.get("/gencaption/{id}")
def get_caption_gen(id: str):
    caption = generate_caption(f"uploads/{id}.jpg")
    return GeneratedCaption(caption)

@threaded
@app.post("/genimage")
def get_image_gen(captiontext: str):
    gen_image = generate_image(captiontext)
    fname = f"gens/{len(gen_images)+1}.jpg"
    gen_images.append(fname)
    gen_image.save(fname)
    return GeneratedImage(fname)


serve()