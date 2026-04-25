from data_preprocessing import load_and_prepare
from rq1_mixed_model import run_rq1
from rq2_regression import run_rq2
from rq3_anova import run_rq3


if __name__ == "__main__":
    filepath = "merged_survey_data/merged_waves_numeric.csv"

    df = load_and_prepare(filepath)

    # Run models
    # run_rq1(df)
    run_rq2(df)
    run_rq3(df)