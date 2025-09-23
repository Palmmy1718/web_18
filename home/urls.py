# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # auth ของผู้ใช้ทั่วไป
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),

    # แผงหลังบ้านของระบบคุณเอง (เปลี่ยนจาก admin/ เป็น dashboard/)
    path('dashboard/login/', views.admin_login, name='admin_login'),
    path('dashboard/logout/', views.admin_logout, name='admin_logout'),

    path('dashboard/recipes/', views.admin_recipes, name='admin_recipes'),
    path('dashboard/recipes/add/', views.add_recipe, name='add_recipe'),
    path('dashboard/recipes/edit/<int:recipe_id>/', views.edit_recipe, name='edit_recipe'),
    path('dashboard/recipes/delete/<int:recipe_id>/', views.delete_recipe, name='delete_recipe'),
]
