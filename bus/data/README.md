# Montevideo Bus Lines — Wikipedia Research Notes

Sources downloaded to `data-bus/`:

| File | Wikipedia article |
|------|-------------------|
| `urbanos-de-montevideo.html` | Anexo:Urbanos de Montevideo |
| `transporte-fuera-de-servicio.html` | Anexo:Líneas de transporte fuera de servicio de Montevideo |
| `stm.html` | Sistema de Transporte Metropolitano |
| `cutcsa.html` | CUTCSA |
| `ucot.html` | Unión Cooperativa Obrera del Transporte |
| `coetc.html` | Cooperativa de Obreros y Empleados del Transporte Colectivo |
| `raincoop.html` | Rápido Internacional Cooperativo |
| `lineas-cutcsa.html` | Anexo:Líneas de CUTCSA |
| `come.html` | Corporación de Ómnibus Micro Este S.A. |
| `lines/linea-*.html` | Individual line articles (128 total) |

External sources consulted (not downloaded):

| URL | What it provided |
|-----|-----------------|
| https://enciclopedia-transporte-del-uruguay.fandom.com/es/wiki/Cooperativa_de_%C3%93mnibus_L%C3%ADnea_A | Cooperativa Línea A routes and their post-1938 numbered successors |
| https://comomemuevo.uy/efemerides | Efemérides: confirmed line 192 created 15 May 1955 by CUTCSA |
| https://www.montevideoantiguo.net/historia-del-omnibus-montevideo/ | General cooperative era history (Alejandro Michelena) |
| https://www.cutcsa.com.uy/institucional/historia | CUTCSA official history: 526 buses on founding day (16 Aug 1937); letras → números Oct 1938 |

---

## Companies — history and line counts

### CUTCSA (1937–present)
- **1928:** Centro de Propietarios de Ómnibus assigns a letter to each cooperative line.
- **1934:** 14 lettered lines in operation: A, B, B-A, B-B, D, E, F-A, G, H, I, K, L, M, Z.
- **1937:** All 14 merged into CUTCSA (founded 16 August 1937) with a fleet of 526 buses.
- **1938:** Letters converted to numbers by IMM order. Full mapping in `cutcsa.txt` lines 184–214.
- **1992:** Absorbed Cooperativa de Trolebuses (a.k.a. Cooptrol) lines after its dissolution.
- **2016:** Absorbed Raincoop lines 14, 21, 77, D10 after Raincoop dissolved.
- **Current (per Wikipedia):** 59 urban + 2 centric (CE1, CE2) + 28 local + 4 differential (DE1, D5, D8, D10) + 10 suburban = ~105 routes; 1,135 units.
- **Internal structure:** Lines grouped into "agrupaciones" named after original cooperatives:
  - Línea A (1929): urban 21, 64, 100, 102, 103, 105, 109, 110, 111, 112; local L20, L30, L36, L46
  - Línea Pocitos (2004, merger of B and Bb): urban 62, 104, 116, 117, 121
  - Línea D (1928): urban 124, 125, 127, 128, 130, 133, 135, 137, 195; local L1, L4–L6, L15, L23, L26, L28, L35, L39
  - Línea E (1928): urban 60, 115, 140–145; local L40, L41
  - Línea FHZ (2008 merger of F and HZ): urban 113, 147–151, 163, 180, 191, 199; local L3, G3, G6, G10, G11
  - Línea G (1930): urban 150, 155, 156, 157, 158
  - Línea I (1929): urban 169, 174, 175, 185, 186, 192; local L2, L22, G8
  - Línea J (2020, electric): centric CE1, CE2; urban E14; differential DE1
  - Línea K: urban 181, 182, 183
  - Línea L: urban 187, 188
  - Inter-diferencial: differential D5, D8, D10; suburban C1–C5, 214, 227, 230, 268, 276

---

### COETC (1959/1963–present)
- **Constituted:** 1959 (statutes approved 27 October 1959, registered April 1961).
- **Service start:** 7 February 1963.
- **Founding lines (12):** 402, 404, 405, 407, 409, 410, 411, 427, 441, 445, 447, 456.
  - 441, 445, 447 operated only months; 410 closed 1969.
- **1992:** Absorbed Cotsur (Cooperativa Obrera de Transportes del Sur) after its dissolution.
  Received 65 permits + lines 1 (nocturnal, short-lived), 68→468, 95→495 and ~300 workers.
