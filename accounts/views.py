# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm  # Django自带的注册表单

def register(request):
    """注册新用户"""
    # 1. GET请求：显示空的注册表单
    if request.method != 'POST':
        form = UserCreationForm()  # 自带的注册表单（用户名+密码）
    # 2. POST请求：处理提交的注册数据
    else:
        form = UserCreationForm(data=request.POST)
        if form.is_valid():
            # 保存新用户（密码会自动加密）
            new_user = form.save()
            # 自动登录新注册的用户
            login(request, new_user)
            # 跳转到主页
            return redirect('learning_logs:index')
    
    # 渲染注册页面
    context = {'form': form}
    return render(request, 'accounts/register.html', context)