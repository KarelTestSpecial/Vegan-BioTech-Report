# src/generate_longread.py
import os, sys, argparse, json, re, datetime
from typing import List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from pipeline.models import ArticleOutline


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def generate_longread_article(outline_path: str, output_path: str, lang_name: str, lang_code: str):
    eprint(f"AI pipeline started for language: {lang_name}...")
    API_TYPE = os.getenv('AI_API_TYPE')
    MODEL_ID = os.getenv('AI_MODEL_ID')
    API_KEY = os.getenv('AI_API_KEY')
    BASE_URL = os.getenv('AI_BASE_URL')
    llm = None
    
    eprint(f"Provider type: {API_TYPE}, Model: {MODEL_ID}")

    if API_TYPE == 'google':
        llm = ChatGoogleGenerativeAI(model=MODEL_ID, google_api_key=API_KEY, temperature=0.7)
    elif API_TYPE == 'openai_compatible':
        llm = ChatOpenAI(model=MODEL_ID, openai_api_base=BASE_URL, api_key=API_KEY, temperature=0.7)
    else:
        raise ValueError(f"Ongeldig AI_API_TYPE: {API_TYPE}")

    eprint(f"LangChain model geïnitialiseerd: {getattr(llm, 'model', 'Onbekend')}")

    try:
        with open(outline_path, "r", encoding="utf-8") as f:
            outline = ArticleOutline.model_validate_json(f.read())
        eprint(f"✓ Outline successfully loaded. English Title: '{outline.title}'")
    except FileNotFoundError:
        eprint(f"❌ Fout: Outline bestand niet gevonden op {outline_path}")
        sys.exit(1)

    eprint(f"Generating full article in {lang_name} from outline...")
    sections_list_str = ""
    for i, section in enumerate(outline.sections):
        sections_list_str += f"{i+1}. Title: {section.title}\n   Talking Points: {', '.join(section.talking_points)}\n"

    article_input = {
        "title": outline.title,
        "introduction_hook": outline.introduction_hook,
        "conclusion_summary": outline.conclusion_summary,
        "sections_list": sections_list_str,
        "lang_name": lang_name
    }
    
    prompt_full_article_text = """
    You are a talented writer. Your task is to write a complete, in-depth article in {lang_name} based on the provided structured English outline.

    CRITICAL: The ENTIRE article, including the title, must be written in {lang_name}.

    English Outline:
    - Article Title: {title}
    - Introduction Hook: {introduction_hook}
    - Conclusion Summary: {conclusion_summary}
    - Sections to write:
    {sections_list}

    Your tasks:
    1.  Create a new, catchy, and natural-sounding title for the article in {lang_name}. Do NOT literally translate the English title.
    2.  Write a compelling introduction in {lang_name} based on the 'Introduction Hook'.
    3.  Write a detailed section in {lang_name} for EACH item in the 'Sections to write' list.
    4.  Format the entire result as a single Markdown document. Start with the new # Title in {lang_name}. Use ## for section titles.

    FINAL ARTICLE IN {lang_name}:
    """
    prompt_full_article = PromptTemplate.from_template(prompt_full_article_text)
    chain_full_article = prompt_full_article | llm | StrOutputParser()
    eprint("✓ Full Article Writer Chain has been built.")
    
    final_article_markdown = chain_full_article.invoke(article_input)
    eprint(f"✓ Full article in {lang_name} generated!")
    eprint("-" * 50)
    
    # --- DE ROBUUSTE OPSCHOONLOGICA ---
    content = final_article_markdown
    if content.strip().startswith("```markdown"):
        content = content.strip()[10:]
    if content.strip().startswith("```"):
        content = content.strip()[3:]
    if content.strip().endswith("```"):
        content = content.strip()[:-3]
    content = content.strip()
    heading_pos = content.find('# ')
    if heading_pos > 0:
        content = content[heading_pos:]
    cleaned_markdown = content

    def _fallback_insert_more(markdown_content: str, reason: str) -> str:
        """Inserts the <!--more--> tag before the first H2 heading as a fallback."""
        h2_pattern = re.compile(r'^\s*## ', re.MULTILINE)
        match = h2_pattern.search(markdown_content)
        if match:
            insertion_point = match.start()
            result = markdown_content[:insertion_point] + '<!--more-->\n\n' + markdown_content[insertion_point:]
            eprint(f"✓ <!--more--> tag ingevoegd (fallback-logica: {reason}).")
            return result
        return markdown_content

    # Logic to insert the <!--more--> tag based on the first paragraph
    lines = cleaned_markdown.split('\n')
    title_line_index = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('# '):
            title_line_index = i
            break

    if title_line_index == -1:
        cleaned_markdown = _fallback_insert_more(cleaned_markdown, "geen H1 gevonden")
    else:
        # Find the first paragraph after the title
        first_paragraph_start_index = -1
        for i in range(title_line_index + 1, len(lines)):
            if lines[i].strip():
                first_paragraph_start_index = i
                break

        if first_paragraph_start_index != -1:
            first_paragraph_end_index = -1
            for i in range(first_paragraph_start_index, len(lines)):
                if not lines[i].strip():
                    first_paragraph_end_index = i
                    break
            if first_paragraph_end_index == -1:
                first_paragraph_end_index = len(lines)

            paragraph_lines = lines[first_paragraph_start_index:first_paragraph_end_index]
            paragraph_text = "\n".join(paragraph_lines)
            words_in_paragraph = paragraph_text.split()

            if len(words_in_paragraph) > 100:
                word_count = 0
                inserted = False
                for i in range(len(paragraph_lines)):
                    line_words = paragraph_lines[i].split()
                    if not inserted and word_count + len(line_words) >= 100:

                        word_index_in_line = 100 - word_count

                        before_tag_words = line_words[:word_index_in_line]
                        after_tag_words = line_words[word_index_in_line:]

                        # Reconstruct the line with the tag, handling potential empty strings
                        parts = []
                        if before_tag_words:
                            parts.append(' '.join(before_tag_words))

                        parts.append('<!--more-->')

                        if after_tag_words:
                            parts.append(' '.join(after_tag_words))

                        paragraph_lines[i] = ' '.join(parts)

                        inserted = True
                        eprint("✓ <!--more--> tag ingevoegd in de eerste paragraaf (na 100 woorden), met behoud van opmaak.")
                        break

                    word_count += len(line_words)

                lines[first_paragraph_start_index:first_paragraph_end_index] = paragraph_lines

            else:
                lines.insert(first_paragraph_end_index, '<!--more-->')
                eprint("✓ <!--more--> tag ingevoegd na de eerste paragraaf.")

            cleaned_markdown = "\n".join(lines)
        else:
            cleaned_markdown = _fallback_insert_more(cleaned_markdown, "geen paragraaf gevonden")
    
    # Pak de titel uit de opgeschoonde content
    lines = cleaned_markdown.splitlines()
    raw_title = "Untitled" # Default title
    # Zoek naar de eerste regel die daadwerkelijk een H1 heading is
    for line in lines:
        if line.strip().startswith('# '):
            raw_title = line.strip().lstrip('# ').strip()
            break # Stop zodra de eerste titel is gevonden
            
    safe_title = raw_title.replace('"', '”')


    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', output_path)
    article_date = date_match.group(1) if date_match else datetime.date.today().isoformat()

    front_matter = f"""---
title: "{safe_title}"
date: {article_date}
language: {lang_code}
---

"""
    
    full_content = front_matter + cleaned_markdown
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_content)
    eprint(f"✅ Article with front matter successfully saved as: {output_path}")

if __name__ == "__main__":
    load_dotenv()
    parser = argparse.ArgumentParser(description="Generate a long-read article from an outline in a specific language.")
    parser.add_argument("--outline-in", type=str, required=True, help="The path to the input JSON outline.")
    parser.add_argument("-o", "--output", type=str, required=True, help="The path to the output Markdown file.")
    parser.add_argument("--lang-name", required=True, type=str, help="The full name of the target language (e.g., 'Nederlands').")
    parser.add_argument("--lang-code", required=True, type=str, help="The code of the target language (e.g., 'en', 'nl').")
    
    args = parser.parse_args()
    
    generate_longread_article(args.outline_in, args.output, args.lang_name, args.lang_code)
