from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('signin/', views.open_signin, name='open_signin'),
    path('signup/', views.open_signup, name='open_signup'),
    path('signup/submit/', views.signup, name='signup'),
    path('signin/submit/', views.signin, name='signin'),
    path('logout/', views.logout_view, name='logout'),
    path('customer/<str:username>/', views.customer_home, name='customer_home'),
    path('manage/dashboard/', views.admin_home, name='admin_home'),
    path('manage/restaurants/new/', views.open_add_restaurant, name='open_add_restaurant'),
    path('manage/restaurants/new/submit/', views.add_restaurant, name='add_restaurant'),
    path('manage/restaurants/', views.open_show_restaurant, name='open_show_restaurant'),
    path('manage/restaurants/<int:restaurant_id>/edit/', views.open_update_restaurant, name='open_update_restaurant'),
    path('manage/restaurants/<int:restaurant_id>/edit/submit/', views.update_restaurant, name='update_restaurant'),
    path('manage/restaurants/<int:restaurant_id>/delete/', views.delete_restaurant, name='delete_restaurant'),
    path('manage/restaurants/<int:restaurant_id>/menu/', views.open_update_menu, name='open_update_menu'),
    path('manage/restaurants/<int:restaurant_id>/menu/add/', views.update_menu, name='update_menu'),

    path('restaurants/<int:restaurant_id>/menu/<str:username>/', views.view_menu, name='view_menu'),
    path('cart/items/<int:item_id>/<str:username>/add/', views.add_to_cart, name='add_to_cart'),

    path('cart/<str:username>/', views.show_cart, name='show_cart'),

    path('checkout/<str:username>/', views.checkout, name='checkout'),

    path('orders/<str:username>/', views.orders, name='orders'),

    
]
