# AGENTS.md: Analyse van de Vegan BioTech Report Codebase

Dit document beschrijft de analyse van de codebase en de processen van de Vegan BioTech Report website. Het dient als intern referentiedocument voor het uitvoeren van de gevraagde taken.

## 1. Codebase Analyse

### a. Mappenstructuur en Bestandsorganisatie

-   **`content/`**: Bevat de Hugo content, opgesplitst in `newsletters`, `longreads`, en `posts`. Nieuwe content wordt programmatisch aangemaakt in submappen met een tijdstempel (bv. `content/newsletters/2025-11-24_04-01-25/`).
-   **`pipeline/`**: Bevat alle Python scripts die de content generatie en beheer verzorgen.
    - `run_pipeline.py`: Hoofdscript voor content creatie.
    - `generate_images.py`: Script voor AI afbeelding generatie.
    - `manage_content.py`: Script voor content beheer (archive/publish).
    - En diverse helper scripts (`fetch.py`, `curate.py`, etc.).
-   **`themes/ananke/`**: De Hugo-themamodule (Ananke).
-   **`layouts/`**: Bevat overschrijvingen op het thema (`index.html` voor homepage logica).
-   **`static/`**: Statische assets.
    - `css/custom.css`: Eigen CSS aanpassingen (tekstschaduw, filters).
    - `images/`: Gegenereerde en statische afbeeldingen.
-   **`.github/workflows/`**: GitHub Actions workflows voor automatisering.

### b. Content Generatie Pijplijn (pipeline/run_pipeline.py)

Het proces is volledig geautomatiseerd en kan zowel lokaal als via GitHub Actions worden gestart:

1.  **Archivering**: Oude content wordt indien nodig gearchiveerd (via `manage_content.py` logica).
2.  **Generatie**:
    - Data ophalen & cureren (`fetch.py`, `curate.py`).
    - Nieuwsbrieven & Artikelen schrijven (`draft.py`, `generate_longread.py`).
    - Afbeeldingen genereren (`generate_images.py`).
3.  **Deployment**: Hugo bouwt de site en pusht naar `gh-pages`.

## 2. Workflows (GitHub Actions)

Er zijn 6 gedefinieerde workflows voor beheer:

1.  **[AUTO] Generate Content & Deploy**: Volledige cyclus: genereren, afbeeldingen maken, deployen.
2.  **[MANUAL] Run Pipeline Only**: Draait alleen de generatie scripts (geen deploy).
3.  **[MANUAL] Fill Missing Images Only**: Scant content op ontbrekende afbeeldingen en genereert deze (zonder tekst te herschrijven).
4.  **[MANUAL] Deploy Site Only**: Bouwt en publiceert de huidige staat van de `main` branch.
5.  **[UTIL] Manage Content Status**: Tools om content te archiveren (`published` -> `archived`) of weer live te zetten.
6.  **[UTIL] View Content Status**: Rapporteert welke content live en welke gearchiveerd is.

## 3. Strategie & Status

### Gerealiseerde Verbeteringen
-   **Refactoring**: Scripts verplaatst van root/src naar `pipeline/` voor overzicht.
-   **Pipeline Modules**: Scripts draaien nu als Python modules (`python -m pipeline.screen_name`) voor betrouwbare imports.
-   **Image Management**: Afbeeldingen worden centraal in `static/images/` opgeslagen.
-   **CSS Styling**: `custom.css` zorgt voor leesbaarheid (tekstschaduw op heros/navigatie) zonder de rest van de site te storen.
-   **Frontmatter Beheer**: `manage_content.py` maakt gebruik van frontmatter status (`archived: true`) in plaats van bestanden fysiek te verplaatsen, waardoor Hugo meer controle heeft.

### Openstaande Punten
-   Verdere optimalisatie van prompts in `prompts/` map.
-   Eventuele uitbreiding van archief-pagina functionaliteit in Hugo templates.
