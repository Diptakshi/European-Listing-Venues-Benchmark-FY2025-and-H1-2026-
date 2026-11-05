import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

import venues as vn  # noqa: E402

HERE = Path(__file__).parent


def d():
    return vn.load(HERE / "data_venue_datapoints.csv")


def test_real_data_passes_checks():
    assert vn.validate(d())["failures"].sum() == 0


def test_checks_catch_bad_rows():
    bad = pd.concat([d(), pd.DataFrame([
        {"venue": "Euronext", "metric": "ipo_count", "value": 999, "unit": "count", "period": "FY2025", "basis": "x",
         "source_url": "", "comparability_note": ""},
        {"venue": "Nowhere", "metric": "ipo_proceeds", "value": None, "unit": "USD m", "period": "2019", "basis": "x",
         "source_url": "http://x", "comparability_note": ""},
    ])], ignore_index=True)
    c = vn.validate(bad).set_index("check")["failures"]
    for name in ["Known venue", "Allowed unit", "Numeric value", "Plausible range", "Known period", "Source present",
                 "Definition present", "No duplicates"]:
        assert c[name] > 0, name


def test_average_deal_size():
    t = vn.venue_table(d(), "FY2025").set_index("venue")
    assert t.loc["Euronext", "avg per IPO"] == round(678 / 76, 1)
    assert t.loc["Deutsche Börse (Frankfurt)", "avg per IPO"] == round(1186 / 3, 1)


def test_no_cross_currency_share():
    # London reports in GBP, Europe in EUR: no share may be computed
    assert vn.share(d(), "London Stock Exchange", "ipo_proceeds", "FY2025") is None
    assert vn.share(d(), "Euronext", "ipo_proceeds", "H1 2026") == round(4595 / 7200 * 100, 1)


def test_every_flagged_figure_is_listed():
    f = vn.flags(d())
    assert {"Euronext", "London Stock Exchange", "Europe (all venues)"} <= set(f["venue"])
    assert (f["comparability_note"].str.len() > 0).all()
