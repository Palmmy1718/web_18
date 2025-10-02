# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # --- URL ใหม่สำหรับให้สมาชิกเพิ่มสูตรอาหาร ---
    path('recipe/add/', views.user_add_recipe, name='user_add_recipe'),

    # --- แผงควบคุมสำหรับ Admin ---
    path('dashboard/recipes/', views.admin_recipes, name='admin_recipes'),
    path('dashboard/recipes/add/', views.add_recipe, name='add_recipe'),
    path('dashboard/recipes/edit/<int:recipe_id>/', views.edit_recipe, name='edit_recipe'),
    path('dashboard/recipes/delete/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
]