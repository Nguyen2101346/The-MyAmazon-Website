from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
   path('',views.home, name="home"),
   path('Login/', views.RegisternLogin,name="Login"),
   path('logout', views.logoutdef, name='logout'),
   path('cart/', views.cart,name="cart"),
   path('checkout/', views.checkout ,name="checkout"),
   path('search/', views.Search, name = "search"),
   path('api/suggestions/', views.search_suggestions, name='search_suggestions'),
   path('MyShop/', views.Myshop ,name = "myshop"),
   path('category/',views.CategoryDetail, name = "category"),
   path('update_item/', views.updateItem, name='updateItem'),
   path('update_product/', views.updateProduct, name='update_product'),
   path('update-profile', views.update_profile, name='update_profile'),
   path('product/', views.ProductDetail,name = 'product'),
   path('account/', views.account, name = 'account'),
   path('history/', views.browsing_history_view, name='browsing_history'),
   path('add-to-wishlist/', views.add_to_wishlist, name='add_to_wishlist'),
   path('order/<int:order_id>/',views.order_detail,name='order'),
   path('order/<int:order_id>/confirm-received/', views.confirm_received, name='confirm-received'),
]