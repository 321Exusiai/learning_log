# learning_logs/forms.py
from django import forms
from .models import Topic, Entry

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['text']
        labels = {'text': ''}

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        fields = ['text', 'image', 'attachment']  # 新增image和attachment
        labels = {
            'text': '',
            'image': '上传图片',
            'attachment': '上传附件'
        }
        widgets = {
            'text': forms.Textarea(attrs={'cols': 80}),
            # 自定义文件上传控件样式
            'image': forms.ClearableFileInput(attrs={
                'class': 'file-input',
                'accept': 'image/*'  # 只允许上传图片
            }),
            'attachment': forms.ClearableFileInput(attrs={
                'class': 'file-input',
                'accept': '.zip,.rar,.7z,.json,.png,.jpg,.gif'  # 限制附件类型
            })
        }