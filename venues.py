"""Load, validate and compare European listing venues.

Each datapoint keeps its unit, period, definition, source and comparability note. Ratios are only
computed between figures with the same unit and period, so no currency or methodology is mixed silently.
"""
from __future__ import annotations

import pandas as pd

VENUES = ["Euronext", "London Stock Exchange", "Nasdaq Nordic (Stockholm + Helsinki)", "Deutsche Börse (Frankfurt)",
          "SIX Swiss Exchange", "Oslo Børs", "Europe (all venues)"]
METRICS = {
    "ipo_count": ("IPOs / new equity listings", {"count"}, (0, 500)),
    "ipo_proceeds": ("IPO proceeds", {"EUR m", "GBP m", "CHF m"}, (0, 60000)),
    "followon_proceeds": ("Follow-on proceeds", {"EUR m"}, (0, 100000)),
    "largest_ipo": ("Largest IPO", {"EUR m", "CHF m"}, (0, 20000)),
    "tech_share_of_listings": ("Tech share of new listings", {"%"}, (0, 100)),
    "listed_issuers": ("Listed issuers", {"count"}, (10, 10000)),
    "market_cap": ("Market capitalisation", {"EUR bn"}, (10, 20000)),
}
PERIODS = {"FY2025", "H1 2026", "Dec 2025"}


def load(path: str = "data_venue_datapoints.csv") -> pd.DataFrame:
    d = pd.read_csv(path, encoding="utf-8", keep_default_na=False)
    d["value"] = pd.to_numeric(d["value"], errors="coerce")
    return d


def validate(d: pd.DataFrame) -> pd.DataFrame:
    out = []

    def check(name, mask, rule):
        bad = d[mask]
        out.append({"check": name, "rule": rule, "failures": int(mask.sum()),
                    "detail": "; ".join(f"{r.venue} / {r.metric} / {r.period}" for r in bad.itertuples())})

    check("Known venue", ~d["venue"].isin(VENUES), "venue is in the list")
    check("Known metric", ~d["metric"].isin(METRICS), "metric is in the dictionary")
    check("Allowed unit", d.apply(lambda r: r.metric in METRICS and r.unit not in METRICS[r.metric][1], axis=1),
          "unit allowed for the metric")
    check("Numeric value", d["value"].isna(), "value parses as a number")
    check("Plausible range", d.apply(lambda r: r.metric in METRICS and pd.notna(r.value)
                                     and not (METRICS[r.metric][2][0] <= r.value <= METRICS[r.metric][2][1]), axis=1),
          "value inside the plausible range")
    check("Known period", ~d["period"].isin(PERIODS), "period is FY2025, H1 2026 or Dec 2025")
    check("Source present", ~d["source_url"].str.startswith("http"), "every datapoint has a source")
    check("Definition present", d["basis"].str.len() < 5, "every datapoint states its basis")
    check("No duplicates", d.duplicated(["venue", "metric", "period"], keep=False), "one value per venue, metric and period")
    return pd.DataFrame(out)


def get(d: pd.DataFrame, venue: str, metric: str, period: str):
    r = d[(d["venue"] == venue) & (d["metric"] == metric) & (d["period"] == period)]
    return (None, None) if r.empty else (float(r["value"].iloc[0]), r["unit"].iloc[0])


def venue_table(d: pd.DataFrame, period: str = "FY2025") -> pd.DataFrame:
    """IPO count, proceeds and average deal size per venue. Average only when count and proceeds both exist."""
    rows = []
    for v in VENUES:
        n, _ = get(d, v, "ipo_count", period)
        p, unit = get(d, v, "ipo_proceeds", period)
        big, bunit = get(d, v, "largest_ipo", period)
        if n is None and p is None and big is None:
            continue
        rows.append({"venue": v, "IPOs": n, "proceeds": p, "unit": unit,
                     "avg per IPO": round(p / n, 1) if n and p is not None else None,
                     "largest IPO": big, "largest IPO unit": bunit})
    return pd.DataFrame(rows)


def share(d: pd.DataFrame, venue: str, metric: str, period: str) -> float | None:
    """Venue figure as % of the European total, only if units match."""
    a, ua = get(d, venue, metric, period)
    b, ub = get(d, "Europe (all venues)", metric, period)
    if a is None or b is None or ua != ub or not b:
        return None
    return round(a / b * 100, 1)


def flags(d: pd.DataFrame) -> pd.DataFrame:
    return d.loc[d["comparability_note"] != "", ["venue", "metric", "period", "value", "unit", "comparability_note"]]


def insights(d: pd.DataFrame) -> dict:
    enx25, _ = get(d, "Euronext", "ipo_proceeds", "FY2025")
    n25, _ = get(d, "Euronext", "ipo_count", "FY2025")
    enx26, _ = get(d, "Euronext", "ipo_proceeds", "H1 2026")
    n26, _ = get(d, "Euronext", "ipo_count", "H1 2026")
    csg, _ = get(d, "Euronext", "largest_ipo", "H1 2026")
    fo, _ = get(d, "Euronext", "followon_proceeds", "FY2025")
    return {
        "euronext_share_of_european_proceeds_2025": share(d, "Euronext", "ipo_proceeds", "FY2025"),
        "euronext_share_of_european_proceeds_h1_2026": share(d, "Euronext", "ipo_proceeds", "H1 2026"),
        "euronext_avg_ipo_2025": round(enx25 / n25, 1),
        "euronext_avg_ipo_h1_2026": round(enx26 / n26, 1),
        "csg_share_of_euronext_h1_2026": round(csg / enx26 * 100, 1),
        "euronext_followon_to_ipo_ratio_2025": round(fo / enx25, 1),
    }
