from data_preprocessing import load_and_prepare
from rq1_mixed_model import run_rq1
from rq2_regression import run_rq2
from rq3_anova import run_rq3


if __name__ == "__main__":
    filepath = "merged_survey_data/merged_waves_numeric.csv"
    rq1_filepath = "merged_survey_data/RQ1merged_waves_numeric.csv"

    df = load_and_prepare(filepath)
    df_rq1 = load_and_prepare(rq1_filepath)
    

    # Run models
    run_rq1(df_rq1)
    run_rq2(df)
    run_rq3(df)