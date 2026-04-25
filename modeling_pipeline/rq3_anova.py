from scipy.stats import f_oneway
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import pandas as pd


def run_rq3(df):
    print("\n=== RQ3 ANOVA: Cohesion ===")

    # Ensure cohesion is numeric and groups are non-missing
    df = df.copy()
    df['cohesion'] = pd.to_numeric(df.get('cohesion'), errors='coerce')
    df['AI_usage_group'] = df.get('AI_usage_group')
    df = df.dropna(subset=['cohesion', 'AI_usage_group'])

    # Convert group labels to strings (avoid mixed types)
    df['AI_usage_group'] = df['AI_usage_group'].astype(str).str.strip()

    # Prepare groups for ANOVA
    grouped = [g['cohesion'] for _, g in df.groupby('AI_usage_group') if len(g) > 0]
    if len(grouped) < 2:
        raise ValueError('RQ3: need at least two AI_usage_group levels with data to run ANOVA')

    f_stat, p_val = f_oneway(*grouped)

    print(f"F-statistic: {f_stat}, p-value: {p_val}")

    print("\n--- Tukey HSD ---")
    try:
        tukey = pairwise_tukeyhsd(
            endog=df['cohesion'],
            groups=df['AI_usage_group'],
            alpha=0.05
        )
        print(tukey)
    except Exception as e:
        raise RuntimeError(f"Tukey HSD failed: {e}") from e

    return f_stat, p_val, tukey 