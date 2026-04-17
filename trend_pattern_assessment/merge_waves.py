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
    # Assuming all dataframes have a common 'respondent_id' column to merge on
    merged_df = wave_dfs[0]
    for df in wave_dfs[1:]:
        merged_df = pd.merge(merged_df, df, on='respondent_id', how='outer')
    return merged_df

def main():
    wave_dfs = []
    for wave in range(5, 12):  # Assuming waves 5 to 11
        df = load_cleaned_data(wave)
        wave_dfs.append(df)
    
    merged_df = merge_waves(wave_dfs)
    merged_df.to_csv('cleaned/merged_waves_numeric.csv', index=False)

if __name__ == "__main__":
    main()