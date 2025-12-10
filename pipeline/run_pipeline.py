# pipeline/run_pipeline.py

import time
import json
import os
import subprocess
import sys
import datetime
import argparse
import shutil
import glob
from dotenv import load_dotenv
load_dotenv()
from urllib.parse import urljoin

def eprint(*args, **kwargs):
    """Helper functie om naar stderr te printen."""
    print(*args, file=sys.stderr, **kwargs)

def run_command(command: list, env: dict):
    """Voert een command uit en vangt output en fouten af."""
    process = subprocess.run(command, capture_output=True, text=True, env=env)
    if process.stderr:
        eprint(process.stderr.strip())
    if process.returncode != 0:
        eprint(f"--- Fout bij uitvoeren: {' '.join(command)} ---")
        if process.stdout:
            eprint("--- STDOUT (bij fout) ---")
            eprint(process.stdout.strip())
        raise subprocess.CalledProcessError(process.returncode, command)
    return process

def archive_output_files():
    """Archiveert oude output-bestanden naar een timestamped map in de archive directory."""
    output_dir = "output"
    data_files = [os.path.join(output_dir, f) for f in ["raw.json", "curated.json", "longread_outline.json", "last_topics.json"]]

    existing_files = [f for f in data_files if os.path.exists(f)]

    if not existing_files:
        eprint("Geen bestaande output-bestanden gevonden om te archiveren.")
        return
    
    archive_dir = "archive"
    os.makedirs(archive_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_archive_dir = os.path.join(archive_dir, timestamp, "output")
    os.makedirs(run_archive_dir)
    
    for file_path in existing_files:
        shutil.move(file_path, run_archive_dir)

    eprint(f"Oude output-bestanden gearchiveerd in: {run_archive_dir}")

def get_provider_list():
    """Haalt de lijst van AI providers op uit providers.json."""
    try:
        with open('providers.json', 'r') as f:
            all_providers = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        eprint(f"❌ Kon providers.json niet laden. Fout: {e}")
        return []
    
    forced_provider_id = os.getenv('FORCED_PROVIDER')
    if forced_provider_id and forced_provider_id != 'auto':
        eprint(f"⚡️ Modus: Specifieke provider geforceerd: '{forced_provider_id}'")
        found_provider = next((p for p in all_providers if p['id'] == forced_provider_id), None)
        return [found_provider] if found_provider else []
    return all_providers

def build_script_env(provider_config: dict, content_dir: str) -> dict: 
    """Bouwt de environment dictionary voor subprocessen."""
    script_env = os.environ.copy()
    script_env['AI_API_TYPE'] = provider_config['api_type']
    script_env['AI_MODEL_ID'] = provider_config['model_id']
    script_env['AI_API_KEY'] = os.getenv(provider_config['api_key_name'])
    if provider_config.get('base_url'):
        script_env['AI_BASE_URL'] = provider_config['base_url']
    if content_dir:
        script_env['VBR_CONTENT_DIR'] = content_dir
    return script_env

def run_task_with_fallback(task_name: str, task_function, providers_to_run):
    """Draait een taak met provider fallback logica."""
    for i, provider_config in enumerate(providers_to_run):
        if not provider_config:
            eprint(f"⚠️ WAARSCHUWING: Ongeldige providerconfiguratie overgeslagen.")
            continue
        
        provider_id = provider_config['id']
        api_key_name = provider_config['api_key_name']
        api_key_value = os.getenv(api_key_name)
        
        eprint("\n" + "="*50)
        eprint(f"POGING {i+1}/{len(providers_to_run)} voor taak '{task_name}': Gebruik provider '{provider_id}'")
        eprint("="*50)
        
        if not api_key_value:
            eprint(f"⚠️ WAARSCHUWING: API-sleutel '{api_key_name}' niet gevonden. Provider wordt overgeslagen.")
            continue
        try:
            result = task_function(provider_config)
            eprint(f"✅ SUCCES: Taak '{task_name}' voltooid met provider '{provider_id}'.")
            return result
        except Exception as e:
            eprint(f"❌ MISLUKT: Taak '{task_name}' gefaald met provider '{provider_id}'. Fout: {e}")
            if i < len(providers_to_run) - 1:
                eprint("Probeer de volgende provider...")
    
    raise RuntimeError(f"DRAMATISCHE FOUT: Kon taak '{task_name}' met geen enkele provider voltooien.")

def run_full_pipeline(target_date_str: str or None, no_archive: bool):
    """De hoofd-pipeline die alle stappen voor contentgeneratie coördineert."""
    
    run_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    if not no_archive:
        archive_output_files()
    else:
        eprint("Archivering van output bestanden overgeslagen vanwege de --no-archive vlag.")

    target_date = datetime.date.today()
    if target_date_str:
        target_date = datetime.datetime.strptime(target_date_str, '%Y-%m-%d').date()
    target_date_iso = target_date.isoformat()

    providers_to_run = get_provider_list()
    if not providers_to_run:
        eprint("❌ Geen geldige providers gevonden.")
        sys.exit(1)

    # Maak aparte directories voor nieuwsbrieven en longreads
    newsletter_content_dir = os.path.join("content", "newsletters", run_timestamp)
    longread_content_dir = os.path.join("content", "longreads", run_timestamp)
    os.makedirs(newsletter_content_dir, exist_ok=True)
    os.makedirs(longread_content_dir, exist_ok=True)
    eprint(f"Nieuwsbrieven voor deze run worden opgeslagen in: {newsletter_content_dir}")
    eprint(f"Longreads voor deze run worden opgeslagen in: {longread_content_dir}")

    enabled_langs = [lang for lang in json.load(open('languages.json')) if lang.get('enabled')]

    # Definieer output bestanden
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    raw_json_path = os.path.join(output_dir, "raw.json")
    curated_json_path = os.path.join(output_dir, "curated.json")
    outline_path = os.path.join(output_dir, "longread_outline.json")
    topics_file = os.path.join(output_dir, "last_topics.json")

    # Stap 1-3: Fetch, Curate, Draft (draaien nu altijd)
    eprint("\n--- Stap 1: Fetch Data ---")
    run_task_with_fallback("Fetch Data", lambda p: run_command(["python3", "-m", "pipeline.fetch", "--date", target_date_iso, "-o", raw_json_path], env=build_script_env(p, None)), providers_to_run)

    eprint("💤 Even 10 seconden pauze voor de API quota...")
    time.sleep(10)

    eprint("\n--- Stap 2: Curate Data ---")
    run_command(["python3", "-m", "pipeline.curate", "-i", raw_json_path, "-o", curated_json_path], env=os.environ.copy())

    eprint("\n--- Stap 3: Draft Newsletters ---")
    run_task_with_fallback("Draft Newsletters", lambda p: run_command(["python3", "-m", "pipeline.draft", "--date", target_date_iso, "-i", curated_json_path], env=build_script_env(p, newsletter_content_dir)), providers_to_run)

    eprint("💤 Even 30 seconden pauze na het zware schrijfwerk...")
    time.sleep(30)

    # Stap 4: Genereer de Engelse outline (draait nu altijd)
    eprint("\n--- Stap 4: Generate Long-Read Outline ---")
    def task_select_and_generate_outline(provider_config):
        env = build_script_env(provider_config, None) # Geen content dir nodig voor deze stappen
        # Stap 4a: Selecteer onderwerp
        topic_process = run_command(["python3", "-m", "pipeline.select_topic", "-i", curated_json_path, "--history-file", topics_file], env=env)
        longread_topic = topic_process.stdout.strip()

        # Stap 4b: Genereer de outline
        run_command(["python3", "-m", "pipeline.generate_longread_outline", longread_topic, "--outline-out", outline_path], env=env)

        # Stap 4c: Update de lijst met vorige onderwerpen
        try:
            with open(outline_path, 'r', encoding='utf-8') as f:
                new_outline = json.load(f)
            new_topic_title = new_outline.get('title')

            if new_topic_title:
                previous_topics = []
                try:
                    with open(topics_file, 'r', encoding='utf-8') as f:
                        previous_topics = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    pass

                previous_topics.append(new_topic_title)
                # Bewaar de laatste 6 onderwerpen
                previous_topics = previous_topics[-6:]

                with open(topics_file, 'w', encoding='utf-8') as f:
                    json.dump(previous_topics, f, indent=2)
                eprint(f"✅ Onderwerpgeschiedenis bijgewerkt in {topics_file}")

        except Exception as e:
            eprint(f"⚠️ Kon de onderwerpgeschiedenis niet bijwerken: {e}")

    run_task_with_fallback("Generate Long-Read Outline", task_select_and_generate_outline, providers_to_run)

    eprint("💤 Even 10 seconden pauze...")
    time.sleep(10)


    # Stap 5: Genereer de longread voor elke actieve taal
    eprint("\n--- Stap 5: Generate Long-Read Articles ---")
    for lang_config in enabled_langs:
        lang_code = lang_config['code']
        lang_name = lang_config['name']
        output_path = os.path.join(longread_content_dir, f"longread_{target_date_iso}_{lang_code}.md")

        def task_generate_article(provider_config):
            run_command([
                "python3", "-m", "pipeline.generate_longread",
                "--outline-in", outline_path,
                "-o", output_path,
                "--lang-name", lang_name
            ], env=build_script_env(provider_config, None)) # Content dir niet nodig, output path is absoluut
        run_task_with_fallback(f"Generate Long-Read ({lang_name})", task_generate_article, providers_to_run)
    
    eprint("\n✅ Pijplijn voor content generatie voltooid.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Draait de content generatie pijplijn voor de SSG.")
    parser.add_argument("--date", type=str, help="De datum (YYYY-MM-DD) waarvoor content gegenereerd moet worden.")
    parser.add_argument("--no-archive", action='store_true', help="Sla het archiveren van oude content over.")
    args = parser.parse_args()
    
    run_full_pipeline(args.date, args.no_archive)