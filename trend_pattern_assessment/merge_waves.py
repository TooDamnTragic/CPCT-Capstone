#!/usr/bin/env python3
'''
The purpose of this script is to merge the cleaned dataframes from each wave into a single dataframe for analysis. This involves:
- Loading the cleaned numeric dataframes for each wave.
- Merging them on the common columns (e.g. respondent ID, demographic variables).
- Saving the merged dataframe for analysis.
'''
import json
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_crosswalk(path: str | Path = ROOT / 'cptc_qid_crosswalk.json') -> list:
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_cleaned_data(wave: int) -> pd.DataFrame:
    path = ROOT / 'cleaned' / f'Nums_CPTC{wave}_cleaned_numeric.csv'
    return pd.read_csv(path)


def build_rename_map_for_wave(crosswalk: list, wave: int) -> dict:
    # Build mapping from original column name (in that wave file) -> canonical name
    # Try multiple CPTC keys for wave 11 if present in crosswalk
    candidates = []
    if wave == 11:
        candidates = ['CPTC11_55', 'CPTC11_52', 'CPTC11']
    else:
        candidates = [f'CPTC{wave}']

    rename_map = {}
    for entry in crosswalk:
        canonical = entry.get('canonical')
        col_by_wave = entry.get('col_by_wave', {}) or {}
        for key in candidates:
            colname = col_by_wave.get(key)
            if colname and isinstance(colname, str):
                rename_map[colname] = canonical
                break
    return rename_map


def apply_case_insensitive_rename(df: pd.DataFrame, rename_map: dict) -> pd.DataFrame:
    # Match keys in rename_map to actual df columns case-insensitively and trim whitespace
    actual_renames = {}
    cols_lower = {c.strip().lower(): c for c in df.columns}
    for orig, canonical in rename_map.items():
        if orig in df.columns:
            actual_renames[orig] = canonical
            continue
        key = orig.strip().lower()
        actual = cols_lower.get(key)
        if actual:
            actual_renames[actual] = canonical
    if actual_renames:
        df = df.rename(columns=actual_renames)
    return df


def merge_waves(wave_dfs: list) -> pd.DataFrame:
    # Ensure 'ResponseId' exists in each dataframe (after renaming)
    dfs = []
    for df in wave_dfs:
        if 'ResponseId' not in df.columns:
            # Try common alternatives
            alt = None
            for candidate in ['_recordId', 'Response Id', 'responseid']:
                for c in df.columns:
                    if c.strip().lower() == candidate.strip().lower():
                        alt = c
                        break
                if alt:
                    break
            if alt:
                df = df.rename(columns={alt: 'ResponseId'})
        dfs.append(df.set_index('ResponseId'))

    if not dfs:
        return pd.DataFrame()

    concatenated = pd.concat(dfs, axis=0, sort=False)
    merged_df = concatenated.groupby(level=0, sort=False).first().reset_index()
    return merged_df


def main():
    crosswalk = load_crosswalk()

    wave_dfs = []

    # Load wave 5 then 8-11 (same waves as before)
    waves = [5] + list(range(8, 12))
    for wave in waves:
        df = load_cleaned_data(wave)
        rename_map = build_rename_map_for_wave(crosswalk, wave)
        df = apply_case_insensitive_rename(df, rename_map)
        # After renaming, ensure ResponseId is present
        if 'ResponseId' not in df.columns:
            # try to infer from crosswalk mapping if available
            # find canonical->orig mapping for ResponseId
            for entry in crosswalk:
                if entry.get('canonical') == 'ResponseId':
                    col_by_wave = entry.get('col_by_wave', {}) or {}
                    # check same candidate keys as build_rename_map_for_wave
                    candidates = ['CPTC11_55', 'CPTC11_52', 'CPTC11'] if wave == 11 else [f'CPTC{wave}']
                    for key in candidates:
                        orig = col_by_wave.get(key)
                        if orig:
                            # case-insensitive match
                            for c in df.columns:
                                if c.strip().lower() == orig.strip().lower():
                                    df = df.rename(columns={c: 'ResponseId'})
                                    break
                            break
        wave_dfs.append(df)

    merged_df = merge_waves(wave_dfs)
    outpath = ROOT / 'cleaned' / 'merged_waves_numeric.csv'
    merged_df.to_csv(outpath, index=False)


if __name__ == "__main__":
    main()