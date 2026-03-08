# Generated migration for Profile model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
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


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to=profile_avatar_path, verbose_name='头像')),
                ('bio', models.TextField(blank=True, max_length=500, null=True, verbose_name='个性签名')),
                ('gender', models.CharField(blank=True, choices=[('M', '男'), ('F', '女'), ('O', '其他'), ('N', '不愿透露')], max_length=1, null=True, verbose_name='性别')),
                ('age', models.PositiveIntegerField(blank=True, null=True, verbose_name='年龄')),
                ('location', models.CharField(blank=True, max_length=100, null=True, verbose_name='所在地')),
                ('website', models.URLField(blank=True, null=True, verbose_name='个人网站')),
                ('theme_color', models.CharField(default='#6366f1', max_length=7, verbose_name='主题颜色')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '用户资料',
                'verbose_name_plural': '用户资料',
            },
        ),
        migrations.CreateModel(
            name='ProfileAlbum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=profile_album_path, verbose_name='相册图片')),
                ('caption', models.CharField(blank=True, max_length=200, null=True, verbose_name='图片描述')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='album_images', to='accounts.profile')),
            ],
            options={
                'verbose_name': '相册图片',
                'verbose_name_plural': '相册图片',
                'ordering': ['-uploaded_at'],
            },
        ),
    ]
