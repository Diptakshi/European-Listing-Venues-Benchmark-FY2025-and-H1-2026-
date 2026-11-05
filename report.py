"""Excel benchmark, charts and a two-page pitch note."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

import venues as vn

NAVY = "1F4E8C"
SHORT = {"Nasdaq Nordic (Stockholm + Helsinki)": "Nasdaq Nordic", "Deutsche Börse (Frankfurt)": "Frankfurt",
         "London Stock Exchange": "London", "SIX Swiss Exchange": "SIX", "Europe (all venues)": "Europe"}


def _sheet(wb, title, df, widths=None):
    ws = wb.create_sheet(title)
    ws.append([str(c) for c in df.columns])
    for c in ws[1]:
        c.font, c.fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor=NAVY)
        c.alignment = Alignment(wrap_text=True, vertical="top")
    for row in df.itertuples(index=False):
        ws.append([None if (isinstance(v, float) and pd.isna(v)) else v for v in row])
    for i, col in enumerate(df.columns, 1):
        ws.column_dimensions[get_column_letter(i)].width = (widths or {}).get(col, max(12, min(55, len(str(col)) + 4)))
    ws.freeze_panes = "B2"
    return ws


def excel(d: pd.DataFrame, path: str = "out_listing_venue_benchmark.xlsx") -> str:
    wb = Workbook()
    ws = wb.active
    ws.title = "README"
    for line in ["European listing venues – benchmark, FY2025 and H1 2026",
                 "Datapoints: every figure with unit, period, definition, source and comparability note.",
                 "FY2025 / H1_2026: IPO count, proceeds and average deal size per venue (average is a live formula).",
                 "Ratios are only computed between figures in the same currency and period.",
                 "Read the Comparability sheet first: counts and proceeds are defined differently by each source."]:
        ws.append([line])
    ws["A1"].font = Font(bold=True, size=13, color=NAVY)
    ws.column_dimensions["A"].width = 100

    _sheet(wb, "Datapoints", d, {"basis": 55, "source_url": 60, "comparability_note": 55, "venue": 34})
    for period, name in [("FY2025", "FY2025"), ("H1 2026", "H1_2026")]:
        t = vn.venue_table(d, period).drop(columns="avg per IPO")
        ws = _sheet(wb, name, t, {"venue": 34})
        col = ws.max_column + 1
        ws.cell(1, col, "avg per IPO (formula)").font = Font(bold=True, color="FFFFFF")
        ws.cell(1, col).fill = PatternFill("solid", fgColor=NAVY)
        for r in range(2, ws.max_row + 1):
            ws.cell(r, col, f'=IF(AND(ISNUMBER(B{r}),ISNUMBER(C{r}),B{r}>0),ROUND(C{r}/B{r},1),"n.a.")')
    ins = vn.insights(d)
    _sheet(wb, "Insights", pd.DataFrame({"metric": list(ins), "value": list(ins.values())}), {"metric": 50})
    _sheet(wb, "Checks", vn.validate(d), {"rule": 45, "detail": 50})
    _sheet(wb, "Comparability", vn.flags(d), {"comparability_note": 70, "venue": 34})
    wb.save(path)
    return path


def charts(d: pd.DataFrame) -> list[str]:
    files = []
    t = vn.venue_table(d, "FY2025")
    t = t[(t["unit"] == "EUR m") & (t["venue"] != "Europe (all venues)")]
    fig, ax = plt.subplots(1, 2, figsize=(9.5, 3.6))
    names = [SHORT.get(v, v) for v in t["venue"]]
    ax[0].bar(names, t["IPOs"], color="#1F4E8C")
    ax[0].set_title("New listings / IPOs, 2025", fontsize=10)
    ax[1].bar(names, t["proceeds"], color="#E07B39")
    ax[1].set_title("IPO proceeds, 2025 (€m)", fontsize=10)
    for a, col in zip(ax, ["IPOs", "proceeds"]):
        for i, v in enumerate(t[col]):
            a.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=8)
        a.tick_params(labelsize=8)
        a.grid(axis="y", alpha=0.3)
    fig.suptitle("Euro-reporting venues only; Nasdaq Nordic proceeds are a lower bound", fontsize=8, color="#555555", y=0.02)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    files.append("out_count_vs_proceeds_2025.png")
    fig.savefig(files[-1], dpi=200)
    plt.close(fig)

    h = vn.venue_table(d, "H1 2026").dropna(subset=["largest IPO"]).sort_values("largest IPO")
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    cols = ["#1F4E8C" if v in ("Euronext", "Oslo Børs") else "#9AA5B1" for v in h["venue"]]
    ax.barh([SHORT.get(v, v) for v in h["venue"]], h["largest IPO"], color=cols)
    for i, v in enumerate(h["largest IPO"]):
        ax.text(v, i, f" €{v:,.0f}m", va="center", fontsize=8)
    ax.set_title("Largest IPO by venue, H1 2026 (blue = Euronext-operated)", fontsize=10)
    ax.set_xlim(0, h["largest IPO"].max() * 1.2)
    ax.tick_params(labelsize=8)
    fig.tight_layout()
    files.append("out_largest_ipo_h1_2026.png")
    fig.savefig(files[-1], dpi=200)
    plt.close(fig)
    return files


def pitch_note(d: pd.DataFrame, chart_files: list[str], path: str = "out_pitch_note.docx") -> str:
    ins = vn.insights(d)
    g = lambda v, m, p: vn.get(d, v, m, p)[0]
    doc = Document()
    s = doc.sections[0]
    s.left_margin = s.right_margin = Inches(0.6)
    s.top_margin = s.bottom_margin = Inches(0.5)
    doc.styles["Normal"].font.name, doc.styles["Normal"].font.size = "Arial", Pt(9)

    def p(text, size=9, bold=False, color=None, after=4):
        par = doc.add_paragraph()
        r = par.add_run(text)
        r.font.size, r.bold = Pt(size), bold
        if color:
            r.font.color.rgb = RGBColor.from_string(color)
        par.paragraph_format.space_after = Pt(after)

    def bullets(items):
        for t in items:
            doc.add_paragraph(t, style="List Bullet").paragraph_format.space_after = Pt(2)

    p("European Listing Venues – Where Euronext Wins and Where It Doesn’t", 14, True, NAVY, 0)
    p("FY2025 and H1 2026 · public data from exchanges, PwC and EY · figures not converted across currencies", 8.5, color="555555", after=8)
    p("Five takeaways", 11, True, NAVY)
    bullets([
        f"Most listings, small deals (2025). Euronext admitted {g('Euronext','ipo_count','FY2025'):.0f} new equity listings but raised "
        f"€{g('Euronext','ipo_proceeds','FY2025'):,.0f}m in IPOs, about €{ins['euronext_avg_ipo_2025']}m per listing and "
        f"{ins['euronext_share_of_european_proceeds_2025']}% of Europe’s €12.5bn (PwC, Jan–Nov).",
        f"Proceeds went north and to Frankfurt. Nasdaq Stockholm and Helsinki raised at least €{g('Nasdaq Nordic (Stockholm + Helsinki)','ipo_proceeds','FY2025'):,.0f}m "
        f"from {g('Nasdaq Nordic (Stockholm + Helsinki)','ipo_count','FY2025'):.0f} listings, led by Verisure; Frankfurt €1,186m from 3 IPOs; London £2.1bn from 23.",
        f"H1 2026 reversed the picture. Euronext raised €{g('Euronext','ipo_proceeds','H1 2026'):,.0f}m from {g('Euronext','ipo_count','H1 2026'):.0f} listings, "
        f"about {ins['euronext_share_of_european_proceeds_h1_2026']:.0f}% of Europe’s €7.2bn, and hosted CSG (€3.3bn), Europe’s largest IPO since 2022.",
        f"But it rests on one deal: CSG alone is {ins['csg_share_of_euronext_h1_2026']:.0f}% of Euronext’s H1 IPO money. Repeatable mid-cap "
        "deals, the size of Ottobock in Frankfurt (€808m) or SMG on SIX (about CHF 903m), are the gap to close.",
        f"The after-listing case is strong: listed companies raised €{g('Euronext','followon_proceeds','FY2025')/1000:.1f}bn in follow-ons in 2025, "
        f"{ins['euronext_followon_to_ipo_ratio_2025']:.0f}x IPO proceeds, and 36% of new listings were tech companies.",
    ])
    p("Talking points for an issuer pitch", 11, True, NAVY)
    bullets([
        "Large caps: Europe’s largest IPO since 2022 (CSG, €3.3bn) listed on Euronext Amsterdam in H1 2026.",
        "Tech and SMEs: 36% of 2025 listings were tech; about 700 listed tech companies worth €1.4tn.",
        "Life after IPO: €13.7bn of follow-ons in 2025, so listed companies keep raising capital.",
        "Reach: over 1,700 issuers and €6.7tn of market capitalisation across seven national exchanges.",
    ])
    p("Comparability: Euronext counts all new equity listings and includes over-allotment; PwC counts deals ≥ $5m and excludes "
      "greenshoe; London includes AIM; Nordic proceeds are a lower bound; 2025 PwC data stop at 30 November. See the Comparability sheet.",
      7.5, color="555555", after=6)
    for f in chart_files:
        doc.add_picture(f, width=Inches(6.3))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p("Sources: Euronext Q4/FY2025, Q1 and Q2 2026 results and 2025 listings release; EY UK IPO Eye Q4 2025; PwC Nordic IPO Watch 2025; "
      "PwC Germany Emissionsmarkt 2025; EY Switzerland and SIX 2025; PwC IPO Watch Europe 2025 and EMEA H1 2026. Links per figure in the Excel file.",
      7.5, color="555555")
    doc.save(path)
    return path
