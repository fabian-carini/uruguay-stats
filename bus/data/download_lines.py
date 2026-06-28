"""Download individual line Wikipedia pages and parse key fields into lines.csv."""

import csv
import os
import re
import subprocess
import time
import urllib.parse
import urllib.request

LINES = [
    "2",
    "17",
    "21",
    "60",
    "62",
    "64",
    "71",
    "76",
    "79",
    "100",
    "102",
    "103",
    "104",
    "105",
    "109",
    "110",
    "111",
    "112",
    "113",
    "115",
    "116",
    "117",
    "121",
    "124",
    "125",
    "127",
    "128",
    "130",
    "135",
    "137",
    "140",
    "141",
    "142",
    "143",
    "144",
    "145",
    "147",
    "148",
    "149",
    "150",
    "151",
    "155",
    "156",
    "157",
    "158",
    "163",
    "169",
    "174",
    "175",
    "180",
    "181",
    "183",
    "185",
    "186",
    "187",
    "188",
    "191",
    "192",
    "195",
    "199",
    "300",
    "306",
    "316",
    "328",
    "329",
    "330",
    "370",
    "396",
    "402",
    "404",
    "405",
    "407",
    "409",
    "427",
    "456",
    "494",
    "505",
    "522",
    "524",
    "526",
    "538",
    "546",
    "582",
    "CE1",
    "CE2",
    "E14",
    "D5",
    "D8",
    "D10",
    "D11",
    "DE1",
    "DM1",
    "G",
    "G3",
    "G6",
    "G8",
    "G10",
    "G11",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "L6",
    "L7",
    "L8",
    "L9",
    "L12",
    "L13",
    "L14",
    "L15",
    "L16",
    "L19",
    "L20",
    "L21",
    "L23",
    "L24",
    "L25",
    "L26",
    "L28",
    "L29",
    "L30",
    "L31",
    "L32",
    "L33",
    "L34",
    "L35",
    "L36",
    "L38",
    "L39",
    "L40",
    "L41",
    "L46",
    "L22",
    "P1",
    "PB",
    "133",
    "182",
]

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# Canonical company names matched by exact word (case-insensitive)
COMPANY_PATTERNS = [
    (re.compile(r"\bCUTCSA\b", re.I), "CUTCSA"),
    (re.compile(r"\bCOETC\b", re.I), "COETC"),
    (re.compile(r"\bUCOT\b", re.I), "UCOT"),
    # COME/COMESA — only match when not inside "Comercio" / "comenzó" etc.
    # "COMESA" is safe; "COME" only when followed by space/punctuation or preceded by • or newline
    (re.compile(r"\bCOMESA\b", re.I), "COME"),
    (re.compile(r"(?<![a-zA-Z])COME(?![a-zA-Z])", re.I), "COME"),
    (re.compile(r"\bRAINCOOP\b", re.I), "Raincoop"),
    (re.compile(r"\bAMDET\b", re.I), "AMDET"),
]

YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")

# Infobox operator line: "• COMPANY (YEAR - YEAR)" or "• COMPANY (YEAR - presente)"
# also plain "COMPANY (YEAR - YEAR)" without bullet
OP_LINE_RE = re.compile(
    r"[•·]\s*([A-ZÁÉÍÓÚÑ][A-Za-záéíóúñ\s]+?)\s*\(\s*(\d{4})\s*[-–]\s*(\d{4}|presente|actualidad)\s*\)",
    re.IGNORECASE,
)


def html_filename(line):
    return os.path.join(OUT_DIR, "lines", f"linea-{line.lower()}.html")


def txt_filename(line):
    return os.path.join(OUT_DIR, "lines", f"linea-{line.lower()}.txt")


def wiki_url(line):
    name = f"Línea_{line}_(Montevideo)"
    encoded = urllib.parse.quote(name)
    return f"https://es.wikipedia.org/wiki/{encoded}"


def download(line):
    path = html_filename(line)
    if os.path.exists(path):
        return True, "cached"
    url = wiki_url(line)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read().decode("utf-8", errors="replace")
        if "La enciclopedia libre" not in html:
            return False, "not a wiki page"
        with open(path, "w") as f:
            f.write(html)
        return True, "downloaded"
    except Exception as e:
        return False, str(e)


def to_text(line):
    src = html_filename(line)
    dst = txt_filename(line)
    if not os.path.exists(src):
        return False
    result = subprocess.run(["w3m", "-dump", src], capture_output=True, text=True)
    with open(dst, "w") as f:
        f.write(result.stdout)
    return True


def find_companies(text):
    """Return list of canonical company names found in text (no duplicates)."""
    found = []
    for pat, name in COMPANY_PATTERNS:
        if pat.search(text) and name not in found:
            found.append(name)
    return found


