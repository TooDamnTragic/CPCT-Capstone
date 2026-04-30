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

# output all results to CSV
anova_results.to_csv('anova_results.csv', index=False)

df['AI_authority_mean'] = df[['Q24_1','Q24_2','Q24_3','Q24_4','Q24_5']].mean(axis=1) # average of 5 questions about AI authority

def classify_ai_role(x):
    if x <= 2:
        return "Tool"
    elif x <= 3.5:
        return "Collaborator"
    else:
        return "Teammate"

df['AI_role'] = df['AI_authority_mean'].apply(classify_ai_role)

df['AI_teammate_value_mean'] = df[['Q27','Q28','Q29']].mean(axis=1) # average of 3 questions about AI teammate value

df['cohesion'] = df[['OC-1','OC-2','OC-3','OC-4','OC-5']].mean(axis=1) # average of 5 questions about organizational cohesion

df['cognitive_diversity'] = df[['CD-1','CD-2','CD-3','CD-4']].mean(axis=1) # average of 4 questions about cognitive diversity

df['self_diversity'] = df[['Differing abilities_1','Differing abilities_2','Differing abilities_3']].mean(axis=1) # average of 3 questions about self-perceived diversity

AI_authority_mean ~ cohesion + cognitive_diversity

# OR 

AI_teammate_value_mean ~ cohesion + cognitive_diversity

df['AI_usage_group'] = pd.qcut(df['AI_authority_mean'], 3, labels=['Low','Medium','High'])

df['AI_usage_group'] = pd.qcut(df['AI_teammate_value_mean'], 3, labels=['Low','Medium','High'])

from scipy.stats import f_oneway

groups = [g['cohesion'].dropna() for _, g in df.groupby('AI_usage_group')]
f_oneway(*groups)

