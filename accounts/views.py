# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileForm, AlbumImageForm
from .models import Profile, ProfileAlbum

def register(request):
    """注册新用户"""
    if request.method != 'POST':
        form = CustomUserCreationForm()
    else:
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, '注册成功！欢迎加入！')
            return redirect('learning_logs:index')
    
    context = {'form': form}
    return render(request, 'accounts/register.html', context)

@login_required
def profile(request):
    """查看个人资料"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    album_images = profile.album_images.all()[:6]
    
    context = {
        'profile': profile,
        'album_images': album_images,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """编辑个人资料"""
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method != 'POST':
        form = ProfileForm(instance=profile)
    else:
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, '资料更新成功！')
            return redirect('accounts:profile')
    
    context = {'form': form, 'profile': profile}
    return render(request, 'accounts/edit_profile.html', context)

@login_required
def add_album_image(request):
    """添加相册图片"""
    if request.method == 'POST':
        form = AlbumImageForm(request.POST, request.FILES)
        if form.is_valid():
            profile, created = Profile.objects.get_or_create(user=request.user)
            album_image = ProfileAlbum(
                profile=profile,
                image=form.cleaned_data['image'],
                caption=form.cleaned_data.get('caption', '')
            )
            album_image.save()
            messages.success(request, '图片添加成功！')
            return redirect('accounts:profile')
    else:
        form = AlbumImageForm()
    
    context = {'form': form}
    return render(request, 'accounts/add_album_image.html', context)

@login_required
def delete_album_image(request, image_id):
    """删除相册图片"""
    image = get_object_or_404(ProfileAlbum, id=image_id, profile__user=request.user)
    if request.method == 'POST':
        image.delete()
        messages.success(request, '图片已删除！')
    return redirect('accounts:profile')
