"""
visualize_cptc.py
=================
Generates one multi-page PDF per CPTC survey wave containing a chart
for every closed-ended / ordinal / numeric survey question.

Output files (written to the same directory as this script):
  CPTC5_survey_charts.pdf
  CPTC8_survey_charts.pdf
  CPTC9_survey_charts.pdf
  CPTC10_survey_charts.pdf
  CPTC11_survey_charts.pdf
  

Run:
    python visualize_cptc.py

Dependencies: matplotlib, pandas  (pip install matplotlib pandas)
"""

import re
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np

# ── Paths ─────────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent.parent / "raw csvs"
OUT_DIR = Path(".")  # Same directory as this script

# ── Colour palette ────────────────────────────────────────────────────────────
NAVY      = "#1F3864"
BLUE      = "#2E75B6"
LIGHT     = "#BDD7EE"
TEAL      = "#1B7A6E"
ORANGE    = "#D46B08"
RED_DARK  = "#8B1A1A"
GREEN     = "#2E7D32"
GREY      = "#757575"
BG        = "#F7F9FC"

LIKERT_PALETTE = {
    "Strongly Agree":          "#1B5E20",
    "Agree":                   "#66BB6A",
    "Neither Agree nor Disagree": "#FDD835",
    "Disagree":                "#EF5350",
    "Strongly Disagree":       "#B71C1C",
}
NPS_PALETTE = {
    "Promoter":  GREEN,
    "Passive":   ORANGE,
    "Detractor": RED_DARK,
}

# ── Scale ordering helpers ─────────────────────────────────────────────────────
LIKERT_ORDER  = ["Strongly Agree", "Agree", "Neither Agree nor Disagree",
                 "Disagree", "Strongly Disagree"]
NPS_ORDER     = ["Promoter", "Passive", "Detractor"]
DEGREE_ORDER  = ["Undergraduate/Full Time", "Undergraduate/Part Time",
                 "Graduate/Full Time", "Graduate/Part Time", "Non-matriculated"]
FORMAL_ORDER  = ["0 years", "1 year", "2 years", "3+ years"]
AGE_ORDER     = ["18-24", "25-29", "30-34", "35-39", "40-44", "45-55",
                 "Other/Prefer not to answer"]

# CD item: extract the tail phrase after "to "
CD_SCALE = ["very large extent", "large extent", "somewhat large extent",
            "moderate extent", "somewhat small extent", "small extent",
            "very small extent"]

def cd_shorten(full_text: str) -> str:
    """Extract extent phrase from long CD text label."""
    m = re.search(r"to (a |)(.*?)\.?$", str(full_text), re.IGNORECASE)
    return m.group(2).strip().title() if m else str(full_text)

# ── Generic chart helpers ──────────────────────────────────────────────────────

def wave_header(fig, wave_name: str, n_respondents: int):
    """Add a slim coloured header bar to the figure."""
    ax_h = fig.add_axes([0, 0.97, 1, 0.03])
    ax_h.set_facecolor(NAVY)
    ax_h.axis("off")
    ax_h.text(0.01, 0.5, f"  {wave_name}  ·  n = {n_respondents} respondents",
              va="center", ha="left", color="white",
              fontsize=9, fontweight="bold", transform=ax_h.transAxes)


def save_title_page(pdf: PdfPages, wave_name: str, n_rows: int, description: str):
    fig = plt.figure(figsize=(11, 8.5))
    fig.patch.set_facecolor(NAVY)
    ax = fig.add_subplot(111)
    ax.set_facecolor(NAVY)
    ax.axis("off")
    ax.text(0.5, 0.65, wave_name, ha="center", va="center",
            fontsize=36, fontweight="bold", color="white", transform=ax.transAxes)
    ax.text(0.5, 0.52, "Survey Response Visualizations",
            ha="center", va="center", fontsize=18, color=LIGHT, transform=ax.transAxes)
    ax.text(0.5, 0.42, f"n = {n_rows} respondents",
            ha="center", va="center", fontsize=14, color=LIGHT, transform=ax.transAxes)
    wrapped = textwrap.fill(description, width=70)
    ax.text(0.5, 0.30, wrapped, ha="center", va="center",
            fontsize=11, color="#AACCEE", transform=ax.transAxes, style="italic")
    pdf.savefig(fig, bbox_inches="tight")
    plt.close(fig)


def hbar(ax, labels, counts, colors, title, xlabel="Count", pct=True, total=None):
    """Horizontal bar chart."""
    if total is None:
        total = sum(counts)
    y = np.arange(len(labels))
    bars = ax.barh(y, counts, color=colors, edgecolor="white", linewidth=0.6, height=0.6)
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_title(title, fontsize=10, fontweight="bold", color=NAVY, pad=8)
    ax.set_facecolor(BG)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.spines[["top","right","left"]].set_visible(False)
    for bar, cnt in zip(bars, counts):
        pct_str = f" {cnt/total*100:.1f}%" if pct and total > 0 else ""
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
                f"{cnt}{pct_str}", va="center", fontsize=8, color=GREY)
    ax.set_xlim(0, max(counts) * 1.22 if counts else 1)


