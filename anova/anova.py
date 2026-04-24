import pandas as pd
import scipy.stats as stats

# Load dataset
df = pd.read_csv('merged_survey_data\merged_waves_numeric.csv')

# Remove metadata row
df_clean = df.iloc[1:].copy()

# Convert to numeric
df_numeric = df_clean.apply(pd.to_numeric, errors='coerce')

# Drop empty columns
df_numeric = df_numeric.dropna(axis=1, how='all')

# Group by WaveYear
grouped = df_numeric.groupby('WaveYear')

results = []

for col in df_numeric.columns:
    if col == 'WaveYear':
        continue
    
    groups = [group[col].dropna().values 
              for _, group in grouped 
              if len(group[col].dropna()) > 1]
    
    if len(groups) > 1:
        f_stat, p_val = stats.f_oneway(*groups)
        results.append((col, f_stat, p_val))

anova_results = pd.DataFrame(results, columns=['Variable', 'F-statistic', 'p-value'])
anova_results = anova_results.sort_values('p-value')

print(anova_results.head(20))