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

**LOG** — hvert pas med load, RPE og parathed den dag. Pas, uret har logget uden
øvelser, kan færdiggøres herfra.

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

**Træningsfiler** (FIT, GPX og TCX) regnes ud i telefonen. Løb: distance,
bevægetid, tempo, kilometersplits, puls, kadence, stigning og afkobling — fart
pr. hjerteslag i anden halvdel mod første; over cirka 5 % kostede turen mere,
end tempoet siger. Styrke og andet indendørs uden GPS: varighed, puls og
forbrænding, og så taster du vægt og gentagelser, som er det eneste, uret ikke
kan måle. Hvor uret selv har regnet en total ud, vinder den over appens egen
udregning fra punktstrømmen.

## Så lidt manuelt arbejde som muligt

### Træninger

**Lad HealthFit lægge filerne af sig selv.** Settings → Auto Export → iCloud
Drive eller Dropbox. Så ender hver træning i mappen, uden at du rører den. I
appen under ⚙ Data trykker du på «Hent en hel bunke ind» og markerer alle
filerne på én gang: iOS' filvælger åbner direkte i mappen, appen sorterer dem på
dato, springer dem over den allerede kender, og udbygger et pas, du har tastet i
forvejen, med urets tal. FIT virker direkte — du behøver ikke skifte format.

**Eller lad en genvej gøre det.** Genveje → Automatisering → Personlig →
Træning → Når en træning slutter → Kør straks. Tilføj «Hent træninger» og
dernæst «Åbn URL» med adressen fra ⚙ Data:

```
https://…/index.html#ind=1&sport=styrke&start=[Startdato]&min=[Varighed]&puls=[Gnspuls]&kcal=[Energi]
```

Felterne i kantede parenteser erstatter du med variabler fra træningen. Til løb
sættes `sport=loeb`, og `&km=[Distance]` tilføjes. Så åbner Morgenlog med passet
lagt ind, og for styrke står den klar til, at du sætter flueben ved øvelserne.
Adressen ryddes efter læsning, og det samme pas kan ikke lande to gange.

Genvejen kender kun totalerne. Løbeturens splits, kadence og afkobling kommer
først med, når du henter selve filen — de to veje udelukker ikke hinanden, for
appen lægger urets fil oven i det pas, genvejen allerede har oprettet.

### Helbredsdata

Tre veje, alle under ⚙ Data:

1. **Health Auto Export** (nemmest). Sæt den til at eksportere HRV, hvilepuls og
   søvn som JSON eller CSV, og læg filen ind en gang om ugen.
2. **Apples egen eksport.** Health → profil → «Eksportér alle data» → læg
   `export.xml` ind. Den er stor, så det tager et øjeblik; appen læser den i
   bidder og henter kun de tre målinger.
3. **En simpel CSV** med kolonnerne dato, HRV, hvilepuls og søvn.

## Claude i appen

Under ⚙ Data kan du lægge en API-nøgle fra `console.anthropic.com` ind. Så går
kaldet direkte fra telefonen til Anthropic — der er ingen server imellem, fordi
der ikke er nogen server. Nøglen bliver på telefonen, og kun hvis du sætter
fluebenet; ellers ligger den i hukommelsen indtil appen lukkes.

Uden nøgle virker kopiér-og-indsæt lige så godt. Det er den samme tekst.

## De to pulstal

Maxpuls og hvilepuls bruges kun til at oversætte løbepuls til anstrengelse. Du
behøver ikke kende dem på forhånd. Når du har hentet træninger og helbredsdata
ind, foreslår appen selv begge tal under ⚙ Data: maxpulsen ud fra det højeste,
dine pas har vist (næsthøjeste, så snart der er tre pas, så én fejlmåling ikke
sætter den), og hvilepulsen som medianen af de seneste 30 morgener. Ét tryk på
«brug», og de står der.

Belastningen regnes forfra ved hver visning — der ligger ikke et fastfrosset
tal på det enkelte pas. Retter du tallene om en måned, bliver hele historikken
regnet om med det samme.

Den højest målte puls er et gulv, ikke et loft: man rammer sjældent sin sande
maxpuls til daglig. Sætter du den for lavt, ser alle løbeture lidt hårdere ud —
men konsekvent, og da akut/kronisk-forholdet sammenligner dig med dig selv,
flytter det næsten ikke på advarslerne. Det, der skævvrides, er balancen mellem
løb og styrke.

## Kør den

Læg filerne på en hvilken som helst statisk webserver — GitHub Pages virker
fint — og åbn siden på telefonen. Del → «Føj til hjemmeskærm», så opfører den
sig som en app og virker uden net.

Dine data ligger i browserens lokale lager. De overlever opdateringer af appen,
men ikke et telefonskifte eller en rydning af browserdata: tag en
sikkerhedskopi under ⚙ Data en gang imellem.
