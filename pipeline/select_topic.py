# src/select_topic.py
import os, glob, argparse, sys, json
import google.generativeai as genai
from openai import OpenAI

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def select_best_topic(news_context: str, previous_topics: list) -> str:
    API_TYPE = os.getenv('AI_API_TYPE')
    MODEL_ID = os.getenv('AI_MODEL_ID')
    API_KEY = os.getenv('AI_API_KEY')
    BASE_URL = os.getenv('AI_BASE_URL')
    
    model = None
    eprint(f"Provider type: {API_TYPE}, Model: {MODEL_ID}")

    if API_TYPE == 'google':
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(MODEL_ID)
    elif API_TYPE == 'openai_compatible':
        client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
        class OpenRouterModel:
            def generate_content(self, prompt):
                response = client.chat.completions.create(model=MODEL_ID, messages=[{"role": "user", "content": prompt}])
                content = ""
                if response.choices and len(response.choices) > 0:
                    choice = response.choices[0]
                    if choice.message and choice.message.content:
                        content = choice.message.content
                
                class ResponseWrapper:
                    def __init__(self, text): self.text = text
                return ResponseWrapper(content)
        model = OpenRouterModel()
    else:
        raise ValueError(f"Ongeldig AI_API_TYPE: {API_TYPE}.")

    previous_topics_list = "\n".join(f"- {topic}" for topic in previous_topics)
    prompt = f"""
    You are a senior content strategist for the "Vegan BioTech Report".
    Your task is to analyze the following JSON data, which contains a list of curated news items, and identify the single most compelling topic for a deep-dive, long-read article (1500-2500 words).
    The ideal topic should have significant long-term impact, be based on a concrete news item (from the `source_url`), and be broad enough for a deep analysis.

    Analyze the JSON data below:
    ---
    {news_context}
    ---

    **VERY IMPORTANT**: Avoid selecting a topic that is too similar to the following recently used topics:
    {previous_topics_list}

    Based on your analysis, formulate a single, descriptive sentence that can be used as a direct input prompt for another AI writer.
    **CRITICAL:** Your ENTIRE output must be ONLY this single sentence. Do not add any commentary, headings, or quotation marks.
    """
    
    eprint(f"🤖 Model '{MODEL_ID}' wordt aangeroepen om onderwerp te selecteren...")
    response = model.generate_content(prompt)
    selected_topic = response.text.strip().strip('"')
    return selected_topic

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Selecteert het beste long-read onderwerp uit een lijst met gecureerd nieuws.")
    parser.add_argument("-i", "--input", type=str, required=True, help="JSON-bestand met gecureerd nieuws.")
    parser.add_argument("--history-file", type=str, help="JSON-bestand met een lijst van eerder gebruikte onderwerpen.")
    args = parser.parse_args()

    previous_topics = []
    if args.history_file:
        try:
            with open(args.history_file, 'r', encoding='utf-8') as f:
                previous_topics = json.load(f)
            eprint(f"Eerder gebruikte onderwerpen geladen uit {args.history_file}")
        except (FileNotFoundError, json.JSONDecodeError):
            eprint(f"Waarschuwing: Kon {args.history_file} niet laden. Ga verder met een lege lijst.")

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            news_data = json.load(f)

        # Converteer de nieuwsdata naar een leesbare string voor de prompt
        news_context = json.dumps(news_data, indent=2, ensure_ascii=False)

        topic = select_best_topic(news_context, previous_topics)
        print(topic) # Print de output naar stdout zodat run_pipeline.py het kan opvangen
    except Exception as e:
        eprint(f"❌ Fout: {e}")
        exit(1)