- **2007 Aug 1:** Absorbed CODET (Cooperativa Obrera de Transporte), created COETC Inter for suburban.
- **2012:** Line 468 renamed G (Corredor Garzón BRT).
- **2016:** Absorbed some Raincoop lines (article says COETC, UCOT, CUTCSA split Raincoop).
- **Current:** 35 lines; 283 units.

---

### UCOT (1963–present)
- **Founded:** 26 February 1963.
- **Founding fleet:** 50 buses (ACLO), 4 lines: **300, 306, 329, 330**.
- **1975:** AMDET dissolved → absorbed lines **316, 366, 370, 396** + 362 workers + 53 Leyland buses.
  - Line 366 later discontinued.
- **Before STM (Jan 2007):** 8 urban lines: 300, 306, 316, 328, 329, 330, 370, 396 + diffeRential D2 (shared) + local L13. Total ~159 units.
- **2007 Feb 1:** Merged with CUTU → absorbed 627 workers, 159 units, added line 11A (suburban) + 3 Canelones locals. Created UCOT Inter.
- **2016:** Raincoop dissolved → UCOT received lines **17, 71, 79, L12, 221** + 31 buses.
- **Current lines (Wikipedia list):** 17, 71, 79, 300, 306, 316, 328, 329, 330, 370, 396, CE1, L12, L13, L31, L32, L33, PB (~18 urban + local).

---

### Raincoop (1975–2016)
- **Founded:** 13 May 1975, from AMDET dissolution (cooperative of ex-municipal workers).
- **Lines at dissolution:** 2, 14, 17, 21, 71, 76, 77, 79, CA1, L12, L17, L18, L20, L21, DM1, D10, 221, 221R, 222, 222D.
- **1992:** Absorbed Cotsur lines 17 and 76.
- **Dissolved:** 10 June 2016 (financial difficulties).
  Lines split: 14, 21, 77, D10 → CUTCSA; 17, 71, 79, L12, 221 → UCOT; others → COETC.

---

### COME — Corporación de Ómnibus Micro Este S.A. (1963–present)
- **Origin:** Workers from AMDET's "Estación Este" (tram depot). First assembly 19 November 1955; 70 Isuzu/Kawasaki buses arrived February 1963.
- **Founded:** 18 July 1963 (first day of service). Like UCOT and COETC, rooted in AMDET workers — but organised independently, not from the 1975 AMDET dissolution.
- **Founding lines:** 22 (Sayago–Trouville), 124 (Aduana–Tres Ombúes), 326 (Sayago–Verdi). Soon added 10, 11, 15, 28, 38, 46 (former tram lines of the Estación Este).
- **August 1963:** IMM renumbering — all lines get "5" prefix: 510, 511, 515, 522, 524, 526, 528, 538, 546.
- **Colors:** grey with red stripe (original) → green for urban, orange for differential/suburban (since 2002).
- **Early 1990s:** Received differential line D11 (Ciudad Vieja–Puente Carrasco).
- **1992:** Cotsur dissolved (30 Oct) → COME absorbed 160 workers + 29 permits for lines 5→505 and 82→582.
- **2006 Oct 9:** Inaugurated local lines L24 and L25 jointly with UCOT (Sayago–Colón corridor). L25 suppressed December 2007, L24 remains.
- **2008 Mar 3:** DM1 launched, shared with all urban operators.
- **2011 Apr:** Merged with SOLFY S.A. (San José suburban) → created COME Inter division, taking on 1M*/2M* suburban lines.
- **2016:** Excluded from Raincoop line negotiations by Montevideo government. Later bought 31 Raincoop buses at auction.
- **Current:** 169 buses; 9 urban + 2 differential (D11, DM1) + 21 suburban + 4 local = ~36 routes.
- **Current Montevideo urban lines:** 505, 522, 524, 526, 538, 546, 582, L24, L38.

---

### Predecessor/dissolved companies