def vbar(ax, labels, counts, colors, title, ylabel="Count", pct=True, total=None,
         rotation=0, wrap_width=12):
    """Vertical bar chart with optional label wrapping."""
    if total is None:
        total = sum(counts)
    wrapped = [textwrap.fill(str(l), wrap_width) for l in labels]
    x = np.arange(len(labels))
    bars = ax.bar(x, counts, color=colors, edgecolor="white", linewidth=0.6, width=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels(wrapped, fontsize=8, rotation=rotation, ha="right" if rotation else "center")
    ax.set_ylabel(ylabel, fontsize=9)
    ax.set_title(title, fontsize=10, fontweight="bold", color=NAVY, pad=8)
    ax.set_facecolor(BG)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines[["top","right","left"]].set_visible(False)
    for bar, cnt in zip(bars, counts):
        pct_str = f"\n{cnt/total*100:.1f}%" if pct and total > 0 else ""
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f"{cnt}{pct_str}", ha="center", va="bottom", fontsize=7.5, color=GREY)
    ax.set_ylim(0, max(counts) * 1.25 if counts else 1)


def histogram(ax, values, title, xlabel, color=BLUE, bins=None):
    """Histogram for continuous/numeric columns."""
    values = [v for v in values if pd.notna(v)]
    if not values:
        ax.axis("off"); return
    if bins is None:
        bins = min(len(set(values)), 20)
    ax.hist(values, bins=bins, color=color, edgecolor="white", linewidth=0.5)
    ax.set_xlabel(xlabel, fontsize=9)
    ax.set_ylabel("Count", fontsize=9)
    ax.set_title(title, fontsize=10, fontweight="bold", color=NAVY, pad=8)
    ax.set_facecolor(BG)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines[["top","right","left"]].set_visible(False)
    mn = np.mean(values); md = np.median(values)
    ax.axvline(mn, color=RED_DARK, linestyle="--", linewidth=1.2, label=f"Mean {mn:.1f}")
    ax.axvline(md, color=TEAL,     linestyle=":",  linewidth=1.2, label=f"Median {md:.1f}")
    ax.legend(fontsize=8)


