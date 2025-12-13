# 🤖 Vegan BioTech Report - Workflow Handleiding

Hier is een overzicht van de automatische processen (Workflows) in dit project en wanneer je ze moet gebruiken.

 Je vindt deze onder het tabblad **Actions** in GitHub.

---

## 1. [AUTO] Generate Content & Deploy
**Bestandsnaam:** `1-auto-generate-and-deploy.yml`

✅ **GEBRUIK DIT VOOR:**
*   Het automatische proces: nieuwe content genereren (nieuwsbrief + longread) + website updaten.
*   **Dit is de hoofdknop.** Als je "gewoon wilt dat er iets gebeurt", gebruik je deze.

**Wat het doet:**
1.  Verzamelt biotech nieuws.
2.  Schrijft een nieuwsbrief en een longread.
3.  Genereert afbeeldingen (via Google Gemini).
4.  Bouwt de website en pusht hem live.

---

## 2. [MANUAL] Run Pipeline Only
**Bestandsnaam:** `2-generate-only.yml`

✅ **GEBRUIK DIT VOOR:**
*   **Testen & Reviewen.**
*   Als je nieuwe content wilt genereren *zonder* dat deze direct online gaat.
*   Je kunt de content dan eerst controleren in de repository.

**Wat het doet:**
*   Draait alle scripts (tekst + beeld).
*   Commit de bestanden naar de repo.
*   **Deploys NIET** naar de live website.

---

## 3. [MANUAL] Fill Missing Images Only
**Bestandsnaam:** `3-images-only.yml`

✅ **GEBRUIK DIT VOOR:**
*   Als je een artikel hebt (handmatig of automatisch) dat nog geen coverafbeelding heeft.
*   Als een eerdere run faalde tijdens het genereren van afbeeldingen.

**Wat het doet:**
*   Scant alle content mappen.
*   Zoekt naar artikelen zonder afbeelding.
*   Genereert *alleen* de ontbrekende afbeeldingen.
*   Past de tekst van het artikel **niet** aan.

---

## 4. [MANUAL] Deploy Site Only
**Bestandsnaam:** `4-build-and-deploy-no-content-generation.yml`

✅ **GEBRUIK DIT VOOR:**
*   Als je **handmatig** wijzigingen hebt gedaan in de code of tekst (bijvoorbeeld een typfout verbeterd in een `.md` bestand via de GitHub editor).
*   Als je wilt dat die handmatige wijzigingen zichtbaar worden op de live website.

**Wat het doet:**
*   Slaat het genereren van content over.
*   Bouwt alleen de Hugo website en publiceert deze.

---

## 5. [UTIL] Manage Content Status
**Bestandsnaam:** `5-manage-content-status.yml`

✅ **GEBRUIK DIT VOOR:**
*   Het opruimen van de homepage.
*   Het "archiveren" van oude artikelen (zodat ze niet meer op de voorpagina staan) door `archived: true` in de frontmatter te zetten.
*   Het terugzetten van gearchiveerde artikelen.

**Opties:**
*   `archive-live-content`: Haalt alles van de voorpagina af (zet op gearchiveerd).
*   `unarchive-latest-content`: Zet de laatste batch weer terug op live.
*   `set-specific-files-archived`: Archiveer specifieke bestanden. Vul bij het veld **Files** de paden in.
*   `set-specific-files-live`: Zet specifieke bestanden weer live.

---

## 6. [UTIL] View Content Status
**Bestandsnaam:** `6-view-content-status.yml`

✅ **GEBRUIK DIT VOOR:**
*   Checken welke artikelen nu "LIVE" zijn en welke "ARCHIVED".
*   Handig om te kijken wat de status van je content is zonder iets te wijzigen.

