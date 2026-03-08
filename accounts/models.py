from django.db import models
from django.contrib.auth.models import User
import os
import uuid

def profile_avatar_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{ext}"
    return f'avatars/{instance.user.id}/{new_filename}'

def profile_album_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{ext}"
    return f'albums/{instance.profile.user.id}/{new_filename}'

class Profile(models.Model):
    GENDER_CHOICES = [
        ('M', '男'),
        ('F', '女'),
        ('O', '其他'),
        ('N', '不愿透露'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to=profile_avatar_path, blank=True, null=True, verbose_name='头像')
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name='个性签名')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='性别')
    age = models.PositiveIntegerField(blank=True, null=True, verbose_name='年龄')
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='所在地')
    website = models.URLField(blank=True, null=True, verbose_name='个人网站')
    theme_color = models.CharField(max_length=7, default='#6366f1', verbose_name='主题颜色')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
    
    def __str__(self):
        return f"{self.user.username} 的资料"

class ProfileAlbum(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='album_images')
    image = models.ImageField(upload_to=profile_album_path, verbose_name='相册图片')
    caption = models.CharField(max_length=200, blank=True, null=True, verbose_name='图片描述')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = '相册图片'
        verbose_name_plural = '相册图片'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.profile.user.username} 的相册图片"
