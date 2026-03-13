# learning_logs/models.py
from django.db import models
from django.contrib.auth.models import User
import os
import uuid

def user_entry_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    new_filename = f"{uuid.uuid4()}{ext}"
    file_type = 'images' if instance.__class__.__name__ == 'EntryImage' else 'attachments'
    user_id = instance.entry.topic.owner.id
    date = instance.entry.date_added.strftime('%Y%m%d')
    return f'entries/{user_id}/{date}/{file_type}/{new_filename}'

class Tag(models.Model):
    """标签模型"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6366f1')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Topic(models.Model):
    COVER_STYLES = [
        ('default', '默认渐变'),
        ('ocean', '海洋蓝'),
        ('sunset', '日落橙'),
        ('forest', '森林绿'),
        ('purple', '梦幻紫'),
        ('pink', '樱花粉'),
        ('gold', '金色阳光'),
        ('dark', '暗夜星空'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', '公开'),
        ('private', '私人'),
        ('followers', '仅关注者可见'),
    ]
    
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True, related_name='topics')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True, verbose_name='封面图片')
    cover_style = models.CharField(max_length=20, choices=COVER_STYLES, default='default', verbose_name='封面样式')
    is_pinned = models.BooleanField(default=False, verbose_name='置顶')
    order = models.IntegerField(default=0, verbose_name='排序权重')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public', verbose_name='可见性')
    
    def __str__(self):
        return self.text

class Entry(models.Model):
    VISIBILITY_CHOICES = [
        ('public', '公开'),
        ('private', '私人'),
        ('followers', '仅关注者可见'),
    ]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='entries')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_image_only = models.BooleanField(default=False, verbose_name='纯图片笔记')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public', verbose_name='可见性')
    video_url = models.URLField(blank=True, null=True, verbose_name='视频链接')
    
    class Meta:
        verbose_name_plural = 'entries'
    
    def __str__(self):
        return self.text[:50] + '...' if len(self.text) > 50 else self.text

class EntryImage(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=user_entry_file_path, verbose_name='笔记图片')
    upload_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.entry.text[:20]}"

class EntryAttachment(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='attachments')
    attachment = models.FileField(upload_to=user_entry_file_path, verbose_name='笔记附件')
    upload_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment for {self.entry.text[:20]}"
    
    def get_attachment_name(self):
        return os.path.basename(self.attachment.name) if self.attachment else None

class EntryRevision(models.Model):
    """笔记修改历史模型"""
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='revisions')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '笔记历史版本'
        verbose_name_plural = '笔记历史版本'
    
    def __str__(self):
        return f"Revision of {self.entry.text[:30]} at {self.created_at}"

class Like(models.Model):
    """点赞模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'entry']
        verbose_name = '点赞'
        verbose_name_plural = '点赞'
    
    def __str__(self):
        return f"{self.user.username} 点赞了 {self.entry.text[:20]}"

class Comment(models.Model):
    """评论模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['created_at']
        verbose_name = '评论'
        verbose_name_plural = '评论'
    
    def __str__(self):
        return f"{self.user.username} 评论了 {self.entry.text[:20]}"

class Follow(models.Model):
    """关注模型"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'followed']
        verbose_name = '关注'
        verbose_name_plural = '关注'
    
    def __str__(self):
        return f"{self.follower.username} 关注了 {self.followed.username}"