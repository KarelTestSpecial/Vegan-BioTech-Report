# Handleiding GitHub Workflows

Dit document beschrijft de verschillende geautomatiseerde workflows die worden gebruikt voor de Vegan BioTech Report website.

---

## 1. Show Content Status

-   **Workflow-bestand:** `view-status.yml`
-   **Doel:** Geeft een overzicht van alle content (nieuwsbrieven, longreads) en hun huidige status: `live` (zichtbaar op de site) of `archived` (gearchiveerd).
-   **Hoe te starten:** Deze workflow moet handmatig worden gestart via het "Actions" tabblad op GitHub.
-   **Wat het doet:** De workflow voert het Python-script `manage_content.py status` uit, dat de status van alle bestanden in de `content` map uitleest en in de logs van de workflow-run weergeeft.

---

## 2. Manage Content Status

-   **Workflow-bestand:** `manage-content.yml`
-   **Doel:** Maakt het mogelijk om de status van content te wijzigen. Hiermee bepaal je welke artikelen live staan en welke gearchiveerd zijn.
-   **Hoe te starten:** Deze workflow moet handmatig worden gestart. Bij het starten verschijnt een formulier met de volgende keuzes:
    -   `archive-live-content`: Zet alle huidige live content op 'archived'.
    -   `unarchive-latest-content`: Zet de meest recent gearchiveerde content op 'live'.
    -   `set-specific-files-archived`: Archiveert specifieke bestanden (je moet de volledige paden naar de bestanden opgeven).
    -   `set-specific-files-live`: Zet specifieke gearchiveerde bestanden op 'live'.
-   **Wat het doet:** Op basis van de gekozen actie wordt het `manage_content.py` script uitgevoerd om de front matter (`archived: true/false`) in de betreffende Markdown-bestanden aan te passen. De wijzigingen worden automatisch gecommit en naar de `main` branch gepusht.

---

## 3. Run Content Pipeline

-   **Workflow-bestand:** `run-content-pipeline.yml`
-   **Doel:** Start het volledige proces voor het genereren van nieuwe content (nieuwsbrieven en longreads).
-   **Hoe te starten:** Deze workflow kan handmatig worden gestart.
-   **Wat het doet:** De workflow installeert de benodigde Python-packages en voert vervolgens de volledige `pipeline/run_pipeline.py` uit. Dit script doorloopt alle stappen, van het ophalen van nieuws tot het schrijven van de uiteindelijke artikelen. De nieuw gegenereerde content wordt automatisch gecommit en gepusht naar de `main` branch.

---

## 4. Deploy Hugo Site to Pages

-   **Workflow-bestand:** `deploy.yml`
-   **Doel:** Publiceert de website naar GitHub Pages, waardoor deze publiek zichtbaar wordt.
-   **Hoe te starten:**
    -   **Automatisch:** Deze workflow wordt automatisch gestart na elke push naar de `main` branch (bijvoorbeeld nadat nieuwe content is gegenereerd of de status is aangepast).
    -   **Handmatig:** Kan ook handmatig worden gestart.
-   **Wat het doet:** De workflow bouwt de Hugo-website met de "extended" versie van Hugo. Het resultaat is een statische website in de `public` map. Vervolgens wordt de inhoud van deze map geïmplementeerd op GitHub Pages. De term `pages-build-deployment` die je op de Actions-pagina ziet, is de naam van de specifieke deploy-stap binnen deze workflow.

---

## 5. Weekly Content Generation and Deploy

-   **Workflow-bestand:** `weekly.yml`
-   **Doel:** Een volledig geautomatiseerde, wekelijkse cyclus van contentcreatie en publicatie.
-   **Hoe te starten:**
    -   **Automatisch:** Draait elke maandagochtend om 03:05 UTC. De workflow draait echter alleen inhoudelijk als het een **even weeknummer** is.
    -   **Handmatig:** Kan op elk moment handmatig worden gestart.
-   **Wat het doet:** Dit is een gecombineerde workflow die de volgende stappen uitvoert:
    1.  **Controleert de week:** Bepaalt of het een even week is. Zo niet, dan stopt de geplande run.
    2.  **Genereert content:** Voert de volledige content generatie pijplijn uit, net als de "Run Content Pipeline" workflow.
    3.  **Commit content:** Slaat de nieuwe artikelen op in de `main` branch.
    4.  **Bouwt en deployt de site:** Publiceert de bijgewerkte site naar GitHub Pages.
    5.  **Verstuurt een notificatie:** Stuurt een e-mail om te laten weten of de workflow succesvol was of niet.
