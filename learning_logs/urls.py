# learning_logs/urls.py
from django.urls import path
from . import views

app_name = 'learning_logs'

urlpatterns = [
    # 主页
    path('', views.index, name='index'),
    # 主题列表
    path('topics/', views.topics, name='topics'),
    # 主题详情
    path('topics/<int:topic_id>/', views.topic, name='topic'),
    # 添加新主题
    path('new_topic/', views.new_topic, name='new_topic'),
    # 添加新笔记
    path('new_entry/<int:topic_id>/', views.new_entry, name='new_entry'),
    # 编辑笔记
    path('edit_entry/<int:topic_id>/<int:entry_id>/', views.edit_entry, name='edit_entry'),
    # 编辑主题
    path('edit_topic/<int:topic_id>/', views.edit_topic, name='edit_topic'),
    # 删除主题
    path('delete_topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    # 删除单条笔记
    path('delete_entry/<int:topic_id>/<int:entry_id>/', views.delete_entry, name='delete_entry'),
]