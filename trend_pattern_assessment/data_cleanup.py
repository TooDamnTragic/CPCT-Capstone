#!/usr/bin/env python3
import pandas as pd, csv, json
from qid_crosswalk import QID_CROSSWALK, CANONICAL_NAME, QUESTION_TEXT

def load_survey(path):
    """
    Loader that strips the double-header correctly.
        - Every file has two header rows. Row 1 is the column name, row 2 is either the full question text or a Qualtrics ImportId JSON blob.
        - The fix is to read both rows explicitly, store row 2 as a separate question-text dictionary keyed by column name, then pass skiprows=[1] when loading data.
    """
    with open(path, encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        col_names = next(reader)
        q_text_row = next(reader)
    question_map = {col: label for col, label in zip(col_names, q_text_row)}
    df = pd.read_csv(path, skiprows=[1], encoding='utf-8-sig')
    return df, question_map

CD_RECODE = {'1':7, '2':6, '3':5, '4':4, '17':3, '18':2, '19':1}
CD_COLS = ['CD-1', 'CD-2', 'CD-3', 'CD-4']

def recode_cd(df):
    """
    The CD items (CD-1 thru CD-4) in the Nums_ files use codes 1-4 and 17-19, which need to be recoded to a common 1-7 scale.
        - The direction is inverted, meaning code 1 = max CD and code 7 = min CD.
    """
    for col in CD_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str).map(CD_RECODE)
    return df

"""
TODO: Handle the CPTC5 Q4 Slider Scale
- The preparedness items Q4_1-q4_6 are continuous sliders 0-100, not Likert 1-5. All other Likert items in the other waves are ordinal 1-5.
  If we intend to pool these waves, we need to either just keep them separate or normalise Q4 to 0–1 before any comparison. 
  Label these columns with their scale type in a metadata dictionary at load time so downstream scripts don't accidentally treat them as Likert.
"""
def normalise_q4(df):
    q4_cols = [col for col in df.columns if col.startswith('Q4_')]
    for col in q4_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce') / 100.0
    return df

"""
TODO: Separate free-text columns before any numeric processing.

Several columns contain open-ended text responses that will break numeric pipelines: `Major`, `Q3`, `Q5`–`Q9`, `Q11`, `Q12`, `Q15`, `Q16`, `Q30` (CPTC11 AI experience), and `Q9 - Topics`. Split these into a separate `df_text` frame keyed on `ResponseId` at load time and keep `df_numeric` containing only scale/ordinal/binary items. This also makes it easy to run NLP on the text columns independently.

Note that the scenario text columns in CPTC5 have **43–75% missingness** (cascading dropout as respondents exit the scenario loop early), so any text analysis should report N per question, not just overall N.
"""
def split_text(df):
    text_cols = ['Major', 'Q3', 'Q5', 'Q6', 'Q7', 'Q8', 'Q9', 'Q11', 'Q12', 'Q15', 'Q16', 'Q30', 'Q9 - Topics']
    df_text = df[['ResponseId'] + [col for col in text_cols if col in df.columns]]
    df_numeric = df.drop(columns=[col for col in text_cols if col in df.columns])
    return df_numeric, df_text

"""
TODO: Use QID_CROSSWALK to map column names to canonical question names.
"""
def map_to_canonical(df, question_map):
    """
    Map column names to canonical question names using the QID_CROSSWALK.
        - This allows us to pool items across waves that have different column names but the same underlying question.
        - The QID_CROSSWALK is a dictionary mapping (wave, column_name) to a canonical question name. We can use this to rename columns in each wave to their canonical names.
    """
    rename_map = {}
    for col in df.columns:
        qid = (col, question_map.get(col, ''))
        if qid in QID_CROSSWALK:
            rename_map[col] = QID_CROSSWALK[qid][CANONICAL_NAME]
    df = df.rename(columns=rename_map)
    return df

def main():
    # CPTC 5
    df, question_map = load_survey('raw csvs/CPTC_13.57 (Nums).csv')
    df = recode_cd(df)
    df = normalise_q4(df)
    df_numeric, df_text = split_text(df)
    df_numeric = map_to_canonical(df_numeric, question_map)
    # Save cleaned data
    df_numeric.to_csv('cleaned/Nums_CPTC5_cleaned_numeric.csv', index=False)
    df_text.to_csv('cleaned/Nums_CPTC5_cleaned_text.csv', index=False)

    # CPTC 8
    df, question_map = load_survey('raw csvs/CPTC8_13.56 (Nums).csv')
    df = recode_cd(df)
    df = normalise_q4(df)
    df_numeric, df_text = split_text(df)
    df_numeric = map_to_canonical(df_numeric, question_map)
    # Save cleaned data
    df_numeric.to_csv('cleaned/Nums_CPTC8_cleaned_numeric.csv', index=False)
    df_text.to_csv('cleaned/Nums_CPTC8_cleaned_text.csv', index=False)

    # CPTC 9
    df, question_map = load_survey('raw csvs/CPTC9_13.55 (Nums).csv')
    df = recode_cd(df)
    df = normalise_q4(df)
    df_numeric, df_text = split_text(df)
    df_numeric = map_to_canonical(df_numeric, question_map)
    # Save cleaned data
    df_numeric.to_csv('cleaned/Nums_CPTC9_cleaned_numeric.csv', index=False)
    df_text.to_csv('cleaned/Nums_CPTC9_cleaned_text.csv', index=False)

    # CPTC 10
    df, question_map = load_survey('raw csvs/CPTC10_13.54 (Nums).csv')
    df = recode_cd(df)
    df = normalise_q4(df)
    df_numeric, df_text = split_text(df)
    df_numeric = map_to_canonical(df_numeric, question_map)
    # Save cleaned data
    df_numeric.to_csv('cleaned/Nums_CPTC10_cleaned_numeric.csv', index=False)
    df_text.to_csv('cleaned/Nums_CPTC10_cleaned_text.csv', index=False)

    # CPTC 11
    df, question_map = load_survey('raw csvs/CPTC11_13.55.csv')
    df = recode_cd(df)
    df = normalise_q4(df)
    df_numeric, df_text = split_text(df)
    df_numeric = map_to_canonical(df_numeric, question_map)
    # Save cleaned data
    df_numeric.to_csv('cleaned/Nums_CPTC11_cleaned_numeric.csv', index=False)
    df_text.to_csv('cleaned/Nums_CPTC11_cleaned_text.csv', index=False)



if __name__ == "__main__":    main()