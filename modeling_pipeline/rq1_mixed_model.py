import pandas as pd
import statsmodels.formula.api as smf


def run_rq1(df):
    import statsmodels.formula.api as smf

    phase_cols = ['Q24_1','Q24_2','Q24_3','Q24_4','Q24_5']

    # Keep only rows with full phase data
    df_rq1 = df[['ResponseId'] + phase_cols].dropna()

    # Reshape
    df_long = df_rq1.melt(
        id_vars='ResponseId',
        value_vars=phase_cols,
        var_name='Phase',
        value_name='Authority'
    )

    # Map labels
    phase_map = {
        'Q24_1': 'Planning',
        'Q24_2': 'Scanning',
        'Q24_3': 'Execution',
        'Q24_4': 'Analysis',
        'Q24_5': 'Output'
    }
    df_long['Phase'] = df_long['Phase'].map(phase_map)

    # Safety check
    if df_long['Phase'].nunique() < 2:
        raise ValueError("Not enough phase variation for mixed model.")

    model = smf.mixedlm(
        "Authority ~ Phase",
        df_long,
        groups=df_long["ResponseId"]
    ).fit()

    print(model.summary())
    return model