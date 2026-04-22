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
import json

def load_merged_data():
    # Read the merged data file located alongside this script
    data_path = Path(__file__).parent / 'merged_waves_numeric.csv'
    return pd.read_csv(data_path)


def build_merged_pdf(out_path: str | Path | None = None, bins: int = 20):
    """Generate a multi-page PDF with a histogram per numeric column.

    - `out_path`: optional output path for the PDF. Defaults to
      `merged_waves_numeric_charts.pdf` next to this script.
    - `bins`: maximum number of histogram bins.
    """
    df = load_merged_data()
    n_rows = len(df)

    # Load QID -> canonical mapping from crosswalk JSON
    def load_qid_crosswalk():
        # crosswalk lives at repo root next to this script's parent
        candidates = [Path(__file__).parent.parent / 'cptc_qid_crosswalk.json',
                      Path(__file__).parent / '..' / 'cptc_qid_crosswalk.json']
        for p in candidates:
            p = Path(p)
            if p.exists():
                try:
                    with p.open('r', encoding='utf-8') as fh:
                        data = json.load(fh)
                except Exception:
                    return {}

                mapping = {}
                for entry in data:
                    question = entry.get('question_text') or entry.get('qid')
                    # Map the qid key itself
                    qid = entry.get('qid')
                    if qid:
                        mapping[qid] = question
                    # Map any wave-specific column names to canonical
                    for v in (entry.get('col_by_wave') or {}).values():
                        if v:
                            mapping[v] = question
                    # Map canonical to itself
                    if question:
                        mapping[question] = question
                return mapping
        return {}

    qmap = load_qid_crosswalk()

    # Identify numeric columns (coerceable to numbers with at least one non-NaN)
    numeric_cols = []
    for col in df.columns:
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        if not s.empty:
            numeric_cols.append(col)

    out = Path(out_path) if out_path else Path(__file__).parent / "merged_waves_numeric_charts.pdf"
    print(f"Building {out.name}  ({n_rows} rows, {len(numeric_cols)} numeric columns)...")

    with PdfPages(out) as pdf:
        # Title page
        fig = plt.figure(figsize=(11, 8.5))
        fig.patch.set_facecolor("white")
        ax = fig.add_subplot(111)
        ax.axis("off")
        ax.text(0.5, 0.6, "Merged Waves — Numeric Variables",
                ha="center", va="center", fontsize=28, fontweight="bold", color="#2E75B6", transform=ax.transAxes)
        ax.text(0.5, 0.45, f"Rows: {n_rows}   |   Numeric columns: {len(numeric_cols)}",
                ha="center", va="center", fontsize=12, color="#555555", transform=ax.transAxes)
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)

        # One histogram per numeric column
        for col in numeric_cols:
            s = pd.to_numeric(df[col], errors="coerce").dropna()
            values = s.values
            if values.size == 0:
                continue

            fig, ax = plt.subplots(figsize=(11, 5))
            ax.hist(values, bins=min(bins, 30, int(np.unique(values).size)),
                    color="#2E75B6", edgecolor="white", linewidth=0.6)
            # Title: use canonical name when available
            display_title = qmap.get(col, col)
            ax.set_title(f"{display_title}", fontsize=12, fontweight="bold", color="#1F3864")
            ax.set_xlabel("Value", fontsize=10)
            ax.set_ylabel("Count", fontsize=10)
            ax.set_facecolor("#FFFFFF")
            ax.grid(axis="y", linestyle="--", alpha=0.3)

            mn = np.mean(values)
            md = np.median(values)
            ax.axvline(mn, color="#8B1A1A", linestyle="--", linewidth=1.2, label=f"Mean {mn:.2f}")
            ax.axvline(md, color="#1B7A6E", linestyle=":", linewidth=1.2, label=f"Median {md:.2f}")
            ax.legend(fontsize=9)

            ax.text(0.99, 0.01, f"n = {values.size}", transform=ax.transAxes,
                    ha="right", va="bottom", fontsize=9, color="#757575")

            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)

    print(f"  → {out}")


if __name__ == "__main__":
    build_merged_pdf()

