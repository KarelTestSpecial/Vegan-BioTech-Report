import os
import time
import frontmatter
import google.generativeai as genai
import requests
from urllib.parse import quote

# --- CONFIGURATIE ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CONTENT_DIR = "content" # Zoekt in alle submappen (newsletters, longreads, etc.)
STATIC_IMG_DIR = "static/images"

# Installeer Google
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Zorg dat de map bestaat
os.makedirs(STATIC_IMG_DIR, exist_ok=True)

def generate_image_prompt(article_text):
    """
    Vraagt Gemini (tekst) om een prompt te schrijven.
    """
    if not GEMINI_API_KEY:
        return "Futuristic biotechnology laboratory, cinematic lighting, 8k"

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an AI art director. Read this summary and write ONE single, descriptive English prompt 
    to generate a cover image.
    
    Style: Photorealistic, cinematic lighting, 8k, highly detailed, cyberpunk or futuristic biotechnology elements.
    Subject: {article_text[:1000]}
    
    Return ONLY the prompt.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"⚠️ Text Gen Error: {e}")
        return "Futuristic biotechnology laboratory with green plants, cinematic lighting, 8k, photorealistic"

def create_image_pollinations(prompt, filename):
    """
    Gebruikt Pollinations.ai (Flux model) - Geen API key nodig.
    """
    print(f"🎨 Pollinations generating: {filename}...")
    
    safe_prompt = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&width=1280&height=720&nologo=true"
    
    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            path = os.path.join(STATIC_IMG_DIR, filename)
            with open(path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Saved to {path}")
            return path
        else:
            print(f"❌ Pollinations Error: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Download Error: {e}")
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
                            
                            with open(file_path, 'wb') as f:
                                frontmatter.dump(post, f)
                            
                            print("💤 Waiting 15s to respect Rate Limits...")
                            time.sleep(15)
                            
                except Exception as e:
                    print(f"Skipping {file}: {e}")

if __name__ == "__main__":
    process_files()