# Instructies voor de volgende sessie

We hebben een harde reset uitgevoerd naar commit `96be2e6` om een reeks mislukte UI-aanpassingen ongedaan te maken.

**De Huidige Status:**
- De website werkt, de navigatiepijltjes ("«" en "»") staan correct bovenaan de artikelen.
- Er is GEEN `min-height` ingesteld op headers.

**Het Probleem:**
- Bij het navigeren tussen artikelen verspringt de hoogte van de 'Hero Header' (de grote afbeelding met titel bovenaan de pagina) omdat de titellengte varieert.

**De Opdracht:**
1.  Geef de **Site Header** (de hero sectie met de achtergrondafbeelding) een vaste minimale hoogte van **633px**.
    - Dit betreft waarschijnlijk `themes/ananke/layouts/partials/site-header.html`.
    - **BELANGRIJK:** Maak een lokale kopie in `layouts/partials/site-header.html` om dit te overriden (als die nog niet bestaat na de reset).
    - Pas de `min-height` toe op zowel de `<header>` tag als de innerlijke `<div>` (die de donkere overlay bevat), zodat de achtergrond en overlay consistent zijn.
2.  Blijf AF van `layouts/_default/single.html` voor wat betreft header-hoogtes. De fout in de vorige sessie was dat de `min-height` op de *artikel-tekst-header* werd gezet in plaats van de *site-hero-header*.

**Context:**
De vorige pogingen faalden omdat:
1. Eerst de verkeerde header (`<header>` binnen `<article>`) werd aangepast, wat witruimte creëerde.
2. Daarna de juiste header werd aangepast, maar de code rommelig werd door de vele correcties.
We beginnen nu met een schone lei vanaf het punt dat de pijltjes goed stonden.

dit is een voorbeeld van de juiste header :
<body class="ma0 avenir bg-near-white production"><header class="cover bg-center" style="background-image:url(https://kareltestspecial.github.io/Vegan-BioTech-Report/images/air_protein.png)" style="min-height:666px">

dit is een voorbeeld van de foute header :

<main class="pb7" role="main"><article class="flex-l mw8 center ph3 flex-wrap justify-between"><header class="mt4 w-100" style="min-height:666px"><div class="flex justify-between items-center mb4">

