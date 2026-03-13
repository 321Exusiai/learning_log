# learning_logs/forms.py
from django import forms
from .models import Topic, Entry, EntryImage, EntryAttachment, Comment

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml']
ALLOWED_ATTACHMENT_TYPES = [
    'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed',
    'application/json', 'text/plain', 'text/markdown',
    'image/jpeg', 'image/png', 'image/gif', 'image/webp',
    'application/pdf', 'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
]
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

def validate_file_type(file, allowed_types):
    """验证文件类型"""
    if file.content_type not in allowed_types:
        return False
    return True

def validate_file_size(file, max_size):
    """验证文件大小"""
    if file.size > max_size:
        return False
    return True

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text', 'cover_style', 'cover_image', 'visibility']
        labels = {'text': '', 'cover_style': '封面样式', 'cover_image': '封面图片', 'visibility': '可见性'}

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text', 'is_image_only', 'visibility', 'video_url']
        labels = {'text': '', 'is_image_only': '纯图片笔记', 'visibility': '可见性', 'video_url': '视频链接'}
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80, 'rows': 10, 'placeholder': '输入笔记内容...'}),
            'video_url': forms.URLInput(attrs={'placeholder': '输入视频链接（支持YouTube、B站等）'}),
        }

class MultiFileInput(forms.FileInput):
    def __init__(self, attrs=None):
        super().__init__(attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs['multiple'] = 'multiple'
        return super().render(name, value, attrs, renderer)

class EntryImageForm(forms.Form):
    image = forms.ImageField(
        widget=MultiFileInput(
            attrs={
                'accept': 'image/*',
                'class': 'file-input multi-file-input',
            }
        ),
        label='上传图片（可多选）',
        required=False
    )
    
    def clean_image(self):
        images = self.files.getlist('image')
        for image in images:
            if not validate_file_type(image, ALLOWED_IMAGE_TYPES):
                raise forms.ValidationError(f'不支持的图片格式: {image.name}')
            if not validate_file_size(image, MAX_FILE_SIZE):
                raise forms.ValidationError(f'文件大小超过限制 (50MB): {image.name}')
        return images

class EntryAttachmentForm(forms.Form):
    attachment = forms.FileField(
        widget=MultiFileInput(
            attrs={
                'accept': '.zip,.rar,.7z,.json,.png,.jpg,.gif,.txt,.md,.pdf,.doc,.docx',
                'class': 'file-input multi-file-input',
            }
        ),
        label='上传附件（可多选）',
        required=False
    )
    
    def clean_attachment(self):
        attachments = self.files.getlist('attachment')
        for attachment in attachments:
            if not validate_file_type(attachment, ALLOWED_ATTACHMENT_TYPES):
                raise forms.ValidationError(f'不支持的文件格式: {attachment.name}')
            if not validate_file_size(attachment, MAX_FILE_SIZE):
                raise forms.ValidationError(f'文件大小超过限制 (50MB): {attachment.name}')
        return attachments

class CommentForm(forms.ModelForm):
    """评论表单"""
    class Meta:
        model = Comment
        fields = ['content']
        labels = {'content': ''}
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': '写下你的评论...', 'class': 'comment-input'})
        }