| Company | Active | Notes |
|---------|--------|-------|
| La Transatlántica de Tranvías | 1907–1933 | Tramways |
| Sociedad Comercial de Montevideo | 1906–1947 | Predecessor to AMDET; unclear if it operated buses or only trams |
| Administración Municipal de Transporte (AMDET) | 1947–1975 | Municipal bus/trolleybus service; dissolved into 4 cooperatives |
| Autobuses Montevideo S.A. | 1947–1949 | |
| Transporte Urbanos S.A. | 1947–1949 | |
| Cooperativa de Trolebuses | 1975–1992 | Trolleybuses; lines absorbed by CUTCSA |
| Cooperativa de Transportes del Sur (Cotsur / COOPTROL) | 1975–1992 | Lines 1, 17, 68, 76, 95 → split to COETC and Raincoop |
| Rápido Internacional Cooperativo (Raincoop) | 1975–2016 | See above |
| CUTU (Cooperativa Uruguaya de Transporte Urbano) | ?–2007 | Absorbed by UCOT Feb 2007 |
| CODET (Cooperativa Obrera de Transporte) | ?–2007 | Absorbed by COETC Aug 2007 |

---

## STM system — key facts

- **Inaugurated:** 15 October 2007.
- **Current totals:** 208 urban lines, 87 suburban lines, 294 total, ~2,334 buses.
- **Original 5 operators (2008):**

| Company | Units at STM launch |
|---------|-------------------|
| CUTCSA | 1,154 |
| COETC | 300 |
| UCOT | 235 |
| COME | 185 |
| Raincoop | ~152 (dissolved 2016) |

- **Later additions (2020+):** Compañía de Ómnibus de Pando (290), Casanova (30), CITA (10), Compañía de Ómnibus del Este (55), Rutas del Norte (18), San Antonio Transporte y Turismo (22), Empresa Tala Pando Montevideo (90), Zeballos Hermanos (30).

---

## Current urban lines by company (Montevideo)

| Company | Urban lines (approx) | Notes |
|---------|---------------------|-------|
| CUTCSA | 59 urban + 2 centric + 28 local + 4 differential | Per Wikipedia CUTCSA article |
| COETC | ~35 total | Per Wikipedia COETC article |
| UCOT | ~18 urban + local | Per Wikipedia UCOT article |
| COME | 9 urban + 2 differential + 4 local | 169 buses total; per Wikipedia COME article |

---

## Shared lines (operated by more than one company)

These lines need special handling in the plot — they cannot be attributed to a single company.

| Line | Companies | Period | Source |
|------|-----------|--------|--------|
| D2 | UCOT + CUTCSA | pre-STM (confirmed Jan 2007) | ucot.txt: "compartida con Cutcsa" |
| CA1 (→ CE1 in 2020) | Raincoop + CUTCSA | 2008–2016 | raincoop.txt: "compartida con CUTCSA" |
| DM1 | All 5 urban operators (CUTCSA, UCOT, COETC, COME, Raincoop) + COPSA | 2008– | ucot.txt + raincoop.txt + come.txt |
| L24, L25 | COME + UCOT | 2006–; L25 suppressed Dec 2007 | come.txt |
| XA1, XA2 | UCOT + COPSA | 2021/2023– | ucot.txt: "compartidas con COPSA" |

**Open question:** CE1 currently appears in both the CUTCSA (Línea J) and UCOT line lists — unclear if this is a data error in Wikipedia or a genuine ongoing co-operation after Raincoop's CA1 was split in 2016.

---

## Historical snapshots — line counts per company (what we know)

These are the data anchors available; anything between them needs inference or additional sources.

| Year | CUTCSA | UCOT | COETC | COME | Raincoop | Cotsur | AMDET | Notes |
|------|--------|------|-------|------|----------|--------|-------|-------|
| 1934 | 14 (letter lines, pre-merger) | — | — | — | — | — | — | Pre-CUTCSA |
| 1937 | all (merger) | — | — | — | — | — | — | 526 buses |
| 1963 | many (unknown) | 4 | 12 | ~9 | — | — | still active | UCOT+COETC+COME all founded this year |
| Aug 1963 | many | 4 | 12 | ~9→ renumbered 5xx | — | — | still active | IMM renumbers COME lines with "5" prefix |
| 1975 | many | ~6+ | ~9 | ~9 | new | new | dissolved | AMDET → 4 coops |
| 1992 | +Trolebuses | 8 | +Cotsur (~11?) | +505,582 | ~9 | dissolved | — | Cotsur lines split: most→COETC, 17+76→Raincoop, 5+82→COME |
| Jan 2007 | ? | 10 (8+D2+L13) | ? | ~9 | ~12 | — | — | Pre-STM snapshot |
| 2008 | ? | ? | ? | ? | ~12 | — | — | STM launch; fleet counts only |
| 2016 | +14,21,77,D10 | +17,71,79,L12,221 | +some | (excluded) | dissolved | — | — | Raincoop closes; COME excluded from line redistribution |
| 2026 | ~93 | ~18 | ~35 | ~15 | — | — | — | Current (approx) |

