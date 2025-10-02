from django.urls import path
from .views import predict_rating

urlpatterns = [
    path('predict/<str:user_id>/<str:item_id>/', predict_rating, name='predict_rating'),
]
