import pandas as pd
import statsmodels.formula.api as smf


def run_rq1(df):
    import statsmodels.formula.api as smf

    phase_cols = ['Q24_1','Q24_2','Q24_3','Q24_4','Q24_5']

    
    # Total rows in dataset
    total_rows = len(df)

    # Rows with at least one phase value
    any_phase = df[phase_cols].notna().any(axis=1).sum()

    # Rows with ALL phase values (this is what RQ1 actually uses)
    complete_cases = df[phase_cols].notna().all(axis=1).sum()

    # Rows that will be dropped
    dropped_rows = total_rows - complete_cases

    print(f"Total rows: {total_rows}")
    print(f"Rows with ANY phase data: {any_phase}")
    print(f"Rows with COMPLETE phase data (used in RQ1): {complete_cases}")
    print(f"Rows dropped for RQ1: {dropped_rows}")

    # Keep only rows with full phase data
    df_rq1 = df[['ResponseId'] + phase_cols].dropna()

    # Reshape
    df_long = df_rq1.melt(
        id_vars='ResponseId',
        value_vars=phase_cols,
        var_name='Phase',
        value_name='Authority'
    )

    print("\nObservations per phase:")
    print(df_long['Phase'].value_counts())

    # Map labels
    phase_map = {
        'Q24_1': 'Planning',
        'Q24_2': 'Scanning',
        'Q24_3': 'Execution',
        'Q24_4': 'Analysis',
        'Q24_5': 'Output'
    }
    df_long['Phase'] = df_long['Phase'].map(phase_map)

    # # Safety check
    # if df_long['Phase'].nunique() < 2:
    #     raise ValueError("Not enough phase variation for mixed model.")

    # Ensure Authority is numeric (patsy/statsmodels requires numeric endog)
    df_long['Authority'] = pd.to_numeric(df_long['Authority'], errors='coerce')
    # Drop rows where coercion produced NaN
    df_long = df_long.dropna(subset=['Authority'])
    df_long['Authority'] = df_long['Authority'].astype(float)

    # Ensure Phase is treated as categorical
    df_long['Phase'] = df_long['Phase'].astype('category')

    model = smf.mixedlm(
        "Authority ~ C(Phase)",
        df_long,
        groups=df_long["ResponseId"]
    ).fit()

    print(model.summary())
    return model

run_rq1(pd.read_csv("merged_survey_data/RQ1merged_waves_numeric.csv"))