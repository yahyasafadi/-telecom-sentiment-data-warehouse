import pandas as pd
import os

input_dir = r"C:\Users\moham\Desktop\Docker\data\raw"
output_dir = r"C:\Users\moham\Desktop\Docker\data\dw_output"
os.makedirs(output_dir, exist_ok=True)

df_rev = pd.concat([pd.read_csv(f"{input_dir}\\{op}\\cleaned_reviews.csv").assign(operateur_name=op) for op in ['IAM', 'Orange', 'INWI'] if os.path.exists(f"{input_dir}\\{op}\\cleaned_reviews.csv")], ignore_index=True)
df_ag = pd.concat([pd.read_csv(f"{input_dir}\\{op}\\data_agences_cleaned.csv").assign(operateur_name=op) for op in ['IAM', 'Orange', 'INWI'] if os.path.exists(f"{input_dir}\\{op}\\data_agences_cleaned.csv")], ignore_index=True)

dims = {
    'operateur': pd.DataFrame({'operateur_id': [1,2,3], 'operateur_name': ['IAM','Orange','INWI']}),
    'ville': df_ag[['ville']].drop_duplicates().dropna().assign(ville_id=lambda x: range(1, len(x)+1)),
    'agence': df_ag[['num_agence', 'nom_agence', 'adresse']].drop_duplicates('num_agence').assign(agence_id=lambda x: range(1, len(x)+1)),
    'temps': df_rev[['review_year', 'review_month', 'review_day']].drop_duplicates().dropna().astype(int).sort_values(['review_year','review_month','review_day']).assign(temps_id=lambda x: range(1, len(x)+1)),
    'users': df_rev[['Name']].drop_duplicates().dropna().assign(user_id=lambda x: range(1, len(x)+1)),
    'topic': df_rev[['topic']].drop_duplicates().dropna().assign(topic_id=lambda x: range(1, len(x)+1)),
    'reviews': df_rev[['Comment', 'sentiment_score']].assign(review_id=lambda x: range(1, len(x)+1))
}

fact = df_rev.assign(review_id=range(1, len(df_rev)+1))
for df in [dims['temps'], dims['users'], dims['topic'], dims['operateur'], df_ag[['num_agence', 'ville']].drop_duplicates(), dims['agence'], dims['ville']]:
    fact = fact.merge(df, how='left')

for name, df in dims.items(): df.to_csv(f"{output_dir}\\dim_{name}.csv", index=False)
fact[['review_id', 'agence_id', 'temps_id', 'user_id', 'topic_id', 'ville_id', 'operateur_id', 'sentiment_score', 'comment_length']].to_csv(f"{output_dir}\\fact_reviews.csv", index=False)