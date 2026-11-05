# European Listing Venues – Benchmark (FY2025 and H1 2026)

Where does Euronext win new listings, and where does it lose them? This project compares European
listing venues on IPO counts, IPO proceeds, average deal size and largest deals, using public data
from the exchanges, PwC and EY. It ends with a one-page pitch note of the kind a listing team uses
with issuers.

## Data

27 datapoints in `data_venue_datapoints.csv`, each with its unit, period, definition, source link and,
where needed, a comparability note (21 flagged).

| Venue | 2025 sources |
|---|---|
| Euronext | Q4/FY2025, Q1 and Q2 2026 results; 2025 listings release |
| London Stock Exchange | EY UK IPO Eye Q4 2025 |
| Nasdaq Nordic (Stockholm + Helsinki) | PwC Nordic IPO Watch 2025 |
| Deutsche Börse (Frankfurt) | PwC Germany, Emissionsmarkt 2025 |
| SIX Swiss Exchange | EY Switzerland 2025; SIX full-year figures |
| Europe (all venues) | PwC IPO Watch Europe 2025 and EMEA H1 2026 |

## Method

- **10 data checks** (venue, metric, unit, numeric value, range, period, source, definition,
  duplicates) run before anything is built; the run stops if one fails.
- **Average deal size** = proceeds ÷ number of IPOs, only when both exist for the same period.
- **Shares of the European total** are computed only when the currency matches, so London (GBP)
  and SIX (CHF) are never mixed with euro figures.

## Findings

| | Euronext | Nasdaq Nordic* | Frankfurt | London | SIX |
|---|---|---|---|---|---|
| New listings / IPOs, 2025 | 76 | 18 | 3 | 23 | 3 |
| IPO proceeds, 2025 | €678m | ≥ €6,903m | €1,186m | £2.1bn | > CHF 1bn |
| Average per listing | €8.9m | ≥ €384m | €395m | £91m | ~CHF 333m |

\* Nasdaq Stockholm and Helsinki, main markets and First North.

1. **Most listings, small deals.** In 2025 Euronext had by far the most new listings but raised
   €678m in IPOs, 5.4% of Europe's €12.5bn (PwC, Jan–Nov).
2. **The large deals went elsewhere.** Nasdaq Stockholm and Helsinki raised at least €6.9bn,
   led by Verisure; Frankfurt raised €1.2bn from three IPOs.
3. **H1 2026 reversed it.** Euronext raised €4,595m from 39 listings, about 64% of Europe's
   €7.2bn, and hosted CSG (€3.3bn), Europe's largest IPO since 2022.
4. **One deal carries the half-year.** CSG is 72% of Euronext's H1 IPO money; repeatable mid-cap
   deals are the gap.
5. **The after-listing case is strong.** €13.7bn of follow-ons in 2025 (20x IPO proceeds) and 36%
   of new listings in tech.

## Comparability (read first)

- Euronext counts all new equity listings and includes over-allotment; PwC counts deals of at
  least $5m and excludes greenshoe; EY's European total (100 IPOs, $17.1bn) uses another method.
- London's 23 IPOs include AIM; PwC counts 11 for January to November.
- Nordic proceeds are a lower bound (First North proceeds not disclosed).
- PwC's 2025 European figures stop at 30 November; Frankfurt's at 12 December.
- Shares mixing Euronext and PwC figures are indicative only.

## Files

| File | Role |
|---|---|
| `data_venue_datapoints.csv` | Sourced datapoints |
| `venues.py` | Checks, venue tables, shares, insights |
| `report.py` | Excel workbook (live average formula), 2 charts, one-page pitch note |
| `run.py` | Runs checks, then builds outputs |
| `test_venues.py` | 5 tests (checks, deal size, no cross-currency shares, flags) |

```bash
pip install -r requirements.txt
python run.py
python -m pytest -q test_venues.py
```

*Public data, illustrative analysis.*
