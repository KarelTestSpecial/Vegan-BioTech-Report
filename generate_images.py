import os
import time
import frontmatter
import google.generativeai as genai
import requests
from urllib.parse import quote

# --- CONFIGURATIE ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
CONTENT_DIR = "content" # Zoekt in alle submappen (newsletters, longreads, etc.)
STATIC_IMG_DIR = "static/images/generated"

# Installeer Google
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Zorg dat de map bestaat
os.makedirs(STATIC_IMG_DIR, exist_ok=True)

def generate_image_prompt(article_text):
    """
    Vraagt Gemini (tekst) om een prompt te schrijven.
    """
    # We gebruiken de stabiele 1.5 Flash als prompt-writer (minder strict quota)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
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
        # Fallback prompt als Gemini faalt door quota
        return "Futuristic biotechnology laboratory with green plants, cinematic lighting, 8k, photorealistic"

def create_image_pollinations(prompt, filename):
    """
    Gebruikt Pollinations.ai (Flux model) - Geen API key nodig, heel stabiel.
    """
    print(f"🎨 Pollinations generating: {filename}...")
    
    # Maak de prompt veilig voor een URL
    safe_prompt = quote(prompt)
    
    # We gebruiken het 'flux' model (erg goed)
    url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&width=1280&height=720&nologo=true"
    
    try:
        # Timeout van 60 seconden, want plaatjes maken duurt even
        response = requests.get(url, timeout=60)
        
        if response.status_code == 200:
            path = os.path.join(STATIC_IMG_DIR, filename)
            with open(path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Saved to {path}")
            return f"/images/generated/{filename}" # Return relative URL for Hugo
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
                    
                    # Check of er al een afbeelding is
                    # We checken zowel 'image' als 'featured_image'
                    if not post.get('featured_image') and not post.get('image') and not post.get('cover'):
                        print(f"Processing {file}...")
                        
                        # 1. Genereer prompt met Gemini
                        image_prompt = generate_image_prompt(post.content)
                        print(f"   Prompt: {image_prompt[:50]}...")
                        
                        # 2. Genereer bestandsnaam
                        img_filename = file.replace(".md", ".png")
                        
                        # 3. Maak afbeelding met Pollinations
                        relative_path = create_image_pollinations(image_prompt, img_filename)
                        if relative_path:
                            # 4. Update Frontmatter
                            post['featured_image'] = relative_path
                            
                            with open(file_path, 'wb') as f:
                                frontmatter.dump(post, f)
                            
                            # CRUCIAAL: PAUZE VOOR RATE LIMITS
                            # We wachten 15 seconden tussen elk bestand om Gemini rust te geven
                            print("💤 Waiting 15s to respect Google Quota...")
                            time.sleep(15)
                            
                except Exception as e:
                    print(f"Skipping {file}: {e}")

if __name__ == "__main__":
    process_files()
