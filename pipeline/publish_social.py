# src/publish_social.py
import os
import sys
import json
from dotenv import load_dotenv
from google import genai
from openai import OpenAI

def eprint(*args, **kwargs):
    """Helper functie om naar stderr te printen."""
    print(*args, file=sys.stderr, **kwargs)

def get_ai_client_info():
    """Geeft de geconfigureerde AI-client informatie terug."""
    API_TYPE = os.getenv('AI_API_TYPE')
    MODEL_ID = os.getenv('AI_MODEL_ID')
    API_KEY = os.getenv('AI_API_KEY')
    BASE_URL = os.getenv('AI_BASE_URL')

    if not all([API_TYPE, MODEL_ID, API_KEY]):
        eprint("⚠️ WAARSCHUWING: AI-configuratievariabelen niet volledig ingesteld voor flair-selectie.")
        return None, None, None

    try:
        if API_TYPE == 'google':
            return genai.Client(api_key=API_KEY), MODEL_ID, API_TYPE
        elif API_TYPE == 'openai_compatible':
            return OpenAI(base_url=BASE_URL, api_key=API_KEY), MODEL_ID, API_TYPE
        else:
            eprint(f"⚠️ WAARSCHUWING: Ongeldig AI_API_TYPE '{API_TYPE}' voor flair-selectie.")
            return None, None, None
    except Exception as e:
        eprint(f"⚠️ WAARSCHUWING: Kon AI-client voor flair-selectie niet initialiseren. Fout: {e}")
        return None, None, None

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

def select_best_flair_with_ai(title: str, available_flairs: list, client_info) -> str or None:
    """Gebruikt AI om de beste flair te selecteren uit een lijst."""
    client, model_id, api_type = client_info
    if not client or not available_flairs:
        return None

    flair_texts = [f"'{flair['text']}'" for flair in available_flairs]
    flair_list_str = ", ".join(flair_texts)

    prompt = f"""
    You are a Reddit expert. Your task is to select the most appropriate flair for a post.
    Analyze the post title and choose the best option from the list of available flairs.

    Post Title: "{title}"

    Available Flairs: [{flair_list_str}]

    CRITICAL: Respond with ONLY the single, exact text of the best flair from the provided list.
    For example, if you choose the flair 'Biology', your entire response must be just: Biology
    Do not add any explanation, punctuation, or quotation marks.
    """

    eprint(f"🤖 AI wordt aangeroepen om de beste flair te kiezen uit: {flair_list_str}")
    try:
        chosen_flair_text = get_ai_response(client, model_id, prompt, api_type).strip().strip("'\"")

        for flair in available_flairs:
            if flair['text'] == chosen_flair_text:
                eprint(f"✅ AI heeft een geldige flair gekozen: '{chosen_flair_text}'")
                return flair['id']

        eprint(f"⚠️ AI koos een ongeldige flair: '{chosen_flair_text}'. Poging wordt gestaakt.")
        return None
    except Exception as e:
        eprint(f"❌ Fout tijdens AI-flair selectie: {e}")
        return None

def post_to_mastodon(post_content):
    """Publiceert een post op Mastodon."""
    eprint("-> Poging tot publicatie op Mastodon...")
    try:
        from mastodon import Mastodon, MastodonError
    except ImportError:
        eprint("❌ FOUT: De 'Mastodon.py' library is niet geïnstalleerd.")
        return

    api_base_url = os.getenv('MASTODON_API_BASE_URL')
    access_token = os.getenv('MASTODON_ACCESS_TOKEN')

    if not all([api_base_url, access_token]):
        eprint("❌ FOUT: Mastodon credentials niet gevonden in omgevingsvariabelen.")
        return

    try:
        mastodon_api = Mastodon(access_token=access_token, api_base_url=api_base_url)
        status = mastodon_api.status_post(post_content['text_content'])
        eprint(f"✅ SUCCES: Gepost op Mastodon! URL: {status['url']}")
    except MastodonError as e:
        eprint(f"❌ FOUT: Publicatie op Mastodon mislukt: {e}")
    except Exception as e:
        eprint(f"❌ FOUT: Een onverwachte fout is opgetreden bij Mastodon: {e}")

