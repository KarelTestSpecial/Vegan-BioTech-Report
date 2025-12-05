# Handleiding voor de Contentmanager - Vegan BioTech Report

Welkom bij de handleiding voor het beheren van de Vegan BioTech Report website. Dit document legt de belangrijkste taken uit die je als contentmanager zult uitvoeren.

## Inhoudsopgave
1.  De Maandelijkse Workflow: Een Overzicht
2.  Stap 1: Nieuwe Content Genereren
3.  Stap 2: Content Beheren (Archiveren en Live Zetten)
4.  Optioneel: Afbeeldingen Toevoegen aan Artikelen
5.  De Website Publiceren: Hoe het Werkt

---

## 1. De Maandelijkse Workflow: Een Overzicht

De workflow is ontworpen om je volledige controle te geven. Elke maand doorloop je de volgende stappen:

1.  **Content Genereren:** Je start handmatig een proces dat een nieuwe set content (nieuwsbrieven en een longread) voor je aanmaakt. Deze nieuwe content staat onmiddellijk "live" op de website.
2.  **Content Beheren:** Alle vorige content blijft ook "live" staan. Je kunt nu handmatig, via een interface in GitHub, beslissen welke artikelen je wilt archiveren en welke je live wilt houden.
3.  **Verrijken & Publiceren:** Je kunt de artikelen verrijken met afbeeldingen. Alle wijzigingen worden automatisch gepubliceerd.

## 2. Stap 1: Nieuwe Content Genereren

Het genereren van nieuwe content is een **handmatige actie**. Je hebt zelf de controle over wanneer dit gebeurt.

1.  Ga naar de GitHub repository en klik op het tabblad **"Actions"**.
2.  Aan de linkerkant zie je een lijst met workflows. Klik op **"3. Run Content Pipeline"**.
3.  Klik op de "Run workflow" knop aan de rechterkant. Het proces zal nu op de achtergrond de nieuwste content voor je genereren. Dit kan enkele minuten duren.

Wanneer dit proces is voltooid, is de nieuwe content aangemaakt en staat deze automatisch "live" (bovenaan de homepage). **Belangrijk:** Oudere content wordt niet automatisch gearchiveerd.

*(Voor de toekomst: deze actie kan worden geautomatiseerd om bijvoorbeeld elke eerste van de maand te draaien. Dit is momenteel uitgeschakeld om je volledige controle te geven.)*

## 3. Stap 2: Content Beheren (Archiveren en Live Zetten)

Nadat je nieuwe content hebt gegenereerd, wil je misschien oudere artikelen van de homepage halen door ze te archiveren. Dit beheer je volledig via een interface in GitHub.

De workflow bestaat uit 3 simpele stappen: **Kijken, Kopiëren, en Aanpassen**.

### Stap A: Kijken - De status van alle content bekijken

1.  Ga naar het **"Actions"** tabblad in GitHub.
2.  Klik aan de linkerkant op de workflow **"1. Show Content Status"**.
3.  Klik op de "Run workflow" knop.
4.  Klik op de voltooide run om het logboek te openen. Je ziet nu een volledige lijst van alle content, met de status `[LIVE]` of `[ARCHIVED]` en het volledige pad naar het bestand.

### Stap B: Kopiëren - Selecteer de bestanden die je wilt aanpassen

1.  Selecteer en kopieer het volledige pad van de bestanden die je wilt wijzigen uit de lijst van de vorige stap.
2.  Je kunt meerdere bestanden tegelijk aanpassen. Plak de paden in een teksteditor, gescheiden door een **spatie**.

**Voorbeeld:**
`content/newsletters/2025-12-05.../nl.md content/longreads/2025-11-01.../en.md`

### Stap C: Aanpassen - De status van de geselecteerde bestanden wijzigen

1.  Ga terug naar het **"Actions"** tabblad.
2.  Klik nu op de workflow **"2. Manage Content Status"**.
3.  Klik op "Run workflow". Er verschijnt nu een formulier.
4.  **Action:** Kies uit de dropdown wat je wilt doen.
    - `set-specific-files-archived`: Archiveer de geselecteerde bestanden.
    - `set-specific-files-live`: Maak de geselecteerde bestanden weer live.
    - `archive-live-content`: Een handige bulk-actie om *alle* live content in één keer te archiveren.
5.  **Files:** Plak de gekopieerde bestandsnamen in dit tekstveld (niet nodig voor de bulk-actie).
6.  Klik op de groene "Run workflow" knop om de wijziging door te voeren.

## 4. Optioneel: Afbeeldingen Toevoegen aan Artikelen

De gegenereerde artikelen bevatten geen afbeeldingen. Je kunt deze eenvoudig handmatig toevoegen.

1.  **Vind het juiste artikel:** Navigeer in de `content/longreads` of `content/newsletters` map naar de map van het artikel dat je wilt aanpassen.
2.  **Upload de afbeelding:** Upload je afbeelding (bv. `mijn-afbeelding.jpg`) in dezelfde map als het `.md` bestand van het artikel.
3.  **Voeg de afbeelding toe in de tekst:** Open het `.md` bestand en voeg de volgende Markdown-code toe op de plek waar je de afbeelding wilt hebben:
    `![Een beschrijving van mijn afbeelding](./mijn-afbeelding.jpg)`

## 5. De Website Publiceren: Hoe het Werkt

De website wordt gehost via GitHub Pages. Er is een workflow genaamd **"Deploy Hugo Site to Pages"** die dit automatisch voor je doet.

Deze workflow start automatisch telkens wanneer er een wijziging wordt opgeslagen in de `main` branch. Aangezien zowel de content-pijplijn als de management-acties hun wijzigingen automatisch opslaan, hoef je **geen aparte publicatiestap** te ondernemen. De site wordt altijd vanzelf bijgewerkt.