def parse_operator_timeline(text):
    """
    Extract structured operator history from infobox bullets like:
      • RAINCOOP (1975 - 2016)
      • COETC (2016 - presente)

    Returns list of (company, year_from, year_to) where year_to is None = present.
    """
    entries = []
    for m in OP_LINE_RE.finditer(text):
        raw_name = m.group(1).strip()
        yr_from = int(m.group(2))
        raw_to = m.group(3).strip().lower()
        yr_to = None if raw_to in ("presente", "actualidad") else int(raw_to)
        # map to canonical name
        canonical = raw_name
        for pat, name in COMPANY_PATTERNS:
            if pat.search(raw_name):
                canonical = name
                break
        entries.append((canonical, yr_from, yr_to))
    return entries


def parse_txt(line):
    path = txt_filename(line)
    if not os.path.exists(path):
        return {}

    with open(path) as f:
        text = f.read()

    result = {
        "line": line,
        "company_current": "",
        "company_history": "",
        "year_start": "",
        "year_end": "",
        "status": "active",
        "route": "",
        "notes": "",
    }

    # ── operator timeline from infobox ───────────────────────────────────────
    # Only look in first 3000 chars (infobox comes before body text)
    infobox = text[:3000]
    timeline = parse_operator_timeline(infobox)

    if timeline:
        # current = entry with no end year
        current = [c for c, yf, yt in timeline if yt is None]
        result["company_current"] = "+".join(current) if current else timeline[-1][0]
        result["company_history"] = "; ".join(
            f"{c}({yf}-{yt or 'present'})" for c, yf, yt in timeline
        )
        # earliest year in timeline = line's first bus service year
        result["year_start"] = str(min(yf for c, yf, yt in timeline))
    else:
        # fallback: scan infobox for "Operador" label then find company names
        idx = infobox.find("Operador")
        if idx == -1:
            idx = infobox.find("Empresa")
        if idx != -1:
            snippet = infobox[idx : idx + 200]
            companies = find_companies(snippet)
            # exclude AMDET from current company
            current = [c for c in companies if c != "AMDET"]
            result["company_current"] = "+".join(current)
        if not result["company_current"]:
            # last resort: first 2000 chars, exclude nav noise
            body_start = text.find("[editar]")
            body = text[body_start : body_start + 2000] if body_start != -1 else text[:2000]
            companies = [c for c in find_companies(body) if c != "AMDET"]
            result["company_current"] = "+".join(companies)

    # ── year_start from "Inauguración" infobox field if not already set ─────
    if not result["year_start"]:
        for label in ("Inauguración", "Inicio de servicio"):
            idx = infobox.find(label)
            if idx != -1:
                m = YEAR_RE.search(infobox[idx : idx + 80])
                if m:
                    result["year_start"] = m.group(1)
                    break

    # ── year_end and status — only from actual line termination ──────────────
    for label in ("Supresión", "Clausura", "Fin de servicio"):
        idx = infobox.find(label)
        if idx != -1:
            m = YEAR_RE.search(infobox[idx : idx + 80])
            if m:
                result["year_end"] = m.group(1)
                result["status"] = "inactive"
            break
    # also check Estado/Situación field
    for label in ("Estado", "Situación"):
        idx = infobox.find(label)
        if idx != -1:
            val = infobox[idx + len(label) : idx + len(label) + 60].strip().split("\n")[0].strip()
            if any(w in val.lower() for w in ("servicio", "activ", "operativ")):
                result["status"] = "active"
            elif any(w in val.lower() for w in ("inactiv", "suspendid", "clausurad", "suprimid")):
                result["status"] = "inactive"
            break

    # ── route from "Destinos" ────────────────────────────────────────────────
    for label in ("Destinos", "Recorrido"):
        idx = text.find(label)
        if idx != -1:
            result["route"] = (
                text[idx + len(label) : idx + len(label) + 100].strip().split("\n")[0].strip()
            )
            break

    return result


def main():
    os.makedirs(os.path.join(OUT_DIR, "lines"), exist_ok=True)

    print("=== Downloading (skips cached) ===")
    for line in LINES:
        ok, msg = download(line)
        if msg != "cached":
            print(f"  {line:8s}  {msg}")
            time.sleep(0.4)

    print("\n=== Converting to text ===")
    for line in LINES:
        to_text(line)

    print("\n=== Parsing ===")
    rows = []
    for line in LINES:
        r = parse_txt(line)
        rows.append(r)
        hist = r.get("company_history", "")
        cur = r.get("company_current", "?")
        print(
            f"  {line:8s}  current={cur:20s}  start={r.get('year_start', ''):6s}"
            f"  end={r.get('year_end', ''):6s}  {hist}"
        )

    csv_path = os.path.join(OUT_DIR, "lines.csv")
    fields = [
        "line",
        "company_current",
        "company_history",
        "year_start",
        "year_end",
        "status",
        "route",
        "notes",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {csv_path}")


if __name__ == "__main__":
    main()
