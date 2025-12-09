import os
import time
import frontmatter
import google.generativeai as genai
from PIL import Image
import io

# CONFIGURATIE
# We gebruiken de bestaande secret, gemapped naar deze env var
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") 
CONTENT_DIR = "content" # Aangepast naar root content dir om recursief te zoeken
STATIC_IMG_DIR = "static/images" # Aangepast naar bestaande structuur

# Setup Google GenAI
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not found in environment.")

# We gebruiken het specifieke "Nano Banana" model (Gemini 2.5 Flash Image)
# In de API heet dit 'gemini-2.5-flash-image' maar gedraagt zich als image model
MODEL_NAME = 'gemini-2.5-flash-image'

print(f"GenAI Library Version: {genai.__version__}")

os.makedirs(STATIC_IMG_DIR, exist_ok=True)

def generate_image_prompt(article_text): 
    """Vraagt Gemini (tekst) om een prompt te schrijven voor Gemini (beeld).""" 
    # We gebruiken Flash ook voor de tekst-analyse (is razendsnel) 
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
    Je bent een expert in AI art prompts. Lees deze blogpost en schrijf EEN enkele, 
    beschrijvende prompt (in het Engels) om een cover image te genereren.
    Stijl: Photorealistic, cinematic lighting, 8k, highly detailed.
    Onderwerp: {article_text[:1500]}
    Geef ALLEEN de prompt terug. Geen 'Here is the prompt:' etc.
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Text Gen Error: {e}")
        return "A futuristic biotechnology laboratory with green plants, cinematic lighting, 8k"

def create_image(prompt, filename): 
    """Roept Gemini 2.5 Flash Image (Nano Banana) aan.""" 
    print(f"🍌 Nano Banana generating: {filename}...")

    try:
        # We initialiseren het ImageGenerationModel met de specifieke ID
        # Note: De SDK support voor specifieke nieuwe modellen kan varieren, 
        # maar 'imagen-3.0-generate-001' is vaak de stabiele fallback. 
        # We proberen eerst de opgegeven specifieke modelnaam.
        try:
             imagen_model = genai.ImageGenerationModel(MODEL_NAME)
             response = imagen_model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="16:9",
                safety_filter_level="block_only_high",
                person_generation="allow_adult",
            )
        except Exception:
             # Fallback naar standaard Imagen model als 2.5 flash image niet direct beschikbaar is via deze call
             imagen_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
             response = imagen_model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="16:9",
            )

        image = response.images[0]
        
        path = os.path.join(STATIC_IMG_DIR, filename)
        image.save(path)
        print(f"✅ Saved to {path}")
        return f"/images/{filename}" # Return relative path for Hugo

    except Exception as e:
        print(f"❌ Nano Banana Error for {filename}: {e}")
        return None

def process_files(): 
    for root, dirs, files in os.walk(CONTENT_DIR):
        for file in files: 
            if file.endswith(".md") and "_index" not in file:
                file_path = os.path.join(root, file)
                try:
                    post = frontmatter.load(file_path)

                    if not post.get('featured_image') and not post.get('image') and not post.get('cover'):
                        print(f"Processing {file}...")
                        image_prompt = generate_image_prompt(post.content)
                        
                        # Safe filename
                        safe_name = file.replace(".md", "").replace(" ", "_")
                        img_filename = f"{safe_name}.png"
                        
                        image_rel_path = create_image(image_prompt, img_filename)
                        
                        if image_rel_path:
                             # Hugo path fix - using 'featured_image' as standard
                            post['featured_image'] = image_rel_path
                            
                            # Write back
                            with open(file_path, 'wb') as f:
                                frontmatter.dump(post, f)
                            
                            # Even pauze voor de API rate limits
                            time.sleep(4)
                except Exception as e:
                    print(f"Error processing file {file}: {e}")

if __name__ == "__main__":
    process_files()
