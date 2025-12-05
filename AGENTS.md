# AGENTS.md: Analyse van de Vegan BioTech Report Codebase

Dit document beschrijft de analyse van de codebase en de processen van de Vegan BioTech Report website. Het dient als intern referentiedocument voor het uitvoeren van de gevraagde taken.

## 1. Codebase Analyse

### a. Mappenstructuur en Bestandsorganisatie

-   **`content/`**: Bevat de Hugo content, opgesplitst in `newsletters`, `longreads`, en `posts`. Nieuwe content wordt programmatisch aangemaakt in submappen met een tijdstempel (bv. `content/newsletters/2025-11-24_04-01-25/`).
-   **`src/`**: Bevat alle Python scripts die de content generatie pijplijn vormen. Dit is het hart van de automatisering.
-   **`archive/`**: Bevat gearchiveerde content. De `run_pipeline.py` verplaatst oudere content van `content/` naar een nieuwe submap met tijdstempel in `archive/`. Dit is de reden waarom oudere content niet op de live site verschijnt: Hugo verwerkt alleen bestanden binnen de `content/` map.
-   **`themes/ananke/`**: De Hugo-thema dat het uiterlijk van de site bepaalt. Aanpassingen aan de layout en het design moeten hier gebeuren.
-   **`layouts/`**: Bevat overschrijvingen of toevoegingen aan het Ananke-thema. Momenteel bevat het een `_default/baseof.html` en een `partials/summary.html`, wat wijst op maatwerk.
-   **`hugo.toml`**: Het hoofdconfiguratiebestand voor de Hugo-site. Bepaalt de titel, het thema, de menu's en welke secties als "main" worden beschouwd.
-   **`run_pipeline.py`**: Het centrale script dat het hele contentgeneratieproces orkestreert, van data ophalen tot social media posts genereren.

### b. Content Generatie Pijplijn (run_pipeline.py)

Het proces is volledig geautomatiseerd via Python scripts en wordt als volgt uitgevoerd:

1.  **Archivering**: `archive_old_content()` verplaatst de inhoud van de vorige run uit de `content` map naar de `archive` map.
2.  **Setup**: Maakt nieuwe mappen met tijdstempels aan in `content/newsletters` en `content/longreads` voor de huidige run.
3.  **Data Fetching**: `fetch.py` haalt ruwe data op.
4.  **Curatie**: `curate.py` verwerkt de ruwe data naar een `curated.json` bestand.
5.  **Drafting**: `draft.py` genereert nieuwsbrieven op basis van de gecureerde data.
6.  **Topic Selectie**: `select_topic.py` kiest een onderwerp voor de longread, waarbij `last_topics.json` wordt gebruikt om herhaling te voorkomen.
7.  **Outline Generatie**: `generate_longread_outline.py` maakt een outline voor de longread.
8.  **Longread Generatie**: `generate_longread.py` schrijft het volledige artikel in meerdere talen.
9.  **Social Media Posts**: `generate_social_posts.py` maakt posts voor sociale media.

Dit proces is ontworpen om één volledige "run" aan content te genereren.

## 2. Antwoorden op de Kernvragen (Initiële Analyse)

-   **(2) Nettere repo**: De repo kan netter door de Python-scripts, configuratiebestanden en de Hugo-site duidelijker van elkaar te scheiden. Een `scripts` of `pipeline` map in plaats van `src` zou duidelijker kunnen zijn. De output-bestanden (`raw.json`, `curated.json`, etc.) zouden in een `output` of `build` map kunnen staan die in `.gitignore` staat.
-   **(3) Maandelijkse contentcreatie**: Het `run_pipeline.py` script is de sleutel. Dit script moet zo aangepast of aangeroepen worden dat het slechts één keer per maand draait. Dit is een proces/workflow vraag (bv. via een cron job of GitHub Action) en geen code-aanpassing in de pijplijn zelf.
-   **(4) Voorkomen van herhaling**: Het script `select_topic.py` leest een `last_topics.json` bestand waarin de titels van de laatste twee longreads worden bijgehouden. De AI wordt geïnstrueerd om een ander onderwerp te kiezen. Dit is een eenvoudig maar effectief mechanisme.
-   **(5 & 6) Controle en locatie van content**: Nieuwe content staat in `content/` in een map met een tijdstempel. Oude content wordt verplaatst naar `archive/`. De **enige** content die live op de site staat, is de content die op dat moment in `content/` staat. Controle uitoefenen betekent dus bepalen welke bestanden in de `content` map blijven staan wanneer Hugo de site bouwt.
-   **(7) Controle over preview-lengte**: De lengte van de samenvattingen op de homepage wordt waarschijnlijk bepaald door `layouts/partials/summary.html` of `themes/ananke/layouts/partials/summary.html`. Hugo's `.Summary` functie wordt hier gebruikt. De lengte kan aangepast worden door de configuratie (`summaryLength` in `hugo.toml`) of door het template aan te passen om expliciet te 'truncaten'.
-   **(8) Uiterlijk**: Het uiterlijk wordt volledig beheerd door het Ananke-thema (`themes/ananke`). Verbeteringen kunnen worden doorgevoerd door de CSS van het thema aan te passen, of door een compleet nieuw thema te kiezen en te configureren.
-   **(9) Volledige archief aanbieden**: Hugo toont het archief niet omdat de bestanden fysiek uit de `content` map worden verplaatst. Om het hele archief te tonen, moet de workflow worden aangepast. In plaats van bestanden te verplaatsen, zouden we een `status` (bv. `published`, `archived`) in de front matter van de markdown-bestanden kunnen gebruiken. Zo blijven alle bestanden in de `content` map en kan Hugo ze allemaal verwerken. We kunnen dan archiefpagina's maken die filteren op deze status.

## 3. Strategie

De volgende stappen zijn nodig om de wensen van de gebruiker te realiseren:

1.  **Rapportage**: Schrijf een gedetailleerde analyse op basis van bovenstaande punten en sla dit op als `analyse_rapport.md`.
2.  **Refactoring & Organisatie**:
    -   Hernoem `src` naar `pipeline`.
    -   Maak een `.gitignore` om output-bestanden (`*.json`, `*.txt`) te negeren.
    -   Pas `run_pipeline.py` aan om output in een `output/` map te schrijven.
3.  **Content Workflow Aanpassen**:
    -   Pas de pijplijn aan: in plaats van bestanden te verplaatsen naar `archive/`, voeg een `status: published` of `status: archived` toe aan de front matter van de content-bestanden. Oudere content krijgt de status `archived`.
    -   Pas de Hugo templates aan:
        -   De homepage (`index.html`) toont alleen content met `status: published`.
        -   Maak een nieuwe archiefpagina (`/archive/`) die alle content toont, of filtert op `status: archived`.
4.  **Design & Layout**:
    -   Analyseer de CSS van het Ananke-thema en identificeer mogelijkheden voor verbetering.
    -   Implementeer aanpassingen aan de preview-lengte in de `summary.html` partial.
5.  **Handleiding**: Schrijf een uitgebreide handleiding (`handleiding.md`) die alle nieuwe processen en workflows uitlegt voor de contentmanager.
