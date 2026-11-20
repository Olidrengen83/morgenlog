#!/usr/bin/env python3
"""ForældreIntra → kalender.

Logger ind på ForældreIntra for hvert barn (én indgang pr. barn), samler
teksten fra forside, opslag, beskeder, ugeplaner, kalender m.m., lader Claude
trække datoer og vigtige beskeder ud, og skriver resultatet til

  * en .ics-fil pr. barn + én samlet (kan importeres/abonneres på)
  * valgfrit direkte i Google Kalender (via en servicekonto)
  * en kort oversigt (oversigt.md) med vigtige beskeder uden dato

Kør:  python fetcher.py --config config.yaml
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional
from urllib.parse import urljoin, urlparse

import yaml
from pydantic import BaseModel, Field

# --------------------------------------------------------------------------
# Konfiguration
# --------------------------------------------------------------------------

DEFAULT_KEYWORDS = [
    "forside", "opslag", "nyhed", "besked", "kalender", "arrangement",
    "ugeplan", "tilmeld", "lektie", "aktivitet", "begivenhed", "skema",
    "information", "news", "message", "calendar", "weekplan", "signup",
]
SKIP_WORDS = ["logout", "log-ud", "logud", "log ud", "logoff", "mailto:",
              "javascript:", "tel:", "/account/", "profil", "indstilling",
              "settings", "help", "hjaelp", "hjælp"]
FILE_EXT = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".jpg", ".jpeg",
            ".png", ".gif", ".zip", ".mp4", ".ics")


@dataclass
class Child:
    name: str
    match: Optional[str] = None        # navnet som det står i ForældreIntra (default: name)
    calendar_id: Optional[str] = None  # Google-kalender kun for dette barn
    color_id: Optional[str] = None     # Google farve "1".."11"
    extra_urls: list[str] = field(default_factory=list)
    # Kun hvis barnet har sit EGET login (ellers bruges `account`):
    url: Optional[str] = None
    login: Optional[str] = None
    username_env: Optional[str] = None
    password_env: Optional[str] = None

    @property
    def slug(self) -> str:
        return _fold_name(self.name).replace(" ", "-") or "barn"

    @property
    def needle(self) -> str:
        return _fold_name(self.match or self.name)


@dataclass
class Account:
    url: str
    login: str = "direct"            # "direct" (ForældreIntra-login) eller "unilogin"
    username_env: str = "FI_USER"
    password_env: str = "FI_PASS"

    @property
    def key(self) -> tuple:
        return (self.url, self.login, self.username_env, self.password_env)


def _fold_name(s: str) -> str:
    s = s.lower().replace("æ", "ae").replace("ø", "oe").replace("å", "aa")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


SHARED = Child(name="Fælles")


def load_config(path: Path) -> dict:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    cfg["children"] = [Child(**c) for c in cfg["children"]]
    base = cfg.get("account") or {}
    # Gruppér børnene pr. login: ét login kan have flere børn (indgange).
    groups: dict[tuple, tuple[Account, list[Child]]] = {}
    for c in cfg["children"]:
        acc = Account(**{**base, **{k: v for k, v in {
            "url": c.url, "login": c.login, "username_env": c.username_env,
            "password_env": c.password_env}.items() if v}})
        groups.setdefault(acc.key, (acc, []))[1].append(c)
    cfg["accounts"] = list(groups.values())
    cfg.setdefault("max_pages", 25)
    cfg.setdefault("keywords", DEFAULT_KEYWORDS)
    cfg.setdefault("timezone", "Europe/Copenhagen")
    cfg.setdefault("output_dir", "output")
    cfg.setdefault("state_dir", "state")
    cfg.setdefault("model", "claude-opus-5-5")
    cfg.setdefault("keep_past_days", 30)
    cfg.setdefault("google_calendar", {"enabled": False})
    return cfg


# --------------------------------------------------------------------------
# Hent sider med en rigtig (headless) browser
# --------------------------------------------------------------------------

@dataclass
class Page:
    url: str
    title: str
    text: str

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.text.encode()).hexdigest()


class LoginError(RuntimeError):
    pass


def _visible(page, selector: str):
    loc = page.locator(selector)
    for i in range(loc.count()):
        el = loc.nth(i)
        try:
            if el.is_visible():
                return el
        except Exception:
            pass
    return None


def _click_text(page, pattern: str) -> bool:
    for role in ("button", "link"):
        loc = page.get_by_role(role, name=re.compile(pattern, re.I))
        if loc.count() and loc.first.is_visible():
            loc.first.click()
            page.wait_for_load_state("networkidle")
            return True
    loc = page.get_by_text(re.compile(pattern, re.I))
    if loc.count() and loc.first.is_visible():
        loc.first.click()
        page.wait_for_load_state("networkidle")
        return True
    return False


def _submit(page, field_el):
    btn = _visible(page, "button[type=submit], input[type=submit]")
    if btn:
        btn.click()
    else:
        field_el.press("Enter")
    page.wait_for_load_state("networkidle")


USER_SEL = ("input[type=text], input[type=email], input[name*=user i], "
            "input[name*=brugernavn i], input[id*=user i]")
PASS_SEL = "input[type=password]"


def login(page, acc: Account) -> None:
    user = os.environ.get(acc.username_env, "")
    pw = os.environ.get(acc.password_env, "")
    if not user or not pw:
        raise LoginError(f"Mangler {acc.username_env}/{acc.password_env} i miljøet")

    page.goto(acc.url, wait_until="networkidle")

    if acc.login == "unilogin":
        _click_text(page, r"unilogin")
        # UniLogin: brugernavn → Næste → adgangskode → Log ind
        u = _visible(page, USER_SEL)
        if not u:
            raise LoginError("Fandt ikke UniLogin-brugernavnsfelt")
        u.fill(user)
        if not _visible(page, PASS_SEL):
            _submit(page, u)
        p = _visible(page, PASS_SEL)
        if not p:
            raise LoginError("Fandt ikke UniLogin-adgangskodefelt")
        p.fill(pw)
        _submit(page, p)
    else:
        # Nogle skoler viser først et rollevalg (Forælder/Elev/Personale).
        if not _visible(page, PASS_SEL):
            _click_text(page, r"for(æ|ae)lder|parent")
        if not _visible(page, PASS_SEL):
            _click_text(page, r"log ?ind|login")
        u = _visible(page, USER_SEL)
        p = _visible(page, PASS_SEL)
        if not (u and p):
            raise LoginError("Fandt ikke login-formularen (brugernavn/adgangskode)")
        u.fill(user)
        p.fill(pw)
        # Rolle-dropdown på den klassiske ForældreIntra-login
        role = _visible(page, "select[name*=role i]")
        if role:
            for label in role.locator("option").all_inner_texts():
                if re.search(r"for(æ|ae)lder|parent", label, re.I):
                    role.select_option(label=label)
                    break
        _submit(page, p)

    # Samtykke-/"Fortsæt"-skærme efter login
    for _ in range(2):
        if not _click_text(page, r"^(fortsæt|continue|ok|accepter)$"):
            break

    if _visible(page, PASS_SEL):
        raise LoginError("Login lykkedes ikke (adgangskodefeltet er der stadig) – tjek brugernavn/adgangskode og login-type")


def _page_text(page) -> str:
    text = page.evaluate("""() => {
        const root = document.querySelector('main, [role=main], #content, .content') || document.body;
        return root.innerText;
    }""")
    lines = [ln.strip() for ln in text.splitlines()]
    out, prev = [], None
    for ln in lines:
        if ln and ln != prev:
            out.append(ln)
        prev = ln
    return "\n".join(out)


def _links(page, base_host: str, skip: bool = True) -> list[tuple[str, str]]:
    raw = page.evaluate("""() => Array.from(document.querySelectorAll('a[href]'))
        .map(a => [a.href, (a.innerText || a.title || '').trim()])""")
    seen, out = set(), []
    for href, label in raw:
        href = href.split("#")[0]
        u = urlparse(href)
        if u.scheme not in ("http", "https") or u.hostname != base_host:
            continue
        low = (href + " " + label).lower()
        if skip and (any(w in low for w in SKIP_WORDS) or u.path.lower().endswith(FILE_EXT)):
            continue
        if href not in seen:
            seen.add(href)
            out.append((href, label))
    return out


CHILD_PATH = re.compile(r"(/parent/\d+/[^/?#]+)", re.I)


def _child_prefix(href: str) -> Optional[str]:
    m = CHILD_PATH.search(urlparse(href).path)
    return m.group(1) if m else None


def _find_child(page, host: str, child: Child, home: str) -> Optional[str]:
    """Find barnets startside (fx /parent/1234/Emma/Index) fra barnevælgeren."""
    from urllib.parse import unquote
    for href, label in _links(page, host, skip=False):
        hay = _fold_name(unquote(href) + " " + label)
        if child.needle and re.search(rf"\b{re.escape(child.needle)}\b", hay):
            return href
    # Ingen link med navnet – prøv at klikke på navnet (dropdown-vælger).
    page.goto(home, wait_until="networkidle")
    _click_text(page, r"skift barn|vælg barn|mine børn")
    pat = re.escape(child.match or child.name)
    if _click_text(page, rf"\b{pat}\b"):
        return page.url
    return None


def crawl_account(acc: Account, children: list[Child], cfg: dict,
                  debug_dir: Optional[Path]) -> dict[str, list[Page]]:
    """Ét login → sider pr. barn. Returnerer {child.slug: [Page, ...]}."""
    from playwright.sync_api import sync_playwright

    keywords = [k.lower() for k in cfg["keywords"]]
    max_pages = int(cfg["max_pages"])
    launch = {}
    if os.environ.get("CHROMIUM_PATH"):
        launch["executable_path"] = os.environ["CHROMIUM_PATH"]

    def score(link: tuple[str, str]) -> int:
        low = (link[0] + " " + link[1]).lower()
        return sum(k in low for k in keywords)

    result: dict[str, list[Page]] = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(**launch)
        ctx = browser.new_context(locale="da-DK", timezone_id=cfg["timezone"])
        page = ctx.new_page()
        page.set_default_timeout(30_000)

        def dump(tag: str):
            if debug_dir:
                debug_dir.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(debug_dir / f"{tag}.png"), full_page=True)
                (debug_dir / f"{tag}.html").write_text(page.content(), encoding="utf-8")

        try:
            login(page, acc)
        except Exception:
            dump("login")
            raise
        home = page.url
        host = urlparse(home).hostname

        # Find alle børns startsider først, så vi kan holde dem adskilt.
        starts: dict[str, Optional[str]] = {}
        if len(children) == 1 and not children[0].match:
            starts[children[0].slug] = home
        else:
            for c in children:
                page.goto(home, wait_until="networkidle")
                starts[c.slug] = _find_child(page, host, c, home)
        prefixes = {slug: _child_prefix(u) for slug, u in starts.items() if u}

        for child in children:
            start = starts.get(child.slug)
            print(f"  {child.name}: start {start or '(ikke fundet)'}")
            if not start:
                page.goto(home, wait_until="networkidle")
                dump(f"{child.slug}-ikke-fundet")
                print(f"  ! Fandt ikke {child.name} i ForældreIntra – tjek `match:` i config",
                      file=sys.stderr)
                continue
            mine = prefixes.get(child.slug)
            others = [p for s, p in prefixes.items() if s != child.slug and p and p != mine]

            def allowed(href: str) -> bool:
                pre = _child_prefix(href)
                return not (pre and (pre in others or (mine and pre != mine)))

            pages: list[Page] = []
            visited: set[str] = set()

            def grab(url: Optional[str] = None) -> bool:
                if url:
                    if url in visited:
                        return False
                    try:
                        page.goto(url, wait_until="networkidle")
                    except Exception as e:
                        print(f"  ! kunne ikke åbne {url}: {e}", file=sys.stderr)
                        return False
                    visited.add(url)
                visited.add(page.url.split("#")[0])
                p = Page(page.url, page.title(), _page_text(page))
                if p.text:
                    pages.append(p)
                return True

            grab(start)
            sections = [l for l in _links(page, host) if score(l) > 0 and allowed(l[0])]
            sections.sort(key=score, reverse=True)
            queue = [urljoin(home, u) for u in child.extra_urls] + [u for u, _ in sections]

            # Niveau 1: sektioner. Niveau 2: enkelte opslag/beskeder i sektionerne.
            level2: list[str] = []
            for url in queue:
                if len(pages) >= max_pages:
                    break
                if not grab(url):
                    continue
                for href, _ in _links(page, host):
                    if href in visited or href in level2 or href in queue or not allowed(href):
                        continue
                    if href.startswith(url.rstrip("/") + "/") or re.search(r"\d{3,}", urlparse(href).path):
                        level2.append(href)
            for url in level2:
                if len(pages) >= max_pages:
                    break
                grab(url)
            result[child.slug] = pages

        browser.close()
    return result


# --------------------------------------------------------------------------
# Claude: træk datoer og vigtige beskeder ud
# --------------------------------------------------------------------------

Category = Literal["fri", "arrangement", "foraeldremoede", "udflugt",
                   "deadline", "medbring", "lektie", "andet"]


class ExtractedEvent(BaseModel):
    title: str = Field(description="Kort dansk titel, fx 'Juleklip – medbring saks'")
    date: str = Field(description="Startdato YYYY-MM-DD")
    start_time: Optional[str] = Field(None, description="HH:MM, eller null hvis heldags")
    end_date: Optional[str] = Field(None, description="Slutdato YYYY-MM-DD hvis flerdags")
    end_time: Optional[str] = Field(None, description="HH:MM")
    location: Optional[str] = None
    category: Category
    details: str = Field(description="1-3 sætninger: hvad, hvem, hvad skal forældre/barn gøre eller medbringe")
    action_required: bool = Field(description="Skal forældre gøre noget (tilmelde, betale, svare, medbringe)?")
    cancelled: bool = Field(False, description="Er begivenheden aflyst/udsat?")
    existing_uid: Optional[str] = Field(None, description="uid fra listen over kendte begivenheder hvis det er den samme")
    source: str = Field(description="Hvilken side/opslag det stammer fra")


class Extraction(BaseModel):
    events: list[ExtractedEvent]
    notes: list[str] = Field(description="Vigtige beskeder UDEN dato, max 5, én linje hver")


SYSTEM = """Du læser tekst fra ForældreIntra (skolens forældreportal) for ét barn \
og finder det, forældre skal have i kalenderen: fridage, arrangementer, \
forældremøder, udflugter, tilmeldings- og betalingsfrister, ting der skal \
medbringes, prøver/afleveringer.

