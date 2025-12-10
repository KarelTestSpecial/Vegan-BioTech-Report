#!/usr/bin/env python3
import os
import glob
import argparse
import datetime

def get_content_files():
    """Vindt alle markdown-bestanden in de content-mappen."""
    files = []
    for content_type in ["newsletters", "longreads"]:
        search_path = os.path.join("content", content_type, "**", "*.md")
        files.extend(glob.glob(search_path, recursive=True))
    return files

def get_file_status(filepath):
    """Controleert of een bestand de 'archived: true' status heeft."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return "archived: true" in content
    except Exception:
        return False

def set_archive_status(filepath, archive: bool):
    """Voegt 'archived: true' toe of verwijdert het uit de front matter."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = content.split('---', 2)
        if len(parts) < 3:
            print(f"WAARSCHUWING: Kon geen valide front matter vinden in {filepath}. Bestand wordt overgeslagen.")
            return False

        front_matter = parts[1]
        body = parts[2]

        lines = front_matter.strip().split('\n')

        if archive:
            if "archived: true" not in front_matter:
                lines.append("archived: true")
        else: # Unarchive
            lines = [line for line in lines if "archived: true" not in line]

        new_front_matter = "\n".join(lines)
        new_content = f"""---
{new_front_matter}
---
{body}
"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"FOUT: Kon {filepath} niet aanpassen. Fout: {e}")
        return False

def archive_live_content():
    """Archiveert alle content die momenteel 'live' is."""
    print("--- Live content archiveren ---")
    files_to_archive = [f for f in get_content_files() if not get_file_status(f)]

    if not files_to_archive:
        print("Geen live content gevonden om te archiveren.")
        return

    for f in files_to_archive:
        if set_archive_status(f, archive=True):
            print(f"[ARCHIVED] {f}")
    print("\n✅ Alle live content is gearchiveerd.")

def unarchive_latest_content():
    """Zet de meest recente gearchiveerde content weer 'live'."""
    print("--- Meest recente gearchiveerde content live zetten ---")
    archived_files = [f for f in get_content_files() if get_file_status(f)]

    if not archived_files:
        print("Geen gearchiveerde content gevonden.")
        return

    # Sorteer op de directorynaam (die de timestamp bevat)
    latest_archived_run_dir = os.path.dirname(sorted(archived_files, reverse=True)[0])
    files_to_unarchive = [f for f in archived_files if os.path.dirname(f) == latest_archived_run_dir]

    print(f"De volgende content wordt live gezet (van run {os.path.basename(latest_archived_run_dir)}):")
    for f in files_to_unarchive:
        if set_archive_status(f, archive=False):
            print(f"[LIVE]     {f}")
    print("\n✅ Meest recente gearchiveerde content is weer live.")

def show_status():
    """Toont een overzicht van alle content en de status ervan."""
    print("--- Content Status Overzicht ---")
    files = get_content_files()
    if not files:
        print("Geen content gevonden.")
        return

    status_counts = {"live": 0, "archived": 0}
    for f in sorted(files):
        is_archived = get_file_status(f)
        status = "ARCHIVED" if is_archived else "LIVE"
        if is_archived:
            status_counts["archived"] += 1
        else:
            status_counts["live"] += 1
        print(f"[{status: <8}] {f}")

    print("\n--- Samenvatting ---")
    print(f"Live items:     {status_counts['live']}")
    print(f"Gearchiveerd:   {status_counts['archived']}")
    print(f"Totaal:         {len(files)}")

def main():
    parser = argparse.ArgumentParser(
        description="Een eenvoudig script om content te beheren voor de Vegan BioTech Report website.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Beschikbare commando's")

    # Status commando
    subparsers.add_parser("status", help="Toon een overzicht van alle content en de status (live/gearchiveerd).")

    # Archive commando
    subparsers.add_parser("archive", help="Archiveer alle 'live' content.")

    # Unarchive commando
    subparsers.add_parser("unarchive", help="Zet de meest recente set gearchiveerde content weer 'live'.")

    # Set-archived commando
    parser_set_archived = subparsers.add_parser("set-archived", help="Archiveer een of meerdere specifieke bestanden.")
    parser_set_archived.add_argument("files", nargs='+', help="De paden naar de bestanden die gearchiveerd moeten worden.")

    # Set-live commando
    parser_set_live = subparsers.add_parser("set-live", help="Zet een of meerdere specifieke bestanden weer live.")
    parser_set_live.add_argument("files", nargs='+', help="De paden naar de bestanden die live gezet moeten worden.")

    args = parser.parse_args()

    if args.command == "status":
        show_status()
    elif args.command == "archive":
        archive_live_content()
    elif args.command == "unarchive":
        unarchive_latest_content()
    elif args.command == "set-archived":
        for f in args.files:
            if os.path.exists(f):
                if set_archive_status(f, archive=True):
                    print(f"[ARCHIVED] {f}")
            else:
                print(f"FOUT: Bestand niet gevonden: {f}")
    elif args.command == "set-live":
        for f in args.files:
            if os.path.exists(f):
                if set_archive_status(f, archive=False):
                    print(f"[LIVE]     {f}")
            else:
                print(f"FOUT: Bestand niet gevonden: {f}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