---

## lines.csv — date format

Year fields use the following notation where exact dates are unavailable:
- `YEAR` — confirmed year
- `YEAR-YEAR` — plausible range (e.g. `1920-1937` = created in the 1920s, became CUTCSA by 1937)
- `YEAR-` — created around this year, end unknown (e.g. `1937-` = CUTCSA-era line, exact founding undocumented)
- `-YEAR` — ended around this year, origin unknown

---

## Key data gaps and findings from research

- **Cooperativa Línea A routes → numbered lines:** Línea A had routes Ab, Ac, Af, Ai, Aj, Ak which became lines **103, 104, 105, 106, 107, 108** respectively. Lines 100, 102, 109–112 are in the current Línea A *agrupación* but are NOT confirmed successors of the pre-1937 cooperative — they may be post-1937 CUTCSA additions. Source: Fandom wiki.
- **Line 192 confirmed created 1955** by CUTCSA (Punta Carretas–Hipódromo). Source: comomemuevo.uy efemérides.
- **Lines 100, 102, 109–112:** Origin unknown from available sources. Assigned `year_start='1937-'` (CUTCSA era, date undocumented).

- **Were the 14 letter-lines the only buses in 1937?**
  - The Centro de Propietarios "reunió y nucleó a **diversos**" operators,
    implying it may not have been exhaustive. The Sociedad Comercial de
    Montevideo (1906–1947) existed in parallel but it is unclear whether it
    ran buses or only trams. Not resolved by Wikipedia sources.
- **CUTCSA line count per year**
  - only "current 59 urban" and "1934: 14 letter lines". No intermediate data.
- **COETC line count history** 
  - only founding 12 lines and current 35.
- **COME founding date and line list** 
  - no Wikipedia source; company website (come.com.uy) may have it.
- **Raincoop line count pre-1992** 
  - article says 9 urban at dissolution but not the earlier number.
- **Cotsur / Cooptrol line list** 
  - mentioned as predecessors, no detailed article.
- **Intermediate years** 
  - all sources give snapshot data at key events, not annual series.
- **Line number ↔ company attribution pre-STM**
  - the `Urbanos de Montevideo` page lists all current lines but **without
    company** column. Need to cross-reference UCOT and COETC line lists
    against the master list.

---

## lines.csv — auto-parsed output and known caveats

`data-bus/lines.csv` was generated by `download_lines.py` from the 133 individual line Wikipedia pages.
Fields: `line, company_current, company_history, year_start, year_end, status, route, notes`.

**What the parser does well:**
- Lines that have a structured infobox operator timeline (`• COMPANY (YEAR–YEAR)`) get full history extracted: 2, 17, 21, 60, 62, 64, 71, 76, 79, G, L12, and most UCOT/COETC/COME lines.
- `company_current` is reliable for all lines with named operators in the infobox.

**Known systematic caveats — manual review needed:**
- **Supresión + Reapertura combo:** Some lines (71, 582, L12, others) show a `Supresión` year that is actually a company transfer, immediately followed by `Reapertura`. Parser sets `year_end` from Supresión; should be cleared for active lines.
- **Predecessor Inauguración dates:** Lines 103, 191 (and likely others in CUTCSA's 1xx range) have `Inauguración` years going back to 1905–1930s because their infobox refers to the original letter-cooperative. The numbered line only started in 1937–1938. Rule of thumb: if `year_start < 1937` for a CUTCSA line, it's a predecessor date.
- **"inicios" in operator timeline:** Some lines (e.g. L12) have `• RAINCOOP (inicios – 2016)`. The parser can't extract a year from "inicios" so the timeline entry is skipped and `year_start` becomes 2016 (the UCOT takeover), not the true origin.
- **Missing operator:** Line 125 (and a few others) have no operator listed in their infobox. Company is blank; should be CUTCSA per the Líneas de CUTCSA annex.

## Next steps

1. Manual pass on `lines.csv` to fix the caveats above.
2. Use `comomemuevo.uy/Efemerides` for year-level event timeline to fill gaps.
3. Once CSV is clean, build the plot.
4. Consider a plot with **event-based** time axis rather than continuous years:
   key events: 1937 (CUTCSA), 1963 (UCOT+COETC), 1975 (AMDET dissolves), 1992 (Cotsur dissolves), 2007 (STM), 2016 (Raincoop dissolves).
