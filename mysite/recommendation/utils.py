# recommendation/utils.py

import pandas as pd
from joblib import load
from ast import literal_eval

# Load mô hình và dữ liệu
predicted_df = load('recommendation/models_data/predicted_ratings_df.joblib')
products_df = pd.read_csv('recommendation/models_data/products_with_clusters.csv')
rules_df = pd.read_csv('recommendation/models_data/association_rules.csv')

def predict_rating(user_id, item_id):
    try:
        return round(predicted_df.loc[user_id, item_id], 2)
    except:
        return None

def recommend_by_cluster(item_id):
    if item_id not in products_df['item_id'].values:
        return []
    cluster_id = products_df[products_df['item_id'] == item_id]['cluster'].values[0]
    return products_df[products_df['cluster'] == cluster_id]['item_id'].tolist()

def recommend_by_association(item_id):
    result = []
    for _, row in rules_df.iterrows():
        antecedents = list(literal_eval(row['antecedents']))
        if item_id in antecedents:
            result.extend(literal_eval(row['consequents']))
    return list(set(result))
def get_recommendations_for_user(user_id, top_n=6):
    # Lấy toàn bộ sản phẩm
      # Nếu predicted_df là DataFrame:
    try:
        user_ratings = predicted_df.loc[user_id].sort_values(ascending=False)
        return user_ratings.head(top_n).index.tolist()
    except KeyError:
        return []