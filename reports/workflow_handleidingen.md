# Handleiding GitHub Workflows

Dit document beschrijft de verschillende geautomatiseerde workflows die worden gebruikt voor de Vegan BioTech Report website.

---

## 1. Auto Generate and Deploy

-   **Workflow-bestand:** `1-auto-generate-and-deploy.yml`
-   **Doel:** De volledige automatische cyclus: content genereren, opslaan en de site publiceren.
-   **Hoe te starten:** Handmatig via het "Actions" tabblad of automatisch via een schema (indien geactiveerd).
-   **Wat het doet:** Voert de volledige pijplijn uit (`run_pipeline.py`), commit de nieuwe content en bouwt/deployt de Hugo site naar GitHub Pages.

---

## 2. Generate Only

-   **Workflow-bestand:** `2-generate-only.yml`
-   **Doel:** Alleen nieuwe content genereren zonder de site direct te publiceren.
-   **Wat het doet:** Handig voor het voorbereiden van content die je eerst wilt controleren.

---

## 3. Fill Missing Images

-   **Workflow-bestand:** `3-image-gen-only.yml`
-   **Doel:** Scant de content mappen op artikelen die nog geen afbeelding hebben en genereert deze alsnog, zonder build & deploy.

---

## 4. Build and Deploy (No Content Generation)

-   **Workflow-bestand:** `4-build-and-deploy-no-content-generation.yml`
-   **Doel:** De website opnieuw publiceren op basis van de huidige bestanden in de repository.
-   **Wanneer te gebruiken:** Na handmatige aanpassingen aan de lay-out of CSS, of na het archiveren van artikelen.

---

## 5. Manage Content Status

-   **Workflow-bestand:** `5-manage-content-status.yml`
-   **Doel:** De status van artikelen wijzigen (live of gearchiveerd).
-   **Hoe te starten:** Handmatig via Actions. Er verschijnt een formulier om acties en bestanden te selecteren.

---

## 6. View Content Status

-   **Workflow-bestand:** `6-view-content-status.yml`
-   **Doel:** Een overzicht genereren in de logs van welke artikelen momenteel live staan of gearchiveerd zijn.
