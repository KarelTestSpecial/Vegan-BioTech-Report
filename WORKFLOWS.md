# 🤖 Vegan BioTech Report - Workflow Handleiding

Hier is een overzicht van de automatische processen (Workflows) in dit project en wanneer je ze moet gebruiken.

 Je vindt deze onder het tabblad **Actions** in GitHub.

---

## 1. [AUTO] Generate Content & Deploy
**Bestandsnaam:** `1-auto-generate-and-deploy.yml`

✅ **GEBRUIK DIT VOOR:**
*   Het genereren van nieuwe content (nieuwsbrief + longread).
*   Het updaten van de website met nieuwe artikelen.
*   **Dit is de hoofdknop.** Als je "gewoon wilt dat er iets gebeurt", gebruik je deze.

**Wat het doet:**
1.  Verzamelt biotech nieuws.
2.  Schrijft een nieuwsbrief en een longread.
3.  Genereert afbeeldingen (via Pollinations.ai).
4.  Bouwt de website en zet hem online.

---

## 2. [MANUAL] Deploy Site Only
**Bestandsnaam:** `2-manual-deploy.yml`

✅ **GEBRUIK DIT VOOR:**
*   Als je **handmatig** wijzigingen hebt gedaan in de code of tekst (bijvoorbeeld een typfout verbeterd in een `.md` bestand via de GitHub editor).
*   Als je wilt dat die handmatige wijzigingen zichtbaar worden op de live website.

**Wat het doet:**
*   Slaat het genereren van content over.
*   Bouwt alleen de Hugo website en publiceert deze.

---

## 3. [UTIL] Manage Content
**Bestandsnaam:** `3-manage-content.yml`

✅ **GEBRUIK DIT VOOR:**
*   Het opruimen van de homepage.
*   Het "archiveren" van oude artikelen (zodat ze niet meer op de voorpagina staan).
*   Het terugzetten van gearchiveerde artikelen.

**Opties:**
*   `archive-live-content`: Haalt alles van de voorpagina af.
*   `unarchive-latest-content`: Zet de laatste batch weer terug.

---

## 4. [UTIL] View Content Status
**Bestandsnaam:** `4-view-status.yml`

✅ **GEBRUIK DIT VOOR:**
*   Checken welke artikelen nu "LIVE" zijn en welke "ARCHIVED".
*   Handig om te kijken wat er in de database staat zonder iets te wijzigen.

---

## 5. [DEBUG] Run Pipeline Only
**Bestandsnaam:** `5-debug-pipeline-only.yml`

✅ **GEBRUIK DIT VOOR:**
*   **Testen.**
*   Als je wilt zien of de AI scripts werken zonder dat je de website meteen aanpast.
*   Genereert wel bestanden in de repository, maar publiceert de site **niet** opnieuw.
