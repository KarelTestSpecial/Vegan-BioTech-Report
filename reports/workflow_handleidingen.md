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
-   **Hoe te starten:** Deze workflow moet handmatig worden gestart. Bij het starten verschijnt een formulier met keuzes om content te archiveren of live te zetten.
-   **Wat het doet:** Op basis van de gekozen actie wordt het `manage_content.py` script uitgevoerd om de front matter (`archived: true/false`) in de betreffende Markdown-bestanden aan te passen. De wijzigingen worden automatisch gecommit.

---

## 3. Run Content Pipeline

-   **Workflow-bestand:** `run-content-pipeline.yml`
-   **Doel:** Start **handmatig** het proces voor het genereren van een nieuwe set content (nieuwsbrieven en longreads).
-   **Hoe te starten:** Deze workflow kan op elk gewenst moment handmatig worden gestart via het Actions-tabblad.
-   **Wat het doet:** De workflow voert de volledige `pipeline/run_pipeline.py` uit. De nieuw gegenereerde content wordt automatisch opgeslagen in de repository. **Let op:** deze workflow publiceert de site *niet* opnieuw. De nieuwe content wordt pas zichtbaar nadat de "Deploy" workflow is uitgevoerd.

---

## 4. Deploy Hugo Site to Pages

-   **Workflow-bestand:** `deploy.yml`
-   **Doel:** Publiceert de huidige staat van de website naar GitHub Pages.
-   **Hoe te starten:**
    -   **Automatisch:** Start na elke push naar de `main` branch.
    -   **Handmatig:** Kan ook handmatig worden gestart.
-   **Wat het doet:** De workflow bouwt de Hugo-website en implementeert het resultaat op GitHub Pages. Dit is de workflow die ervoor zorgt dat wijzigingen (nieuwe content, status-updates) daadwerkelijk online zichtbaar worden.

---

## 5. Monthly Content Generation and Deploy

-   **Workflow-bestand:** `monthly.yml`
-   **Doel:** Een volledig **geautomatiseerde, maandelijkse cyclus** van contentcreatie en publicatie. Dit is de primaire workflow voor het onderhouden van de site.
-   **Hoe te starten:**
    -   **Automatisch:** Draait op de eerste dag van elke maand om 03:00 UTC.
    -   **Handmatig:** Kan ook handmatig worden gestart.
-   **Wat het doet:** Dit is een gecombineerde workflow die de volgende stappen uitvoert:
    1.  **Genereert content:** Voert de volledige content generatie pijplijn uit.
    2.  **Commit content:** Slaat de nieuwe artikelen op in de `main` branch.
    3.  **Bouwt en deployt de site:** Publiceert de bijgewerkte site, inclusief de nieuwe content, direct naar GitHub Pages.
    4.  **Verstuurt een notificatie:** Stuurt een e-mail om te laten weten of de workflow succesvol was.

---

## Overige Workflows

### pages-build-deployment

Je zult deze workflow in de lijst zien, maar je kunt hem niet handmatig starten. Dit is normaal.

-   **Doel:** Dit is een **interne, automatische workflow van GitHub zelf**. Het is de allerlaatste stap in het publicatieproces van de website.
-   **Hoe het start:** Deze workflow wordt automatisch door GitHub geactiveerd zodra een van onze andere workflows (zoals "Deploy Hugo Site to Pages" of "Monthly Content Generation") een nieuwe versie van de website heeft gebouwd en aanbiedt voor publicatie.
-   **Wat het doet:** Het pakt de door ons voorbereide websitebestanden en zet deze daadwerkelijk live op de server van GitHub Pages. Je kunt het zien als de 'bezorgdienst' van GitHub die de site aflevert.

### Wat is het verschil tussen "Run Content Pipeline" en "Monthly Content Generation"?

-   **Run Content Pipeline** is voor **handmatige** acties. Het genereert alleen de bestanden, maar zet ze niet live. Dit is handig als je content wilt genereren en controleren *voordat* het gepubliceerd wordt.
-   **Monthly Content Generation and Deploy** is de **volledig geautomatiseerde** workflow. Het genereert de content én publiceert deze onmiddellijk. Dit is de "set-and-forget" workflow die de site maandelijks van nieuwe inhoud voorziet.
