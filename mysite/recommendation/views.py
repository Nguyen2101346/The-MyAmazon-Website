import os
import joblib
from django.http import JsonResponse

# Nạp mô hình
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models_data', 'predicted_ratings_df.joblib')
cf_model = joblib.load(MODEL_PATH)

def predict_rating(request, user_id, item_id):
    try:
        prediction = cf_model.predict(user_id, item_id)
        return JsonResponse({
            'user_id': user_id,
            'item_id': item_id,
            'estimated_rating': prediction.est,
            'was_impossible': prediction.details.get('was_impossible', False)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
