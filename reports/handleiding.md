# Handleiding voor de Contentmanager - Vegan BioTech Report

Welkom bij de handleiding voor het beheren van de Vegan BioTech Report website. Dit document legt de belangrijkste taken uit die je als contentmanager zult uitvoeren.

## Inhoudsopgave
1.  De Maandelijkse Workflow: Een Overzicht
2.  Content Genereren: De Pijplijn Draaien
3.  Content Beheren: Bepalen wat Live Staat
4.  Afbeeldingen Toevoegen aan Artikelen
5.  De Website Publiceren

---

## 1. De Maandelijkse Workflow: Een Overzicht

De workflow is ontworpen om zo eenvoudig mogelijk te zijn. Elke maand doorloop je de volgende stappen:

1.  **Content Genereren:** Je start een geautomatiseerd proces dat een nieuwe set content (nieuwsbrieven en een longread) voor je aanmaakt.
2.  **Content Beheren:** De nieuw aangemaakte content staat nu "live". De vorige live content wordt automatisch gearchiveerd. Via een interface in GitHub kun je de status van elk artikel handmatig aanpassen.
3.  **Optioneel: Verrijken:** Je kunt de gegenereerde artikelen handmatig verrijken met afbeeldingen.
4.  **Publiceren:** De wijzigingen worden automatisch doorgevoerd op de live website.

## 2. Content Genereren: De Pijplijn Draaien

De content wordt automatisch gegenereerd door een script. Om dit proces te starten:

1.  Ga naar de GitHub repository en klik op het tabblad **"Actions"**.
2.  Aan de linkerkant zie je een lijst met "workflows". Klik op **"RUN CONTENT PIPELINE"**.
3.  Klik op de "Run workflow" knop. Het proces zal nu op de achtergrond de nieuwste content voor je genereren. Dit kan enkele minuten duren.

Wanneer dit proces is voltooid, is de nieuwe content aangemaakt en staat deze automatisch "live" op de website. De content die voorheen live was, is nu automatisch gearchiveerd.

## 3. Content Beheren: Bepalen wat Live Staat

Je hebt de volledige controle over welke artikelen op de homepage verschijnen (live) en welke alleen in het archief te vinden zijn. Dit beheer je volledig via een interface in GitHub.

De workflow bestaat uit 3 simpele stappen: **Kijken, Kopiëren, en Aanpassen**.

### Stap 1: Kijken - De status van alle content bekijken

1.  Ga naar het **"Actions"** tabblad in GitHub.
2.  Klik aan de linkerkant op de workflow **"1. Show Content Status"**.
3.  Klik op de "Run workflow" knop.
4.  Klik op de voltooide run om het logboek te openen. Je ziet nu een volledige lijst van alle content, met de status `[LIVE]` of `[ARCHIVED]` en het volledige pad naar het bestand.

### Stap 2: Kopiëren - Selecteer de bestanden die je wilt aanpassen

1.  Selecteer en kopieer het volledige pad van de bestanden die je wilt wijzigen uit de lijst van de vorige stap.
2.  Je kunt meerdere bestanden kopiëren. Plak ze tijdelijk in een teksteditor en zorg ervoor dat ze gescheiden zijn door een **spatie**.

**Voorbeeld:**
`content/newsletters/2025-12-05.../nl.md content/longreads/2025-11-01.../en.md`

### Stap 3: Aanpassen - De status van de geselecteerde bestanden wijzigen

1.  Ga terug naar het **"Actions"** tabblad.
2.  Klik nu op de workflow **"2. Manage Content Status"**.
3.  Klik op "Run workflow". Er verschijnt nu een formulier.
4.  **Action:** Kies uit de dropdown wat je wilt doen.
    - `set-specific-files-live`: Maak de geselecteerde bestanden live.
    - `set-specific-files-archived`: Archiveer de geselecteerde bestanden.
    - `archive-live-content`: Archiveer *alle* live content in één keer.
5.  **Files:** Plak de gekopieerde bestandsnamen in dit tekstveld.
6.  Klik op de groene "Run workflow" knop om de wijziging door te voeren. De wijzigingen worden automatisch opgeslagen.

## 4. Afbeeldingen Toevoegen aan Artikelen

De gegenereerde artikelen bevatten geen afbeeldingen. Je kunt deze eenvoudig handmatig toevoegen.

1.  **Vind het juiste artikel:** Navigeer in de `content/longreads` of `content/newsletters` map naar de map van het artikel dat je wilt aanpassen.
2.  **Upload de afbeelding:** Upload je afbeelding (bv. `mijn-afbeelding.jpg`) in dezelfde map als het `.md` bestand van het artikel.
3.  **Voeg de afbeelding toe in de tekst:** Open het `.md` bestand en voeg de volgende Markdown-code toe op de plek waar je de afbeelding wilt hebben:
    `![Een beschrijving van mijn afbeelding](./mijn-afbeelding.jpg)`

## 5. De Website Publiceren

De website wordt gehost via GitHub Pages. Dit betekent dat **elke wijziging die wordt opgeslagen in de `main` branch automatisch wordt gepubliceerd**.

Zowel het draaien van de content-pijplijn als het beheren van de content via de GitHub Action slaan hun wijzigingen automatisch op. Je hoeft dus **geen aparte publicatiestap** te ondernemen.
