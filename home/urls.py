from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-recipes/', views.user_recipes, name='user_recipes'),
    # --- สมาชิกแก้ไข/ลบ/เพิ่มสูตรอาหารของตัวเอง ---
    path('recipe/edit/<int:recipe_id>/', views.user_edit_recipe, name='user_edit_recipe'),
    path('recipe/delete/<int:recipe_id>/', views.user_delete_recipe, name='user_delete_recipe'),
    path('recipe/add/', views.user_add_recipe, name='user_add_recipe'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    # --- แผงควบคุมสำหรับ Admin ---
    path('dashboard/recipes/', views.admin_recipes, name='admin_recipes'),
    path('dashboard/recipes/add/', views.add_recipe, name='add_recipe'),
    path('dashboard/recipes/edit/<int:recipe_id>/', views.edit_recipe, name='edit_recipe'),
    path('dashboard/recipes/delete/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
]