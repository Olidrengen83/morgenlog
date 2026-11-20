# ForældreIntra → kalender

Logger ind på ForældreIntra med ét login, går igennem hver af børnenes
indgange og læser forside, opslag, beskeder, ugeplaner og kalender, og lader Claude
plukke det ud, der skal i kalenderen:

- fridage og ferier
- arrangementer, forældremøder, udflugter
- **frister** (tilmelding, betaling, svar) – får en påmindelse kl. 18 dagen før
- **medbring**-dage (madpakke, regntøj, gymnastiktøj …)
- aflysninger (begivenheden fjernes eller markeres AFLYST)

Resultatet lander tre steder:

| Output | Hvad |
|---|---|
| `output/<barn>.ics` + `output/alle-boern.ics` | Kalenderfiler, kan importeres i alle kalendere |
| Google Kalender (valgfrit) | Synkroniseres direkte; samme begivenhed opdateres i stedet for at blive dubleret |
| `output/oversigt.md` | De næste 14 dage pr. barn + vigtige beskeder uden dato |

Kun nye eller ændrede sider sendes til Claude, så hver kørsel efter den
første koster meget lidt.

## Sådan virker den

1. **Ét login med en rigtig browser** (Playwright/Chromium). Den finder selv
   brugernavn-/adgangskodefelterne og vælger rollen *Forælder* hvis siden spørger.
2. **Barnevælgeren**: den finder hvert barns indgang (`/parent/<id>/<navn>/…`)
   ud fra navnet og holder børnenes sider adskilt.
3. **Crawl pr. barn**: menupunkter med ord som *opslag, besked, kalender,
   ugeplan, tilmelding, arrangement* – og derfra de enkelte opslag/beskeder.
   Log ud, filer og indstillinger springes over.
4. **Fælles sider** (fx indbakken, som er den samme for alle tre) behandles kun
   én gang og lander som *[Fælles]*, så "fri 23/12" ikke står der tre gange.
5. **Claude** får teksten + listen over allerede kendte begivenheder og
   returnerer struktureret JSON (dato, tid, kategori, hvad skal I gøre).
   Relative datoer som "på torsdag" eller "uge 48" løses ud fra dagens dato.
6. **Lager** i `state/state.json` holder styr på sete sider og begivenheder.

## Opsætning lokalt

```bash
cd foraeldreintra
pip install -r requirements.txt
python -m playwright install chromium

cp config.example.yaml config.yaml   # ret navne, skoleadresser og login-type
export ANTHROPIC_API_KEY=...
export FI_USER=... FI_PASS=...      # dit ForældreIntra-login

# 1) Tjek at login og crawl virker – kalder hverken Claude eller Google
python fetcher.py --dry-run --debug

# 2) Rigtig kørsel
python fetcher.py
```

Går login galt, ligger der et skærmbillede og HTML i `debug/` (kun med `--debug`).
Findes et barn ikke, så sæt `match:` til navnet præcis som i barnevælgeren
(der gemmes også et skærmbillede i `debug/`). Brug `--only Barn2` for at køre ét barn, og `--force` for at genbehandle alt.

Finder den ikke en bestemt side (fx kalenderen), så kopiér adressen fra
browseren ind under `extra_urls` for barnet.

## Din private Google Kalender

Fetcheren skriver selv i kalenderen via en lille "robot-konto" (servicekonto),
så det er uafhængigt af, hvilke kalendere Claude-appen har adgang til. Logget
ind med din **private** Google-konto:

1. Gå til <https://console.cloud.google.com/> → opret et projekt (fx "skolekalender").
2. *APIs & Services → Library* → søg **Google Calendar API** → *Enable*.
3. *IAM & Admin → Service Accounts → Create service account* (intet rolle-valg
   nødvendigt) → åbn den → *Keys → Add key → JSON*. Filen downloades.
4. I Google Kalender: opret en ny kalender, fx **"Skole"** (anbefalet, så
   robotten ikke kan røre resten af din kalender) → *Indstillinger og deling* →
   *Del med bestemte personer* → indsæt servicekontoens e-mail
   (`…@….iam.gserviceaccount.com`) med *Foretag ændringer i begivenheder*.
5. Under *Integrer kalender* på samme side står **Kalender-id** – sæt det i
   `google_calendar.calendar_id` og `enabled: true` i `config.yaml`.
6. `export GOOGLE_SERVICE_ACCOUNT_JSON="$(cat nøgle.json)"`

Vil du have en kalender pr. barn, så sæt `calendar_id` på hvert barn i stedet –
så slipper titlerne for `[Navn]` foran.

## Automatisk to gange dagligt (GitHub Actions)

`.github/workflows/foraeldreintra.yml` kører ca. kl. 06 og 14. Læg disse under
*Settings → Secrets and variables → Actions*:

| Secret | Indhold |
|---|---|
| `FORAELDREINTRA_CONFIG` | Hele indholdet af din `config.yaml` (så navne og skoler ikke står i repoet) |
| `ANTHROPIC_API_KEY` | Din Claude API-nøgle |
| `FI_USER` / `FI_PASS` | Dit ForældreIntra-login |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Kun hvis du bruger Google Kalender |

Tilstanden gemmes i Actions-cachen mellem kørsler. Der uploades ingen filer
med børnenes data som artefakter – Google Kalender er vejen ud derfra.
Workflowet kan også startes manuelt (*Run workflow*).

## Begrænsninger

- Skolernes sider kunne ikke nås fra det miljø, hvor dette blev bygget, så
  login og crawl er testet mod en lokal efterligning af ForældreIntra – ikke
  mod en rigtig skole. Kør `--dry-run --debug` først.
- MitID-login understøttes ikke (kræver telefonen). ForældreIntra-login med
  brugernavn/adgangskode virker (UniLogin kan slås til med `login: unilogin`).
- Vedhæftede PDF'er (fx ugeplaner som PDF) læses ikke endnu.
