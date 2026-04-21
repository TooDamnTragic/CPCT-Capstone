#!/usr/bin/env python3
'''
The purpose of this script is to merge the cleaned dataframes from each wave into a single dataframe for analysis. This involves:
- Loading the cleaned numeric dataframes for each wave.
- Merging them on the common columns (e.g. respondent ID, demographic variables).
- Saving the merged dataframe for analysis.
'''
import pandas as pd

def load_cleaned_data(wave):
    return pd.read_csv(f'cleaned/Nums_CPTC{wave}_cleaned_numeric.csv')

def merge_waves(wave_dfs):
    # Merge multiple waves while avoiding duplicate columns.
    # Strategy: set 'ResponseId' as index on each dataframe, concatenate
    # rows, then group by ResponseId taking the first non-null value for
    # each column. This preserves every respondent and avoids creating
    # duplicate suffixed columns.
    dfs = [df.set_index('ResponseId') for df in wave_dfs]
    if not dfs:
        return pd.DataFrame()
    concatenated = pd.concat(dfs, axis=0, sort=False)
    # For each ResponseId, take the first non-null value per column
    merged_df = concatenated.groupby(level=0, sort=False).first().reset_index()
    return merged_df

def main():
    wave_dfs = []

    # Handle loading wave 5 separatetly
    df = load_cleaned_data(5)
    wave_dfs.append(df)

    # Load waves 8-11
    for wave in range(8, 12):  # Assuming waves 8 to 11
        df = load_cleaned_data(wave)
        wave_dfs.append(df)
    
    merged_df = merge_waves(wave_dfs)
    merged_df.to_csv('cleaned/merged_waves_numeric.csv', index=False)

if __name__ == "__main__":
    main()