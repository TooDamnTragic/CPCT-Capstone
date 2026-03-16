import pandas as pd, csv, json

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

"""
TODO: Build a single canonical merge function
"""

"""
TODO: Separate free-text columns before any numeric processing.
"""