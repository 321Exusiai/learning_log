# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='邮箱')
    first_name = forms.CharField(max_length=30, required=False, label='名字')
    last_name = forms.CharField(max_length=30, required=False, label='姓氏')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = '用户名'
        self.fields['password1'].label = '密码'
        self.fields['password2'].label = '确认密码'
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-input',
                'placeholder': self.fields[field].label
            })

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'bio', 'gender', 'age', 'location', 'website', 'theme_color')
        labels = {
            'avatar': '头像',
            'bio': '个性签名',
            'gender': '性别',
            'age': '年龄',
            'location': '所在地',
            'website': '个人网站',
            'theme_color': '主题颜色',
        }
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': '介绍一下自己...'}),
            'theme_color': forms.TextInput(attrs={'type': 'color'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'theme_color':
                self.fields[field].widget.attrs.update({
                    'class': 'form-input'
                })

class AlbumImageForm(forms.Form):
    image = forms.ImageField(label='添加图片')
    caption = forms.CharField(max_length=200, required=False, label='图片描述')
