import statsmodels.formula.api as smf


def run_rq2(df):
    model = smf.ols(
        "AI_authority_mean ~ cohesion + cognitive_diversity + Experience_2 + WaveYear",
        data=df
    ).fit()

    print("\n=== RQ2 Regression Results ===")
    print(model.summary())

    return model