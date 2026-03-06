# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# ✅ 这一行是命名空间的核心，必须有，不能拼错accounts
app_name = 'accounts'

urlpatterns = [
    # 注册
    path('register/', views.register, name='register'),
    # 登录
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    # 注销
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]