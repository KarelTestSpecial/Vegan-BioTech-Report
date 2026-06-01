import os
import time
import frontmatter
from google import genai
import requests
from urllib.parse import quote

# --- CONFIGURATIE ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CONTENT_DIR = "content" # Zoekt in alle submappen (newsletters, longreads, etc.)
STATIC_IMG_DIR = "static/images"

def get_ai_response(client, model_id, prompt):
    """Genereert content en haalt op een robuuste manier de tekst op (Gemini 3.0 ready)."""
    response = client.models.generate_content(model=model_id, contents=prompt)
    if hasattr(response, 'candidates') and response.candidates:
        parts = response.candidates[0].content.parts
        text_part = next((p.text for p in parts if p.text), None)
        if text_part:
            return text_part
    return response.text

# Installeer Google Client
model_client = None
if GEMINI_API_KEY:
    model_client = genai.Client(api_key=GEMINI_API_KEY)

# Zorg dat de map bestaat
os.makedirs(STATIC_IMG_DIR, exist_ok=True)

def get_latest_flash_model(client):
    """Haalt de nieuwste beschikbare flash model naam op via de SDK."""
    try:
        models = client.models.list()
        # Filter op 'flash', vermijd 'preview' en 'image' (die voor beeldgeneratie is)
        flash_models = [m.name for m in models if 'flash' in m.name.lower() and 'preview' not in m.name.lower() and 'image' not in m.name.lower()]
        
        if flash_models:
            # Sorteer om de 'hoogste' versie te krijgen (bijv. 3 > 2.5 > 2.0)
            flash_models.sort(reverse=True)
            latest = flash_models[0]
            # Verwijder 'models/' prefix als die er staat
            if latest.startswith('models/'):
                latest = latest.replace('models/', '')
            print(f"ℹ️ Live Gemini model geselecteerd voor afbeeldingen: {latest}")
            return latest
    except Exception as e:
        print(f"⚠️ Kon Gemini modellen niet live ophalen voor afbeeldingen: {e}")
    return 'gemini-2.5-flash' # Stabiele fallback

def generate_image_prompt(article_text):
    """
    Vraagt Gemini (tekst) om een prompt te schrijven.
    """
    if not model_client:
        return "Futuristic biotechnology laboratory, cinematic lighting, 8k"

    # We halen het nieuwste model live op
    model_id = get_latest_flash_model(model_client)
    
    prompt = f"""
    You are an AI art director. Read this summary and write ONE single, descriptive English prompt 
    to generate a cover image.
    
    Style: Photorealistic, cinematic lighting, 8k, highly detailed, positive, optimistic, clean, innovative, hopeful, cyberpunk or futuristic biotechnology elements.
    Subject: {article_text[:1000]}
    
    Return ONLY the prompt.
    """
    try:
        return get_ai_response(model_client, model_id, prompt).strip()
    except Exception as e:
        print(f"⚠️ Text Gen Error: {e}")
        return "Bright, optimistic futuristic biotechnology laboratory with vibrant green plants and clean, innovative technology, cinematic lighting, 8k, photorealistic"

def create_image_pollinations(prompt, filename):
    """
    Gebruikt Pollinations.ai met een incrementele backoff-strategie.
    """
    print(f"🎨 Pollinations generating: {filename}...")
    
    safe_prompt = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&width=1280&height=720&nologo=true"
    
    timeouts = [45, 90, 135]
    for i, timeout in enumerate(timeouts):
        attempt = i + 1
        print(f"    - Attempt {attempt}/{len(timeouts)} with timeout {timeout}s...")
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                path = os.path.join(STATIC_IMG_DIR, filename)
                with open(path, 'wb') as f:
                    f.write(response.content)
                print(f"✅ Saved to {path}")
                return path
            else:
                print(f"    - Pollinations Error (Attempt {attempt}): {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"    - Download Error (Attempt {attempt}): {e}")

        if attempt < len(timeouts):
            print("    - Waiting 15s before next attempt...")
            time.sleep(15)

    print(f"❌ Failed to download image for {filename} after {len(timeouts)} attempts.")
    return None

def process_files():
    print("🚀 Starting Image Generation Pipeline...")
    
    for root, dirs, files in os.walk(CONTENT_DIR):
        for file in files:
            if file.endswith(".md") and not file.startswith("_"):
                file_path = os.path.join(root, file)
                try:
                    post = frontmatter.load(file_path)
                    
                    # AANGEPAST: Checkt specifiek op featured_image voor Ananke thema
                    if not post.get('featured_image') and not post.get('image'):
                        print(f"Processing {file}...")
                        
                        image_prompt = generate_image_prompt(post.content)
                        img_filename = file.replace(".md", ".png")
                        
                        if create_image_pollinations(image_prompt, img_filename):
                            # AANGEPAST: Schrijft naar featured_image
                            post['featured_image'] = f"/images/{img_filename}"
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                frontmatter.dump(post, f)
                            
                            print("💤 Waiting 30s to respect Rate Limits...")
                            time.sleep(30)
                            
                except Exception as e:
                    print(f"Skipping {file}: {e}")

if __name__ == "__main__":
    process_files()
