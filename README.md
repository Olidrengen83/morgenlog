# Morgenlog

En lille træningsdagbog til telefonen: styrke og løb i ét sted, med et samlet
billede af belastning og restitution — og en direkte vej videre til Claude, når
tallene skal fortolkes.

Ren HTML, CSS og JavaScript i én fil. Ingen server, ingen konto, ingen
byggeproces. Alt ligger i telefonens eget lager.

## Hvad appen gør

**I DAG** — parathedsscore (0–100) med den ene ting, det bedst betaler sig at
skrue på lige nu. Morgentjek på tyve sekunder. Dagens pas: styrkeøvelser med
sæt, gentagelser og vægt, eller en løbetur du lægger ind som fil.

**BALANCE** — akut mod kronisk belastning, formkurve, monotoni og strain, og
HRV og søvn tegnet op mod din egen 42-dages basislinje. Alle diagrammer har en
tabel med de samme tal.

**PLAN** — ugens skelet. Byt rundt på dagene, eller vælg bare et andet pas under
I dag; appen regner på det, du faktisk lavede.

**LOG** — hvert pas med load, RPE og parathed den dag.

**CLAUDE** — hele din status som struktureret tekst, klar til at kopiere. Eller,
med en API-nøgle, en samtale inde i appen hvor Claude automatisk får det hele
med.

## Sådan regner den

**Belastning** bruger sRPE-load: `minutter × anstrengelse (1–10)`. Det er den
eneste enhed, der kan lægge et styrkepas og en løbetur sammen. Anstrengelsen
kommer fra pulsen når den findes (via pulsreserven), ellers fra hvordan passet
føltes.

Derfra: akut belastning som 7-dages eksponentielt snit, kronisk som 28-dages.
Forholdet mellem dem er det tal, der bedst forudsiger overbelastning — 0,8–1,3
er hvor du gerne vil ligge. Monotoni (Fosters metode) fanger den anden fælde:
for mange middelhårde dage i træk.

**Parathed** vægter fem dele, hver målt mod dit eget rullende gennemsnit, ikke
mod en tabel: HRV (28 %), søvn (25 %), krop og hoved (17 %), belastningsbalance
(15 %) og hvilepuls (15 %). Mangler en måling, fordeles vægten på resten.
HRV og hvilepuls læses som 7-dages snit mod en 42-dages basislinje — enkeltdage
støjer for meget til at handle på.

**Løbefiler** (GPX og TCX) regnes ud i telefonen: distance, bevægetid, tempo,
kilometersplits, puls, kadence, stigning og afkobling — fart pr. hjerteslag i
anden halvdel mod første. Over cirka 5 % kostede turen mere, end tempoet siger.

## Data fra Apple Watch

Tre veje, alle under ⚙ Data:

1. **Health Auto Export** (nemmest). Sæt den til at eksportere HRV, hvilepuls og
   søvn som JSON eller CSV, og læg filen ind en gang om ugen.
2. **Apples egen eksport.** Health → profil → «Eksportér alle data» → læg
   `export.xml` ind. Den er stor, så det tager et øjeblik; appen læser den i
   bidder og henter kun de tre målinger.
3. **En simpel CSV** med kolonnerne dato, HRV, hvilepuls og søvn.

Løbeture kommer ud af uret som GPX eller TCX gennem HealthFit, RunGap,
WorkOutDoors eller Strava.

## Claude i appen

Under ⚙ Data kan du lægge en API-nøgle fra `console.anthropic.com` ind. Så går
kaldet direkte fra telefonen til Anthropic — der er ingen server imellem, fordi
der ikke er nogen server. Nøglen bliver på telefonen, og kun hvis du sætter
fluebenet; ellers ligger den i hukommelsen indtil appen lukkes.

Uden nøgle virker kopiér-og-indsæt lige så godt. Det er den samme tekst.

## Kør den

Læg filerne på en hvilken som helst statisk webserver — GitHub Pages virker
fint — og åbn siden på telefonen. Del → «Føj til hjemmeskærm», så opfører den
sig som en app og virker uden net.

Dine data ligger i browserens lokale lager. De overlever opdateringer af appen,
men ikke et telefonskifte eller en rydning af browserdata: tag en
sikkerhedskopi under ⚙ Data en gang imellem.