Regler:
- Kun begivenheder på eller efter i dag. Spring rene menuer, navigation og gamle ting over.
- Løs relative datoer ("på torsdag", "uge 48", "næste fredag") ud fra dagens dato og sidens dato.
- En frist (fx "tilmelding senest 3/12") bliver sin egen begivenhed med category=deadline.
- Er det samme som en kendt begivenhed, så sæt existing_uid og genbrug titlen.
- Opfind aldrig datoer. Er datoen uklar, så læg det i notes i stedet.
- Skriv på dansk, kort og konkret."""


def extract(client, cfg: dict, child: Child, pages: list[Page],
            known: list[dict], today: dt.date, who: Optional[str] = None) -> Extraction:
    known_txt = "\n".join(
        f"- uid={e['uid']} | {e['date']} | {e['title']}" for e in known) or "(ingen)"
    body = "\n\n".join(
        f"=== SIDE: {p.title} ({p.url}) ===\n{p.text[:20000]}" for p in pages)
    user = (f"I dag er {today.isoformat()} ({today.strftime('%A')}). Barn: {who or child.name}.\n\n"
            f"Kendte kommende begivenheder:\n{known_txt}\n\n{body}")

    resp = client.beta.messages.parse(
        model=cfg["model"],
        max_tokens=16000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "medium"},
        system=SYSTEM,
        messages=[{"role": "user", "content": user}],
        output_format=Extraction,
    )
    if resp.stop_reason == "refusal" or resp.parsed_output is None:
        print(f"  ! Claude kunne ikke udtrække noget for {child.name} ({resp.stop_reason})", file=sys.stderr)
        return Extraction(events=[], notes=[])
    return resp.parsed_output


# --------------------------------------------------------------------------
# Lager (hvad er set før, hvilke begivenheder kender vi)
# --------------------------------------------------------------------------

def _uid(child: Child, ev: ExtractedEvent) -> str:
    norm = re.sub(r"\W+", "", ev.title.lower())
    return hashlib.sha1(f"{child.slug}|{ev.date}|{norm}".encode()).hexdigest()


def _valid_date(s: Optional[str]) -> bool:
    try:
        dt.date.fromisoformat(s or "")
        return True
    except ValueError:
        return False


def _valid_time(s: Optional[str]) -> bool:
    return bool(s and re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", s))


class Store:
    def __init__(self, path: Path):
        self.path = path
        self.data = {"pages": {}, "events": {}, "notes": {}}
        if path.exists():
            self.data.update(json.loads(path.read_text(encoding="utf-8")))

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")

    def events_for(self, child: Child) -> list[dict]:
        return [e for e in self.data["events"].values() if e["child"] == child.slug]

    def merge(self, child: Child, ext: Extraction, today: dt.date) -> int:
        changed = 0
        for ev in ext.events:
            if not _valid_date(ev.date):
                continue
            uid = ev.existing_uid if ev.existing_uid in self.data["events"] else _uid(child, ev)
            rec = {
                "uid": uid, "child": child.slug, "child_name": child.name,
                "title": ev.title.strip(), "date": ev.date,
                "start_time": ev.start_time if _valid_time(ev.start_time) else None,
                "end_date": ev.end_date if _valid_date(ev.end_date) else None,
                "end_time": ev.end_time if _valid_time(ev.end_time) else None,
                "location": ev.location, "category": ev.category,
                "details": ev.details, "action_required": ev.action_required,
                "cancelled": ev.cancelled, "source": ev.source,
                "updated": today.isoformat(),
            }
            old = self.data["events"].get(uid)
            if old and {k: v for k, v in old.items() if k not in ("updated", "synced")} == \
                    {k: v for k, v in rec.items() if k != "updated"}:
                continue
            rec["synced"] = False
            self.data["events"][uid] = rec
            changed += 1
        if ext.notes:
            self.data["notes"][child.slug] = {"date": today.isoformat(), "notes": ext.notes}
        return changed

    def prune(self, today: dt.date, keep_days: int):
        cutoff = (today - dt.timedelta(days=keep_days)).isoformat()
        self.data["events"] = {u: e for u, e in self.data["events"].items()
                               if (e.get("end_date") or e["date"]) >= cutoff}


# --------------------------------------------------------------------------
# Output: .ics
# --------------------------------------------------------------------------

VTIMEZONE_CPH = """BEGIN:VTIMEZONE
TZID:Europe/Copenhagen
BEGIN:DAYLIGHT
TZOFFSETFROM:+0100
TZOFFSETTO:+0200
TZNAME:CEST
DTSTART:19700329T020000
RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU
END:DAYLIGHT
BEGIN:STANDARD
TZOFFSETFROM:+0200
TZOFFSETTO:+0100
TZNAME:CET
DTSTART:19701025T030000
RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU
END:STANDARD
END:VTIMEZONE"""

CATEGORY_LABEL = {
    "fri": "Fri", "arrangement": "Arrangement", "foraeldremoede": "Forældremøde",
    "udflugt": "Udflugt", "deadline": "Frist", "medbring": "Medbring",
    "lektie": "Lektie", "andet": "Info",
}


def _esc(s: str) -> str:
    return (s or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line: str) -> str:
    b = line.encode()
    if len(b) <= 75:
        return line
    parts, cur = [], b""
    for ch in line:
        c = ch.encode()
        if len(cur) + len(c) > 74:
            parts.append(cur.decode())
            cur = b""
        cur += c
    parts.append(cur.decode())
    return "\r\n ".join(parts)


def event_summary(e: dict, prefix: bool = True) -> str:
    s = f"[{e['child_name']}] " if prefix else ""
    if e["category"] in ("deadline", "medbring"):
        s += f"{CATEGORY_LABEL[e['category']]}: "
    s += e["title"]
    if e.get("cancelled"):
        s = "AFLYST – " + s
    return s


def event_description(e: dict) -> str:
    d = e["details"] or ""
    if e.get("action_required"):
        d = "⚠️ Kræver handling. " + d
    return f"{d}\n\nKilde: ForældreIntra – {e['source']}"


def _when(e: dict) -> tuple[str, str]:
    d0 = dt.date.fromisoformat(e["date"])
    if not e["start_time"]:
        d1 = dt.date.fromisoformat(e["end_date"]) if e["end_date"] else d0
        return (f"DTSTART;VALUE=DATE:{d0:%Y%m%d}",
                f"DTEND;VALUE=DATE:{d1 + dt.timedelta(days=1):%Y%m%d}")
    start = dt.datetime.combine(d0, dt.time.fromisoformat(e["start_time"]))
    if e["end_time"]:
        end = dt.datetime.combine(dt.date.fromisoformat(e["end_date"] or e["date"]),
                                  dt.time.fromisoformat(e["end_time"]))
        if end <= start:
            end = start + dt.timedelta(hours=1)
    else:
        end = start + dt.timedelta(hours=1)
    return (f"DTSTART;TZID=Europe/Copenhagen:{start:%Y%m%dT%H%M%S}",
            f"DTEND;TZID=Europe/Copenhagen:{end:%Y%m%dT%H%M%S}")


def write_ics(path: Path, name: str, events: list[dict]):
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//foraeldreintra-fetcher//DA",
             "CALSCALE:GREGORIAN", f"X-WR-CALNAME:{_esc(name)}",
             "X-WR-TIMEZONE:Europe/Copenhagen", *VTIMEZONE_CPH.splitlines()]
    for e in sorted(events, key=lambda e: (e["date"], e["start_time"] or "")):
        start, end = _when(e)
        lines += ["BEGIN:VEVENT", f"UID:{e['uid']}@foraeldreintra", f"DTSTAMP:{now}",
                  start, end, f"SUMMARY:{_esc(event_summary(e))}",
                  f"DESCRIPTION:{_esc(event_description(e))}",
                  f"CATEGORIES:{_esc(CATEGORY_LABEL.get(e['category'], 'Info'))}"]
        if e.get("location"):
            lines.append(f"LOCATION:{_esc(e['location'])}")
        if e.get("cancelled"):
            lines.append("STATUS:CANCELLED")
        if e.get("action_required") and not e.get("cancelled"):
            trig = "-PT6H" if not e["start_time"] else "-P1D"   # kl. 18 dagen før / døgnet før
            lines += ["BEGIN:VALARM", "ACTION:DISPLAY",
                      f"DESCRIPTION:{_esc(event_summary(e))}", f"TRIGGER:{trig}", "END:VALARM"]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\r\n".join(_fold(l) for l in lines) + "\r\n", encoding="utf-8")


def write_overview(path: Path, store: Store, children: list[Child], today: dt.date):
    out = [f"# ForældreIntra – oversigt ({today.isoformat()})", ""]
    horizon = (today + dt.timedelta(days=14)).isoformat()
    for c in children:
        out.append(f"## {c.name}")
        evs = sorted((e for e in store.events_for(c)
                      if today.isoformat() <= e["date"] <= horizon and not e["cancelled"]),
                     key=lambda e: (e["date"], e["start_time"] or ""))
        for e in evs:
            t = f" {e['start_time']}" if e["start_time"] else ""
            flag = " ⚠️" if e["action_required"] else ""
            out.append(f"- **{e['date']}{t}** {event_summary(e, prefix=False)}{flag} – {e['details']}")
        if not evs:
            out.append("- Intet de næste 14 dage.")
        notes = store.data["notes"].get(c.slug, {}).get("notes", [])
        if notes:
            out.append("")
            out.append("Vigtige beskeder uden dato:")
            out += [f"- {n}" for n in notes]
        out.append("")
    path.write_text("\n".join(out), encoding="utf-8")


# --------------------------------------------------------------------------
# Output: Google Kalender (valgfrit)
# --------------------------------------------------------------------------

def sync_google(store: Store, children: list[Child], gcfg: dict, tz: str, force: bool):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    info = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/calendar"])
    api = build("calendar", "v3", credentials=creds, cache_discovery=False)
    by_slug = {c.slug: c for c in children}

    n = 0
    for e in store.data["events"].values():
        if e.get("synced") and not force:
            continue
        child = by_slug.get(e["child"])
        cal = (child.calendar_id if child and child.calendar_id else gcfg["calendar_id"])
        prefix = not (child and child.calendar_id)
        body = {
            "id": e["uid"],  # sha1-hex er gyldigt Google-event-id
            "summary": event_summary(e, prefix=prefix),
            "description": event_description(e),
            "location": e.get("location") or None,
            "reminders": {"useDefault": False, "overrides": (
                [{"method": "popup", "minutes": 360 if not e["start_time"] else 1440}]
                if e.get("action_required") else [])},
        }
        if child and child.color_id:
            body["colorId"] = str(child.color_id)
        if e["start_time"]:
            s, en = _when(e)
            fmt = lambda v: dt.datetime.strptime(v.split(":", 1)[1], "%Y%m%dT%H%M%S").isoformat()
            body["start"] = {"dateTime": fmt(s), "timeZone": tz}
            body["end"] = {"dateTime": fmt(en), "timeZone": tz}
        else:
            d1 = dt.date.fromisoformat(e["end_date"] or e["date"]) + dt.timedelta(days=1)
            body["start"] = {"date": e["date"]}
            body["end"] = {"date": d1.isoformat()}
        try:
            if e.get("cancelled"):
                try:
                    api.events().delete(calendarId=cal, eventId=e["uid"]).execute()
                except HttpError as err:
                    if err.resp.status not in (404, 410):
                        raise
                e["synced"] = True
                continue
            api.events().insert(calendarId=cal, body=body).execute()
        except HttpError as err:
            if err.resp.status == 409:   # findes allerede → opdatér
                api.events().update(calendarId=cal, eventId=e["uid"], body=body).execute()
            else:
                print(f"  ! Google-fejl for '{e['title']}': {err}", file=sys.stderr)
                continue
        e["synced"] = True
        n += 1
    print(f"Google Kalender: {n} begivenheder oprettet/opdateret")


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=os.environ.get("FI_CONFIG_FILE", "config.yaml"))
    ap.add_argument("--only", help="Kun ét barn (navn)")
    ap.add_argument("--dry-run", action="store_true", help="Hent og vis sider, men kald ikke Claude/Google")
    ap.add_argument("--force", action="store_true", help="Send alle sider til Claude og gensynkronisér alt")
    ap.add_argument("--debug", action="store_true", help="Gem skærmbillede/HTML ved loginfejl")
    args = ap.parse_args()

    cfg = load_config(Path(args.config))
    base = Path(args.config).resolve().parent
    out_dir = base / cfg["output_dir"]
    state = Store(base / cfg["state_dir"] / "state.json")
    today = dt.date.today()
    children = [c for c in cfg["children"] if not args.only or c.name.lower() == args.only.lower()]

    client = None
    if not args.dry_run:
        import anthropic
        client = anthropic.Anthropic()

    failures = 0
    wanted = {c.slug for c in children}
    for acc, kids in cfg["accounts"]:
        kids = [c for c in kids if c.slug in wanted]
        if not kids:
            continue
        print(f"\n== Login {acc.url} ({', '.join(c.name for c in kids)})")
        try:
            by_child = crawl_account(acc, kids, cfg, base / "debug" if args.debug else None)
        except Exception as e:
            print(f"  ! {type(e).__name__}: {e}", file=sys.stderr)
            failures += len(kids)
            continue
        # Sider uden barn i adressen, som optræder hos flere børn (fx indbakken),
        # behandles én gang som "Fælles" i stedet for tre gange.
        jobs = [(c, by_child[c.slug], None) for c in kids if c.slug in by_child]
        failures += len(kids) - len(jobs)
        if len(jobs) > 1:
            counts: dict[str, int] = {}
            for _, pages, _ in jobs:
                for pg in pages:
                    counts[pg.url] = counts.get(pg.url, 0) + 1
            is_shared = lambda pg: counts[pg.url] > 1 and not _child_prefix(pg.url)
            shared = list({pg.url: pg for _, pages, _ in jobs for pg in pages if is_shared(pg)}.values())
            jobs = [(c, [pg for pg in pages if not is_shared(pg)], None) for c, pages, _ in jobs]
            if shared:
                names = ", ".join(c.name for c in kids)
                jobs.append((SHARED, shared,
                             f"Fælles beskeder for {names}. Står det, at noget kun gælder ét af "
                             f"børnene (eller dets klasse), så skriv barnets navn først i titlen"))
        for child, pages, who in jobs:
            seen = state.data["pages"]
            key = lambda p: f"{child.slug}|{p.url}"
            new = [p for p in pages if args.force or seen.get(key(p)) != p.digest]
            print(f"  {child.name}: {len(pages)} sider hentet, {len(new)} nye/ændrede")
            if args.dry_run:
                for p in pages:
                    print(f"   - {p.title[:60]!r} {p.url} ({len(p.text)} tegn)")
                continue
            if new:
                known = [e for e in state.events_for(child) if e["date"] >= today.isoformat()]
                ext = extract(client, cfg, child, new, known, today, who)
                changed = state.merge(child, ext, today)
                print(f"  {child.name}: {len(ext.events)} begivenheder fundet, {changed} nye/ændrede")
                for p in new:
                    seen[key(p)] = p.digest
            state.save()

    if args.dry_run:
        return 1 if failures else 0

    state.prune(today, int(cfg["keep_past_days"]))
    all_events = list(state.data["events"].values())
    cal_children = cfg["children"] + ([SHARED] if state.events_for(SHARED) else [])
    for c in cal_children:
        write_ics(out_dir / f"{c.slug}.ics", f"Skole – {c.name}", state.events_for(c))
    write_ics(out_dir / "alle-boern.ics", "Skole – alle børn", all_events)
    write_overview(out_dir / "oversigt.md", state, cal_children, today)
    print(f"\nSkrev {len(all_events)} begivenheder til {out_dir}/")

    if cfg["google_calendar"].get("enabled"):
        sync_google(state, cal_children, cfg["google_calendar"], cfg["timezone"], args.force)
    state.save()
    return 1 if failures == len(children) else 0


if __name__ == "__main__":
    sys.exit(main())