def grouped_likert(ax, col_labels, data_dict, scale_order, palette, title):
    """
    Stacked horizontal bar showing Likert distribution across multiple items.
    col_labels : list of short item names (y-axis)
    data_dict  : {item_label: {response: count}}
    """
    n_items = len(col_labels)
    y = np.arange(n_items)
    left = np.zeros(n_items)
    bars_drawn = []
    for resp in scale_order:
        counts = np.array([data_dict[lbl].get(resp, 0) for lbl in col_labels], dtype=float)
        totals = np.array([sum(data_dict[lbl].values()) for lbl in col_labels], dtype=float)
        pcts   = np.where(totals > 0, counts / totals * 100, 0)
        color  = palette.get(resp, LIGHT)
        b = ax.barh(y, pcts, left=left, color=color, label=resp,
                    edgecolor="white", linewidth=0.5, height=0.6)
        bars_drawn.append((b, resp, pcts))
        left += pcts

    ax.set_yticks(y)
    ax.set_yticklabels(col_labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel("% of respondents", fontsize=9)
    ax.set_title(title, fontsize=10, fontweight="bold", color=NAVY, pad=8)
    ax.set_xlim(0, 100)
    ax.set_facecolor(BG)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.spines[["top","right","left"]].set_visible(False)
    ax.legend(loc="lower right", fontsize=7.5, framealpha=0.8,
              ncol=2 if len(scale_order) > 3 else 1)


def nps_gauge(ax, scores_0_10, title):
    """
    Horizontal stacked bar showing NPS breakdown + score, plus
    a distribution of raw 0-10 values.
    """
    scores = [int(s) for s in scores_0_10 if pd.notna(s) and str(s).strip().isdigit()]
    if not scores:
        ax.axis("off"); return
    det = sum(1 for s in scores if s <= 6)
    pas = sum(1 for s in scores if 7 <= s <= 8)
    pro = sum(1 for s in scores if s >= 9)
    n   = len(scores)
    nps = round((pro - det) / n * 100) if n > 0 else 0

    pct_det = det/n*100; pct_pas = pas/n*100; pct_pro = pro/n*100
    ax.barh(0, pct_pro, color=GREEN,  height=0.5, label=f"Promoter {pro} ({pct_pro:.0f}%)")
    ax.barh(0, pct_pas, left=pct_pro, color=ORANGE, height=0.5,
            label=f"Passive {pas} ({pct_pas:.0f}%)")
    ax.barh(0, pct_det, left=pct_pro+pct_pas, color=RED_DARK, height=0.5,
            label=f"Detractor {det} ({pct_det:.0f}%)")
    ax.set_xlim(0, 100)
    ax.set_yticks([])
    ax.set_xlabel("% of respondents", fontsize=9)
    ax.set_title(f"{title}\n  NPS Score: {nps:+d}  (n = {n})",
                 fontsize=10, fontweight="bold", color=NAVY, pad=8)
    ax.set_facecolor(BG)
    ax.spines[["top","right","left"]].set_visible(False)
    ax.legend(loc="lower right", fontsize=8, framealpha=0.8)


# ── Load helper ───────────────────────────────────────────────────────────────

def load(path):
    """Load a CPTC CSV, return (col_names, question_texts, data_df)."""
    raw = pd.read_csv(path, encoding="utf-8-sig", header=None, dtype=str)
    col_names  = raw.iloc[0].tolist()
    q_texts    = raw.iloc[1].tolist()
    data       = raw.iloc[3:].copy()
    data.columns = col_names
    data = data.reset_index(drop=True)
    # Strip whitespace in all cells
    data = data.apply(lambda c: c.str.strip() if c.dtype == object else c)
    return col_names, q_texts, data


def col_map(col_names, q_texts):
    """Build {col_name: question_text} dict."""
    return {c: t.strip().replace("\r\n", " ").replace("\n", " ")
            for c, t in zip(col_names, q_texts)}


def valid_series(data, col):
    """Return non-empty series for a column."""
    s = data[col].dropna()
    return s[s.str.strip() != ""]

# ── Color cycles ──────────────────────────────────────────────────────────────

CYCLE = [BLUE, TEAL, ORANGE, "#7B1FA2", "#D84315", "#00796B", "#F57F17", "#1565C0"]

def cycle_colors(n):
    return [CYCLE[i % len(CYCLE)] for i in range(n)]


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  PER-WAVE CHART BUILDERS                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

def fig_one(title_short, chart_fn, wave_name, n):
    """Return a fresh landscape figure with header."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    fig.patch.set_facecolor("white")
    plt.subplots_adjust(top=0.88, bottom=0.14, left=0.28, right=0.96)
    wave_header(fig, wave_name, n)
    return fig, ax


def add_missing_note(ax, n_valid, n_total):
    if n_total > n_valid:
        ax.annotate(f"n = {n_valid}  ({n_total-n_valid} missing / did not consent)",
                    xy=(0, -0.11), xycoords="axes fraction",
                    fontsize=7.5, color=GREY, style="italic")


# ── Shared question groups ─────────────────────────────────────────────────────

def charts_demographics(pdf, data, qmap, wave_name, n_total, consent_col="Consent"):
    """Consent, gender, age, degree status, formal education."""

    # 1. Consent
    col = consent_col
    if col in data.columns:
        s   = valid_series(data, col)
        vc  = s.value_counts()
        fig, ax = fig_one("", None, wave_name, n_total)
        hbar(ax, vc.index.tolist(), vc.values.tolist(),
             [GREEN if v == "Yes" else RED_DARK for v in vc.index],
             "Consent to Research", total=len(s))
        add_missing_note(ax, len(s), n_total)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # 2. Gender
    gender_col = "Gender" if "Gender" in data.columns else "Q24"
    if gender_col in data.columns:
        s  = valid_series(data, gender_col)
        vc = s.value_counts()
        fig, ax = fig_one("", None, wave_name, n_total)
        hbar(ax, vc.index.tolist(), vc.values.tolist(), cycle_colors(len(vc)),
             "Gender", total=len(s))
        add_missing_note(ax, len(s), n_total)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # 3. Age
    age_col = "Age" if "Age" in data.columns else "Q25"
    if age_col in data.columns:
        s   = valid_series(data, age_col)
        ordered = [a for a in AGE_ORDER if a in s.values]
        vc  = s.value_counts().reindex(ordered).dropna()
        fig, ax = fig_one("", None, wave_name, n_total)
        hbar(ax, vc.index.tolist(), vc.values.astype(int).tolist(),
             [BLUE] * len(vc), "Age Group", total=len(s))
        add_missing_note(ax, len(s), n_total)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # 4. Degree Status
    deg_col = "Degree Status" if "Degree Status" in data.columns else "Q27"
    if deg_col in data.columns:
        s   = valid_series(data, deg_col)
        ordered = [d for d in DEGREE_ORDER if d in s.values]
        rest    = [v for v in s.unique() if v not in ordered]
        ordered += rest
        vc  = s.value_counts().reindex(ordered).dropna()
        fig, ax = fig_one("", None, wave_name, n_total)
        hbar(ax, vc.index.tolist(), vc.values.astype(int).tolist(),
             cycle_colors(len(vc)), "Degree Status", total=len(s))
        add_missing_note(ax, len(s), n_total)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # 5. Formal Education
    fed_col = "Formal Education" if "Formal Education" in data.columns else "Q26"
    if fed_col in data.columns:
        s   = valid_series(data, fed_col)
        ordered = [f for f in FORMAL_ORDER if f in s.values]
        vc  = s.value_counts().reindex(ordered).dropna()
        fig, ax = fig_one("", None, wave_name, n_total)
        vbar(ax, vc.index.tolist(), vc.values.astype(int).tolist(),
             [TEAL]*len(vc),
             "Years of Formal Cybersecurity Education", total=len(s))
        add_missing_note(ax, len(s), n_total)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def charts_experience(pdf, data, wave_name, n_total,
                      e1="Experience_1", e2="Experience_2", e3="Experience_3",
                      extra_cols=None):
    """Competition count, confidence, years experience, + any extras."""
    exp_defs = [
        (e1, "# Security Competitions (before this one)", "Count", False),
        (e2, "Confidence in Pen-Testing Skills", "Scale value", False),
        (e3, "Years of Pen-Testing Experience", "Years", False),
    ]
    if extra_cols:
        exp_defs += extra_cols

    for col, label, xlabel, cont in exp_defs:
        if col not in data.columns:
            continue
        s = valid_series(data, col)
        if s.empty:
            continue
        numeric = pd.to_numeric(s, errors="coerce").dropna()
        if numeric.empty:
            continue

        fig, ax = fig_one("", None, wave_name, n_total)
        if cont:
            histogram(ax, numeric.tolist(), label, xlabel, color=BLUE)
        else:
            vc = numeric.astype(int).value_counts().sort_index()
            vbar(ax, vc.index.tolist(), vc.values.tolist(),
                 [BLUE]*len(vc), label, ylabel="Count",
                 pct=False, total=len(s))
        add_missing_note(ax, len(s), n_total)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def charts_differing_abilities(pdf, data, wave_name, n_total):
    """Three self-categorisation items as a grouped stacked bar."""
    cols = [c for c in ["Differing abilities_1","Differing abilities_2","Differing abilities_3"]
            if c in data.columns]
    if not cols:
        return
    scale = ["1", "2", "3", "4", "5"]
    palette = {"1": "#1B5E20","2": "#66BB6A","3": "#FDD835","4": "#EF5350","5": "#B71C1C"}
    item_labels = ["Def. 1\n(Disability/\nNeurodiversity)", "Def. 2", "Def. 3"][:len(cols)]

    data_dict = {}
    for lbl, col in zip(item_labels, cols):
        s  = valid_series(data, col)
        vc = s.value_counts()
        data_dict[lbl] = {str(k): int(v) for k, v in vc.items()}

    fig, ax = plt.subplots(figsize=(11, 4))
    fig.patch.set_facecolor("white")
    plt.subplots_adjust(top=0.85, bottom=0.12, left=0.22, right=0.72)
    wave_header(fig, wave_name, n_total)

    grouped_likert(ax, item_labels, data_dict, scale, palette,
                   "Self-Categorization: Differing Abilities (1=Does not apply → 5=Applies strongly)")
    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def charts_cd(pdf, data, wave_name, n_total):
    """CD-1 through CD-4 as stacked horizontal bar."""
    cd_cols  = [c for c in ["CD-1","CD-2","CD-3","CD-4"] if c in data.columns]
    if not cd_cols:
        return

    item_labels = {
        "CD-1": "Way of Thinking",
        "CD-2": "Knowledge & Skills",
        "CD-3": "Worldview",
        "CD-4": "Ethical Beliefs",
    }

    palette_cd = {
        "Very Large Extent":       "#1B5E20",
        "Large Extent":            "#66BB6A",
        "Somewhat Large Extent":   "#AED581",
        "Moderate Extent":         "#FDD835",
        "Somewhat Small Extent":   "#FFA726",
        "Small Extent":            "#EF5350",
        "Very Small Extent":       "#B71C1C",
    }

    data_dict = {}
    for col in cd_cols:
        lbl = item_labels.get(col, col)
        s   = valid_series(data, col)
        vc  = s.map(cd_shorten).str.title().value_counts()
        data_dict[lbl] = {k: int(v) for k, v in vc.items()}

    scale_keys = [k for k in [
        "Very Large Extent","Large Extent","Somewhat Large Extent",
        "Moderate Extent","Somewhat Small Extent","Small Extent","Very Small Extent"
    ] if any(k in d for d in data_dict.values())]

    labels = [item_labels.get(c, c) for c in cd_cols]

    fig, ax = plt.subplots(figsize=(11, 5))
    fig.patch.set_facecolor("white")
    plt.subplots_adjust(top=0.85, bottom=0.10, left=0.22, right=0.68)
    wave_header(fig, wave_name, n_total)

    grouped_likert(ax, labels, data_dict, scale_keys, palette_cd,
                   "Perceived Cognitive Diversity (CD Items) — Team Differences")
    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def charts_oc(pdf, data, wave_name, n_total):
    """OC-1 through OC-5 as stacked horizontal bar."""
    oc_cols = [c for c in ["OC-1","OC-2","OC-3","OC-4","OC-5"] if c in data.columns]
    if not oc_cols:
        return

    item_labels = {
        "OC-1": "Coach / Captain keep me informed",
        "OC-2": "Knowledge sharing encouraged (actions)",
        "OC-3": "New knowledge encouraged",
        "OC-4": "Encouraged to voice disagreement",
        "OC-5": "Open communication (team-wide)",
    }

    data_dict = {}
    for col in oc_cols:
        lbl = item_labels.get(col, col)
        s   = valid_series(data, col)
        vc  = s.value_counts()
        data_dict[lbl] = {k: int(v) for k, v in vc.items()}

    labels = [item_labels.get(c, c) for c in oc_cols]
    scale  = [s for s in LIKERT_ORDER
              if any(s in d for d in data_dict.values())]

    fig, ax = plt.subplots(figsize=(11, 5.5))
    fig.patch.set_facecolor("white")
    plt.subplots_adjust(top=0.85, bottom=0.10, left=0.38, right=0.68)
    wave_header(fig, wave_name, n_total)

    grouped_likert(ax, labels, data_dict, scale, LIKERT_PALETTE,
                   "Team Cohesion — Open Communication (OC Items)")
    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def charts_ai_authority(pdf, data, wave_name, n_total):
    """Q24_1–5: AI authority by pen-testing phase."""
    phase_map = {
        "Q24_1": "Planning\n(Scope & Threat Models)",
        "Q24_2": "Scanning\n(Enumerate Vulnerabilities)",
        "Q24_3": "Execution\n(Exploit / Emulate Attacker)",
        "Q24_4": "Analysis\n(Business Impact)",
        "Q24_5": "Output\n(Reporting)",
    }
    cols = [c for c in phase_map if c in data.columns]
    if not cols:
        return

    # Individual bar per phase
    all_means = []
    all_labels = []
    for col in cols:
        s = pd.to_numeric(valid_series(data, col), errors="coerce").dropna()
        if s.empty:
            continue
        vc = s.astype(int).value_counts().reindex([1,2,3,4,5], fill_value=0)
        all_means.append(s.mean())
        all_labels.append(phase_map[col])

        fig, ax = fig_one("", None, wave_name, n_total)
        palette_ai = {1:"#1B5E20",2:"#66BB6A",3:"#FDD835",4:"#EF5350",5:"#B71C1C"}
        vbar(ax, vc.index.tolist(), vc.values.tolist(),
             [palette_ai[i] for i in vc.index],
             f"AI Authority — {phase_map[col]}\n(1 = No authority → 5 = Full authority)",
             ylabel="Count", pct=True, total=len(s))
        ax.annotate(f"Mean = {s.mean():.2f}  |  Median = {s.median():.1f}  |  n = {len(s)}",
                    xy=(0.5, -0.13), xycoords="axes fraction",
                    ha="center", fontsize=8, color=GREY, style="italic")
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # Summary: mean authority by phase
    if all_means:
        fig, ax = plt.subplots(figsize=(11, 5))
        fig.patch.set_facecolor("white")
        plt.subplots_adjust(top=0.85, bottom=0.22, left=0.08, right=0.96)
        wave_header(fig, wave_name, n_total)
        bars = ax.bar(np.arange(len(all_labels)), all_means,
                      color=[BLUE, TEAL, ORANGE, "#7B1FA2", RED_DARK],
                      edgecolor="white", width=0.55)
        ax.set_xticks(np.arange(len(all_labels)))
        ax.set_xticklabels(all_labels, fontsize=8.5, ha="center")
        ax.set_ylabel("Mean Authority Granted to AI (1–5)", fontsize=9)
        ax.set_ylim(0, 5.5)
        ax.set_title("AI Authority by Pen-Testing Phase — Mean Scores",
                     fontsize=10, fontweight="bold", color=NAVY, pad=8)
        ax.set_facecolor(BG)
        ax.axhline(3, linestyle="--", color=GREY, linewidth=0.8, alpha=0.6, label="Midpoint (3)")
        ax.legend(fontsize=8)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines[["top","right","left"]].set_visible(False)
        for bar, m in zip(bars, all_means):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.08,
                    f"{m:.2f}", ha="center", fontsize=9, fontweight="bold", color=NAVY)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def charts_ai_nps(pdf, data, wave_name, n_total):
    """Q27, Q28, Q29: AI teammate NPS."""
    nps_defs = [
        ("Q27", "AI as Teammate — Technical Findings"),
        ("Q28", "AI as Teammate — Report Writing"),
        ("Q29", "AI as Teammate — Presentation"),
    ]
    nps_data = [(col, lbl) for col, lbl in nps_defs if col in data.columns]
    if not nps_data:
        return

    # Combined figure: three gauges stacked
    fig, axes = plt.subplots(len(nps_data), 1,
                             figsize=(11, 2.5 * len(nps_data) + 1.5))
    if len(nps_data) == 1:
        axes = [axes]
    fig.patch.set_facecolor("white")
    wave_header(fig, wave_name, n_total)
    plt.subplots_adjust(top=0.90, bottom=0.08, hspace=0.65, left=0.05, right=0.75)

    for ax, (col, lbl) in zip(axes, nps_data):
        s = valid_series(data, col)
        nps_gauge(ax, s.tolist(), lbl)

    fig.suptitle("AI Teammate Value — NPS Recommendations",
                 fontsize=11, fontweight="bold", color=NAVY, y=0.97)
    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # Per-item 0-10 distribution
    for col, lbl in nps_data:
        if col not in data.columns:
            continue
        s = pd.to_numeric(valid_series(data, col), errors="coerce").dropna().astype(int)
        if s.empty:
            continue
        vc = s.value_counts().reindex(range(11), fill_value=0)
        fig, ax = fig_one("", None, wave_name, n_total)
        colors = ([RED_DARK]*7) + ([ORANGE]*2) + ([GREEN]*2)
        vbar(ax, vc.index.tolist(), vc.values.tolist(), colors,
             f"{lbl}\n(0–10 Raw Distribution)", ylabel="Count", pct=True, total=len(s))
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def charts_cptc5_career_nps(pdf, data, wave_name, n_total):
    """Career intent (Q30) and competition NPS (Q31)."""
    # Career intent
    if "Q30" in data.columns:
        s  = valid_series(data, "Q30")
        vc = s.value_counts()
        fig, ax = fig_one("", None, wave_name, n_total)
        hbar(ax, vc.index.tolist(), vc.values.tolist(),
             [GREEN, ORANGE, RED_DARK][:len(vc)],
             "Do you plan to pursue cybersecurity as a career?", total=len(s))
        add_missing_note(ax, len(s), n_total)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # Competition NPS
    if "Q31" in data.columns:
        s = valid_series(data, "Q31")
        fig, ax = fig_one("", None, wave_name, n_total)
        nps_gauge(ax, s.tolist(), "Recommend CPTC to a friend/colleague?")
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

        s_num = pd.to_numeric(s, errors="coerce").dropna().astype(int)
        vc = s_num.value_counts().reindex(range(11), fill_value=0)
        fig, ax = fig_one("", None, wave_name, n_total)
        colors = ([RED_DARK]*7) + ([ORANGE]*2) + ([GREEN]*2)
        vbar(ax, vc.index.tolist(), vc.values.tolist(), colors,
             "Competition NPS — Raw Score Distribution (0–10)",
             ylabel="Count", pct=True, total=len(s_num))
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def charts_cptc5_preparedness(pdf, data, wave_name, n_total):
    """Q4_1–Q4_6: preparedness sliders (0–100)."""
    prep_map = {
        "Q4_1": "Understanding the\nEnvironment",
        "Q4_2": "Understanding Competition\nRules",
        "Q4_3": "Understanding Your\nRole in the Team",
        "Q4_4": "Understanding Actions\nRequired",
        "Q4_5": "Understanding Professional\nCommunication",
        "Q4_6": "Understanding Ethical\nImplications",
    }
    cols = [c for c in prep_map if c in data.columns]
    if not cols:
        return

    # Combined box-plot summary
    all_vals = []
    all_labels = []
    for col in cols:
        s = pd.to_numeric(valid_series(data, col), errors="coerce").dropna()
        if s.empty:
            continue
        all_vals.append(s.tolist())
        all_labels.append(prep_map[col])

    if all_vals:
        fig, ax = plt.subplots(figsize=(11, 6))
        fig.patch.set_facecolor("white")
        plt.subplots_adjust(top=0.85, bottom=0.22, left=0.06, right=0.97)
        wave_header(fig, wave_name, n_total)
        bp = ax.boxplot(all_vals, patch_artist=True, vert=True,
                        medianprops=dict(color=RED_DARK, linewidth=2))
        for patch, color in zip(bp["boxes"], cycle_colors(len(all_vals))):
            patch.set_facecolor(color); patch.set_alpha(0.7)
        ax.set_xticks(range(1, len(all_labels)+1))
        ax.set_xticklabels(all_labels, fontsize=8, ha="center")
        ax.set_ylabel("Preparedness Score (0–100 slider)", fontsize=9)
        ax.set_title("Scenario Preparedness by Dimension — Distribution",
                     fontsize=10, fontweight="bold", color=NAVY, pad=8)
        ax.set_facecolor(BG)
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.spines[["top","right","left"]].set_visible(False)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)

    # Individual histograms
    for col in cols:
        s = pd.to_numeric(valid_series(data, col), errors="coerce").dropna()
        if s.empty:
            continue
        fig, ax = fig_one("", None, wave_name, n_total)
        histogram(ax, s.tolist(),
                  f"Preparedness — {prep_map[col]}",
                  "Slider value (0–100)", bins=20)
        add_missing_note(ax, len(s), n_total)
        pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def charts_scenario_iteration(pdf, data, wave_name, n_total):
    """Q17: willingness to describe another scenario."""
    if "Q17" not in data.columns:
        return
    s  = valid_series(data, "Q17")
    vc = s.value_counts()
    fig, ax = fig_one("", None, wave_name, n_total)
    hbar(ax, vc.index.tolist(), vc.values.tolist(),
         [BLUE if v == "Yes" else GREY for v in vc.index],
         "Willing to Describe Another Security Situation?", total=len(s))
    add_missing_note(ax, len(s), n_total)
    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


def charts_missing_overview(pdf, data, wave_name, n_total, skip_cols):
    """Horizontal bar showing % missing per question column."""
    question_cols = [c for c in data.columns if c not in skip_cols]
    if not question_cols:
        return

    missing_pct = []
    col_labels  = []
    for col in question_cols:
        s = data[col]
        n_missing = (s.isna() | (s.str.strip() == "")).sum()
        pct = n_missing / n_total * 100 if n_total > 0 else 0
        missing_pct.append(pct)
        col_labels.append(col)

    # Sort by missing % descending
    pairs = sorted(zip(missing_pct, col_labels), reverse=True)
    missing_pct = [p for p, _ in pairs]
    col_labels  = [l for _, l in pairs]

    fig_h = max(5, len(col_labels) * 0.28)
    fig = plt.figure(figsize=(11, min(fig_h, 14)))
    fig.patch.set_facecolor("white")
    ax = fig.add_subplot(111)
    plt.subplots_adjust(top=0.92, bottom=0.07, left=0.30, right=0.95)
    wave_header(fig, wave_name, n_total)

    y = np.arange(len(col_labels))
    colors_m = [RED_DARK if p > 50 else ORANGE if p > 20 else BLUE for p in missing_pct]
    bars = ax.barh(y, missing_pct, color=colors_m, edgecolor="white", height=0.65)
    ax.set_yticks(y)
    ax.set_yticklabels(col_labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel("% Missing / Not Answered", fontsize=9)
    ax.set_title("Response Completeness — % Missing per Question",
                 fontsize=10, fontweight="bold", color=NAVY, pad=8)
    ax.set_xlim(0, 105)
    ax.set_facecolor(BG)
    ax.grid(axis="x", linestyle="--", alpha=0.4)
    ax.spines[["top","right","left"]].set_visible(False)
    ax.axvline(20, color=ORANGE, linestyle=":", linewidth=1, alpha=0.7)
    ax.axvline(50, color=RED_DARK, linestyle=":", linewidth=1, alpha=0.7)
    for bar, pct in zip(bars, missing_pct):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f"{pct:.0f}%", va="center", fontsize=7.5, color=GREY)
    pdf.savefig(fig, bbox_inches="tight"); plt.close(fig)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  MAIN: BUILD ONE PDF PER WAVE                                               ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

META_COLS = {
    "StartDate","EndDate","Status","IPAddress","Progress",
    "Duration (in seconds)","Finished","RecordedDate","ResponseId",
    "RecipientLastName","RecipientFirstName","RecipientEmail",
    "ExternalReference","LocationLatitude","LocationLongitude",
    "DistributionChannel","UserLanguage",
}

# ── CPTC8 ─────────────────────────────────────────────────────────────────────
def build_cptc8():
    path = DATA_DIR / "CPTC8_13.56 (Text).csv"
    col_names, q_texts, data = load(path)
    n = len(data)
    out = OUT_DIR / "CPTC8_survey_charts.pdf"
    print(f"Building {out.name}  ({n} rows)…")

    with PdfPages(out) as pdf:
        save_title_page(pdf, "CPTC8  (2022–2023)", n,
            "Baseline survey wave. Core demographics, cognitive diversity (CD-1–4), "
            "differing abilities, and team cohesion (OC-1–5).")
        charts_missing_overview(pdf, data, "CPTC8", n, META_COLS)
        charts_demographics(pdf, data, {}, "CPTC8", n, consent_col="Consent")
        charts_experience(pdf, data, "CPTC8", n)
        charts_differing_abilities(pdf, data, "CPTC8", n)
        charts_cd(pdf, data, "CPTC8", n)
        charts_oc(pdf, data, "CPTC8", n)
    print(f"  → {out}")


# ── CPTC9 ─────────────────────────────────────────────────────────────────────
def build_cptc9():
    path = DATA_DIR / "CPTC9_13.55 (Text).csv"
    col_names, q_texts, data = load(path)
    n = len(data)
    out = OUT_DIR / "CPTC9_survey_charts.pdf"
    print(f"Building {out.name}  ({n} rows)…")

    with PdfPages(out) as pdf:
        save_title_page(pdf, "CPTC9  (2023–2024)", n,
            "Same instrument as CPTC8. Demographics, cognitive diversity, "
            "differing abilities, and team cohesion.")
        charts_missing_overview(pdf, data, "CPTC9", n, META_COLS)
        charts_demographics(pdf, data, {}, "CPTC9", n)
        charts_experience(pdf, data, "CPTC9", n)
        charts_differing_abilities(pdf, data, "CPTC9", n)
        charts_cd(pdf, data, "CPTC9", n)
        charts_oc(pdf, data, "CPTC9", n)
    print(f"  → {out}")


# ── CPTC10 ────────────────────────────────────────────────────────────────────
def build_cptc10():
    path = DATA_DIR / "CPTC10_13.54 (Text).csv"
    col_names, q_texts, data = load(path)
    n = len(data)
    out = OUT_DIR / "CPTC10_survey_charts.pdf"
    print(f"Building {out.name}  ({n} rows)…")

    with PdfPages(out) as pdf:
        save_title_page(pdf, "CPTC10  (2024–2025)", n,
            "Adds five AI authority items (Q24_1–5, 1–5 scale) to the "
            "CPTC8/9 core instrument.")
        charts_missing_overview(pdf, data, "CPTC10", n, META_COLS)
        charts_demographics(pdf, data, {}, "CPTC10", n)
        charts_experience(pdf, data, "CPTC10", n)
        charts_differing_abilities(pdf, data, "CPTC10", n)
        charts_cd(pdf, data, "CPTC10", n)
        charts_oc(pdf, data, "CPTC10", n)
        charts_ai_authority(pdf, data, "CPTC10", n)
    print(f"  → {out}")


# ── CPTC11 ────────────────────────────────────────────────────────────────────
def build_cptc11():
    # Use 13_52 as primary (both files are identical; 13_55 is a duplicate export)
    path = DATA_DIR / "CPTC11_13.52 (Text).csv"
    col_names, q_texts, data = load(path)
    n = len(data)
    out = OUT_DIR / "CPTC11_survey_charts.pdf"
    print(f"Building {out.name}  ({n} rows)…")

    with PdfPages(out) as pdf:
        save_title_page(pdf, "CPTC11  (2025)", n,
            "Adds AI teammate NPS items (Q27–Q29) and qualitative AI experience "
            "(Q30 free text). Note: CPTC11_13_55 is a duplicate export of this wave.")
        charts_missing_overview(pdf, data, "CPTC11", n, META_COLS)
        charts_demographics(pdf, data, {}, "CPTC11", n)
        charts_experience(pdf, data, "CPTC11", n)
        charts_differing_abilities(pdf, data, "CPTC11", n)
        charts_cd(pdf, data, "CPTC11", n)
        charts_ai_authority(pdf, data, "CPTC11", n)
        charts_ai_nps(pdf, data, "CPTC11", n)
        charts_oc(pdf, data, "CPTC11", n)
    print(f"  → {out}")


# ── CPTC5 ────────────────────────────────────────────────────────────────────
def build_cptc5():
    path = DATA_DIR / "CPTC_13.57 (Text).csv"
    col_names, q_texts, data = load(path)
    n = len(data)
    out = OUT_DIR / "CPTC5_survey_charts.pdf"
    print(f"Building {out.name}  ({n} rows)…")

    # Rename CPTC5 cols to canonical names for reuse of shared chart functions
    rename = {
        "Q23": "Consent", "Q24": "Gender", "Q25": "Age",
        "Q26": "Formal Education", "Q27": "Degree Status", "Q28": "Major",
        "Q29_1": "Experience_1", "Q29_4": "Experience_2", "Q29_5": "Experience_3",
    }
    data = data.rename(columns=rename)

    with PdfPages(out) as pdf:
        save_title_page(pdf, "CPTC5  (2020)", n,
            "Entirely different instrument: scenario-based cognitive walkthrough. "
            "Larger sample (N=401). No CD-2–4, differing abilities, or OC items. "
            "New: career intent, competition NPS, 6-dimension preparedness sliders.")
        charts_missing_overview(pdf, data, "CPTC5", n, META_COLS)
        charts_demographics(pdf, data, {}, "CPTC5", n, consent_col="Consent")
        charts_experience(pdf, data, "CPTC5", n,
                          extra_cols=[
                              ("Q29_6", "Years Believed Needed to Become Effective Pen Tester", "Years", False),
                              ("Q29_7", "Hours/Week on Required Cybersecurity Exercises", "Hours", False),
                              ("Q29_8", "Hours/Week on Voluntary Cybersecurity Exercises", "Hours", False),
                          ])
        charts_cptc5_career_nps(pdf, data, "CPTC5", n)
        charts_cptc5_preparedness(pdf, data, "CPTC5", n)
        charts_scenario_iteration(pdf, data, "CPTC5", n)
    print(f"  → {out}")


# ── Run all ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  CPTC Survey Visualization Generator")
    print("=" * 55)
    build_cptc5()
    build_cptc8()
    build_cptc9()
    build_cptc10()
    build_cptc11()
    print("\nAll PDFs written to:", OUT_DIR)
