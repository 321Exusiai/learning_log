# learning_logs/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete  # 新增：导入信号
from django.dispatch import receiver  # 新增
import os

# 新增：自定义文件上传路径（按用户/日期分文件夹，避免重名）
def user_entry_file_path(instance, filename):
    # 文件会存在 media/entries/用户ID/日期/文件名
    user_id = instance.topic.owner.id
    date = instance.date_added.strftime('%Y%m%d')
    return f'entries/{user_id}/{date}/{filename}'

class Topic(models.Model):
    """用户学习的主题"""
    text = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """返回模型的字符串表示"""
        return self.text

class Entry(models.Model):
    """关于某个主题的具体笔记"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    # 新增：图片字段（可选，支持多张的话用ManyToMany，这里先做单张）
    image = models.ImageField(
        upload_to=user_entry_file_path,  # 上传路径
        blank=True, null=True,  # 可选
        verbose_name='笔记图片'
    )
    # 新增：附件字段（可选）
    attachment = models.FileField(
        upload_to=user_entry_file_path,  # 上传路径
        blank=True, null=True,  # 可选
        verbose_name='笔记附件'
    )

    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        """返回模型的字符串表示"""
        if len(self.text) > 50:
            return f"{self.text[:50]}..."
        else:
            return self.text
    
    # 新增：获取附件的文件名（去掉路径，只显示文件名）
    def get_attachment_name(self):
        if self.attachment:
            return os.path.basename(self.attachment.name)
        return None

# ✅ 新增：信号接收器，在 Entry 被删除后，同步删除磁盘上的物理文件
@receiver(post_delete, sender=Entry)
def delete_files_on_entry_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
    if instance.attachment:
        if os.path.isfile(instance.attachment.path):
            os.remove(instance.attachment.path)