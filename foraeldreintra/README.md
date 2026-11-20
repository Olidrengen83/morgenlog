# ForældreIntra → kalender

Logger ind på ForældreIntra for hvert af børnene (én indgang pr. barn),
læser forside, opslag, beskeder, ugeplaner og kalender, og lader Claude
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

1. **Login med en rigtig browser** (Playwright/Chromium). Den finder selv
   brugernavn-/adgangskodefelterne, vælger rollen *Forælder* hvis siden spørger,
   og understøtter både almindeligt ForældreIntra-login og UniLogin.
2. **Crawl**: fra forsiden følges menupunkter med ord som *opslag, besked,
   kalender, ugeplan, tilmelding, arrangement* – og derfra de enkelte
   opslag/beskeder. Log ud, filer og indstillinger springes over.
3. **Claude** får teksten + listen over allerede kendte begivenheder og
   returnerer struktureret JSON (dato, tid, kategori, hvad skal I gøre).
   Relative datoer som "på torsdag" eller "uge 48" løses ud fra dagens dato.
4. **Lager** i `state/state.json` holder styr på sete sider og begivenheder.

## Opsætning lokalt

```bash
cd foraeldreintra
pip install -r requirements.txt
python -m playwright install chromium

cp config.example.yaml config.yaml   # ret navne, skoleadresser og login-type
export ANTHROPIC_API_KEY=...
export FI_BARN1_USER=... FI_BARN1_PASS=...
export FI_BARN2_USER=... FI_BARN2_PASS=...
export FI_BARN3_USER=... FI_BARN3_PASS=...

# 1) Tjek at login og crawl virker – kalder hverken Claude eller Google
python fetcher.py --dry-run --debug

# 2) Rigtig kørsel
python fetcher.py
```

Går login galt, ligger der et skærmbillede og HTML i `debug/` (kun med `--debug`).
Brug `--only Barn2` for at køre ét barn, og `--force` for at genbehandle alt.

Finder den ikke en bestemt side (fx kalenderen), så kopiér adressen fra
browseren ind under `extra_urls` for barnet.

## Google Kalender (valgfrit)

1. Opret et projekt i Google Cloud Console, slå **Google Calendar API** til.
2. Opret en **servicekonto**, lav en JSON-nøgle.
3. Lav en kalender (fx "Skole") i Google Kalender → *Indstillinger og deling* →
   del den med servicekontoens e-mail med rettigheden *Foretag ændringer i begivenheder*.
4. Sæt `google_calendar.enabled: true` og `calendar_id` (findes under
   *Integrer kalender*) i `config.yaml`.
5. `export GOOGLE_SERVICE_ACCOUNT_JSON="$(cat nøgle.json)"`

Vil du have en kalender pr. barn, så sæt `calendar_id` på hvert barn i stedet –
så slipper titlerne for `[Navn]` foran.

## Automatisk to gange dagligt (GitHub Actions)

`.github/workflows/foraeldreintra.yml` kører ca. kl. 06 og 14. Læg disse under
*Settings → Secrets and variables → Actions*:

| Secret | Indhold |
|---|---|
| `FORAELDREINTRA_CONFIG` | Hele indholdet af din `config.yaml` (så navne og skoler ikke står i repoet) |
| `ANTHROPIC_API_KEY` | Din Claude API-nøgle |
| `FI_BARN1_USER` / `FI_BARN1_PASS` … `FI_BARN3_*` | Login til hver indgang |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Kun hvis du bruger Google Kalender |

Tilstanden gemmes i Actions-cachen mellem kørsler. Der uploades ingen filer
med børnenes data som artefakter – Google Kalender er vejen ud derfra.
Workflowet kan også startes manuelt (*Run workflow*).

## Begrænsninger

- Skolernes sider kunne ikke nås fra det miljø, hvor dette blev bygget, så
  login og crawl er testet mod en lokal efterligning af ForældreIntra – ikke
  mod en rigtig skole. Kør `--dry-run --debug` først.
- MitID-login understøttes ikke (kræver telefonen). ForældreIntra-login og
  UniLogin med brugernavn/adgangskode virker.
- Vedhæftede PDF'er (fx ugeplaner som PDF) læses ikke endnu.