def post_to_reddit(post_content, ai_client_info):
    """Publiceert een post op Reddit, inclusief dynamische flair-selectie."""
    reddit_details = post_content.get('reddit_details')
    if not reddit_details:
        eprint("❌ FOUT: Kan niet posten op Reddit. 'reddit_details' object ontbreekt.")
        return

    target_subreddit = reddit_details.get('suggested_subreddit', 'r/test').lstrip('r/')
    title = reddit_details.get('post_title')
    text_content = post_content.get('text_content')

    if not all([title, text_content]):
        eprint("❌ FOUT: Reddit post mist 'post_title' of 'text_content'.")
        return

    eprint(f"-> Poging tot publicatie op Reddit in r/{target_subreddit}...")

    try:
        import praw
        from praw.exceptions import RedditAPIException
        from prawcore.exceptions import PrawcoreException
    except ImportError:
        eprint("❌ FOUT: De 'praw' library is niet geïnstalleerd.")
        return

    client_id = os.getenv('REDDIT_CLIENT_ID')
    client_secret = os.getenv('REDDIT_CLIENT_SECRET')
    username = os.getenv('REDDIT_USERNAME')
    password = os.getenv('REDDIT_PASSWORD')
    user_agent = os.getenv('REDDIT_USER_AGENT')

    if not all([client_id, client_secret, username, password, user_agent]):
        eprint("❌ FOUT: Reddit credentials niet gevonden.")
        return

    try:
        reddit_api = praw.Reddit(
            client_id=client_id, client_secret=client_secret,
            username=username, password=password, user_agent=user_agent
        )
        subreddit = reddit_api.subreddit(target_subreddit)

        flair_id = None
        try:
            available_flairs = list(subreddit.flair.link_templates)
            if available_flairs:
                flair_id = select_best_flair_with_ai(title, available_flairs, ai_client_info)
            else:
                eprint("INFO: Subreddit heeft geen configureerbare flairs.")
        except Exception as e:
            eprint(f"⚠️ WAARSCHUWING: Kon flairs niet ophalen of verwerken. Fout: {e}")

        submission = subreddit.submit(title=title, selftext=text_content, flair_id=flair_id)
        eprint(f"✅ SUCCES: Gepost op Reddit! URL: {submission.shortlink}")

    except RedditAPIException as e:
        for subexception in e.items:
            if subexception.error_type == 'SUBMIT_VALIDATION_FLAIR_REQUIRED':
                eprint(f"❌ FOUT: r/{target_subreddit} vereist een flair, maar een geldige kon niet dynamisch worden gekozen. De AI-selectie is mogelijk mislukt of er zijn geen flairs beschikbaar.")
                return
        eprint(f"❌ FOUT: Reddit API fout: {e}")
    except PrawcoreException as e:
        eprint(f"❌ FOUT: Kon niet verbinden met Reddit. Controleer je credentials. Foutmelding: {e}")
    except Exception as e:
        eprint(f"❌ FOUT: Een onverwachte fout is opgetreden bij Reddit: {e}")

if __name__ == "__main__":
    eprint("--- Starting Social Media Publisher ---")
    load_dotenv()

    URL_INPUT_FILE = "published_post_url.txt"
    try:
        with open(URL_INPUT_FILE, "r", encoding="utf-8") as f:
            article_url = f.read().strip()
        eprint(f"INFO: Specifieke artikel-URL geladen: {article_url}")
    except FileNotFoundError:
        eprint(f"⚠️ WAARSCHUWING: {URL_INPUT_FILE} niet gevonden. Fallback naar algemene GHOST_PUBLIC_URL.")
        article_url = os.getenv('GHOST_PUBLIC_URL')

    if not article_url:
        eprint("❌ FOUT: Geen artikel-URL of GHOST_PUBLIC_URL beschikbaar.")
        sys.exit(1)

    try:
        with open("social_posts.json", "r", encoding="utf-8") as f:
            posts_to_publish = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        eprint(f"❌ FOUT: Kan 'social_posts.json' niet lezen of parsen. Fout: {e}")
        sys.exit(1)

    # Initialiseer de AI-client informatie eenmalig
    ai_client_info = get_ai_client_info()

    for post in posts_to_publish:
        platform = post.get("platform")
        eprint(f"\nVerwerken van post voor platform: {platform}")

        if 'text_content' in post and post['text_content']:
            post['text_content'] = post['text_content'].replace('{{GHOST_ARTICLE_URL}}', article_url)

        if platform == "mastodon":
            post_to_mastodon(post)
        elif platform == "reddit":
            # De aanroep naar post_to_reddit is hier verwijderd.
            eprint("INFO: Publicatie naar Reddit is momenteel gepauzeerd. Post wordt overgeslagen.")
        else:
            eprint(f"⚠️ WAARSCHUWING: Geen publicatielogica voor platform '{platform}'. Post wordt overgeslagen.")

    eprint("\n--- Social Media Publisher Finished ---")