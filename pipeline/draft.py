# src/draft.py
import json
import os
import datetime
import sys
import argparse
from google import genai
from openai import OpenAI

def eprint(*args, **kwargs):
    """Helper functie om naar stderr te printen."""
    print(*args, file=sys.stderr, **kwargs)

# --- AI Model Selectie ---
API_TYPE = os.getenv('AI_API_TYPE')
MODEL_ID = os.getenv('AI_MODEL_ID')
API_KEY = os.getenv('AI_API_KEY')
BASE_URL = os.getenv('AI_BASE_URL')

def get_ai_response(client, model_id, prompt, api_type):
    """Genereert content en haalt op een robuuste manier de tekst op (Gemini 3.0 ready)."""
    if api_type == 'google':
        response = client.models.generate_content(model=model_id, contents=prompt)
        if hasattr(response, 'candidates') and response.candidates:
            parts = response.candidates[0].content.parts
            text_part = next((p.text for p in parts if p.text), None)
            if text_part:
                return text_part
        return response.text
    else:
        # OpenAI compatible client
        response = client.chat.completions.create(model=model_id, messages=[{"role": "user", "content": prompt}])
        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content
        return ""

PROMPT_TPL_PATH = "prompts/step3.txt"
CURATED_DATA_PATH = "curated.json"
LANGUAGES_CONFIG_PATH = "languages.json"
OUTPUT_DIR = os.getenv('VBR_CONTENT_DIR')
if not OUTPUT_DIR or not os.path.exists(OUTPUT_DIR):
    eprint(f"❌ Kritieke fout: VBR_CONTENT_DIR environment variabele is niet ingesteld of de map bestaat niet.")
    sys.exit(1)

model_client = None
eprint(f"Provider type: {API_TYPE}, Model: {MODEL_ID}")

if API_TYPE == 'google':
    model_client = genai.Client(api_key=API_KEY)
elif API_TYPE == 'openai_compatible':
    model_client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
else:
    raise ValueError(f"Ongeldig AI_API_TYPE: {API_TYPE}")

# --- Argumenten Parser ---
parser = argparse.ArgumentParser(description="Genereer een nieuwsbrief voor een specifieke datum in meerdere talen.")
parser.add_argument('--date', type=str, help="De datum voor de nieuwsbrief in YYYY-MM-DD formaat.")
parser.add_argument('-i', '--input', type=str, required=True, help="Het pad naar het input JSON-bestand (curated.json).")
args = parser.parse_args()

target_date = datetime.date.today()
if args.date:
    try:
        target_date = datetime.datetime.strptime(args.date, '%Y-%m-%d').date()
    except ValueError:
        eprint(f"❌ Ongeldig datumformaat voor --date: '{args.date}'. Gebruik YYYY-MM-DD.")
        exit(1)

today_iso = target_date.isoformat()
eprint(f"Nieuwsbrieven worden geschreven voor datum: {today_iso}")

# --- Data en Talen Laden ---
with open(PROMPT_TPL_PATH, "r", encoding="utf-8") as f:
    PROMPT_TPL = f.read()
try:
    with open(args.input, "r", encoding="utf-8") as f:
        news_data = json.load(f)
    with open(LANGUAGES_CONFIG_PATH, "r", encoding="utf-8") as f:
        all_languages = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    eprint(f"❌ Fout bij laden van configuratie- of databestanden. Fout: {e}")
    exit(1)

active_languages = [lang for lang in all_languages if lang.get("enabled", False)]

if not active_languages:
    eprint("⚠️ Geen talen ingeschakeld in 'languages.json'.")
    exit(0)

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Hoofdlogica: Loop over actieve talen ---
successful_drafts = 0
for lang_config in active_languages:
    lang_code = lang_config['code']
    lang_name = lang_config['name']
    edition_word = lang_config['edition_word']
    
    eprint("-" * 30)
    eprint(f"Voorbereiden van nieuwsbrief voor taal: {lang_name} ({lang_code})")
    
    edition_date_str = target_date.strftime('%d %b %Y')
    
    prompt = PROMPT_TPL.replace('{json_data}', json.dumps(news_data, indent=2, ensure_ascii=False))
    prompt = prompt.replace('{lang}', lang_name)
    prompt = prompt.replace('{edition_word}', edition_word)
    prompt = prompt.replace('{edition_date}', edition_date_str)

    eprint(f"🤖 Model '{MODEL_ID}' wordt aangeroepen voor de {lang_name} nieuwsbrief...")
    try:
        md = get_ai_response(model_client, MODEL_ID, prompt, API_TYPE)
        if md.strip().startswith("```markdown"):
            md = md.strip()[10:-3].strip()
        elif md.strip().startswith("```"):
             md = md.strip()[3:-3].strip()
        
        # Zoek de positie van de eerste H1 heading om ruis te verwijderen
        heading_pos = md.find('# ')
        if heading_pos != -1:
            # Verwijder alle ruis vóór de eerste heading
            clean_md = md[heading_pos:]
        else:
            # Fallback voor het geval er geen heading wordt gevonden
            clean_md = md.lstrip()

        # Extra controle om zeker te zijn dat we de titel pakken
        lines = clean_md.splitlines()
        raw_title = "Untitled" # Default titel
        for line in lines:
            if line.startswith('# '):
                raw_title = line.lstrip('# ').strip()
                break # Stop zodra de eerste titel is gevonden
        
        safe_title = raw_title.replace('"', '”')
        
        article_date = target_date.isoformat()
        
        # Zoek de eerste paragraaf na de titel voor de description
        first_paragraph = ""
        for line in lines:
            # Sla de titel en lege regels direct na de titel over
            if line.startswith('# ') or not line.strip():
                continue
            # De eerste niet-lege regel die geen titel is, is onze paragraaf
            first_paragraph = line.strip().replace('"', '”')
            break

        front_matter = f"""---
title: "{safe_title}"
date: {article_date}
description: "{first_paragraph}"
language: {lang_code}
---

"""
        
        # Gebruik de opgeschoonde markdown voor de body
        full_content = front_matter + clean_md

        # Voeg de <!--more--> tag toe aan het einde van de content
        full_content += "\n<!--more-->\n"

        output_filename = f"{OUTPUT_DIR}/{target_date.strftime('%Y-%m-%d')}_{lang_code}.md"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(full_content)
        eprint(f"✅ {output_filename} geschreven")
        successful_drafts += 1 # Tel een succesvolle poging op

    except Exception as e:
        eprint(f"❌ Fout bij API aanroep voor {lang_name}: {e}")
        continue # Ga door naar de volgende taal

# --- DE NIEUWE CONTROLE IS HIER ---
# Controleer na de loop of alle talen zijn verwerkt.
if successful_drafts < len(active_languages):
    eprint(f"❌ MISLUKT: Slechts {successful_drafts} van de {len(active_languages)} nieuwsbrieven konden worden gegenereerd.")
    sys.exit(1) # Sluit af met een foutcode

eprint("-" * 30)
eprint("✅ Alle ingeschakelde talen zijn verwerkt.")