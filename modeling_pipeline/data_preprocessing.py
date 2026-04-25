import pandas as pd


def load_and_prepare(filepath):
    df = pd.read_csv(filepath)

    # Remove metadata row
    df = df.iloc[1:].copy()

    # Convert to numeric
    df = df.apply(pd.to_numeric, errors='coerce')

    # --- Construct variables ---
    # AI Authority
    df['AI_authority_mean'] = df[['Q24_1','Q24_2','Q24_3','Q24_4','Q24_5']].mean(axis=1)

    # AI Teammate Value
    df['AI_teammate_value_mean'] = df[['Q27','Q28','Q29']].mean(axis=1)

    # Cohesion
    df['cohesion'] = df[['OC-1','OC-2','OC-3','OC-4','OC-5']].mean(axis=1)

    # Cognitive Diversity
    df['cognitive_diversity'] = df[['CD-1','CD-2','CD-3','CD-4']].mean(axis=1)

    # AI Role category
    def classify_ai_role(x):
        if pd.isna(x):
            return None
        elif x <= 2:
            return "Tool"
        elif x <= 3.5:
            return "Collaborator"
        else:
            return "Teammate"

    df['AI_role'] = df['AI_authority_mean'].apply(classify_ai_role)

    # AI usage group
    df['AI_usage_group'] = pd.qcut(
        df['AI_authority_mean'],
        3,
        labels=['Low','Medium','High']
    )

    return df