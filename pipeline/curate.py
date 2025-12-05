#!/usr/bin/env python3
"""
Curates the raw data from raw.json.
- Filters out items with an impact score below a threshold.
- Sorts the remaining items by impact, descending.
- Saves the result to curated.json.
Call: python -m pipeline.curate -i <input_file> -o <output_file>
"""
import json
import argparse

# --- Configuratie ----------------------------------------------------
MINIMUM_IMPACT_SCORE = 7  # Alleen nieuws met deze score of hoger wordt meegenomen
# ---------------------------------------------------------------------

# --- Argumenten Parser ---
parser = argparse.ArgumentParser(description="Filtert en sorteert ruwe nieuwsdata op basis van impact score.")
parser.add_argument('-i', '--input', type=str, required=True, help="Het pad naar het input JSON-bestand (raw.json).")
parser.add_argument('-o', '--output', type=str, required=True, help="Het pad naar het output JSON-bestand (curated.json).")
args = parser.parse_args()


# Lees de ruwe data
try:
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"❌ Fout bij het lezen van {args.input}. Zorg dat het bestand bestaat en valide JSON is. Fout: {e}")
    exit(1)

# Filter de data op basis van de impact score
# .get('impact', 0) zorgt ervoor dat het script niet crasht als een item geen 'impact' heeft.
curated_data = [
    item for item in data if item.get('impact', 0) >= MINIMUM_IMPACT_SCORE
]

# Sorteer de gefilterde data van hoge naar lage impact
curated_data.sort(key=lambda item: item.get('impact', 0), reverse=True)

# Sla de gecureerde data op
with open(args.output, "w", encoding="utf-8") as f:
    json.dump(curated_data, f, indent=2, ensure_ascii=False)

print(f"✅ Data gecureerd. {len(curated_data)} van de {len(data)} items zijn relevant en opgeslagen in {args.output}.")
