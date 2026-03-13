# learning_logs/urls.py
from django.urls import path
from . import views

app_name = 'learning_logs'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('global_search/', views.global_search, name='global_search'),
    path('topics/', views.topics, name='topics'),
    path('topics/<int:topic_id>/', views.topic, name='topic'),
    path('new_topic/', views.new_topic, name='new_topic'),
    path('new_entry/<int:topic_id>/', views.new_entry, name='new_entry'),
    path('edit_entry/<int:topic_id>/<int:entry_id>/', views.edit_entry, name='edit_entry'),
    path('edit_topic/<int:topic_id>/', views.edit_topic, name='edit_topic'),
    path('delete_topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    path('delete_entry/<int:topic_id>/<int:entry_id>/', views.delete_entry, name='delete_entry'),
    path('delete_image/<int:image_id>/', views.delete_entry_image, name='delete_entry_image'),
    path('delete_attachment/<int:attach_id>/', views.delete_entry_attachment, name='delete_entry_attachment'),
    path('trash/', views.trash, name='trash'),
    path('restore_topic/<int:topic_id>/', views.restore_topic, name='restore_topic'),
    path('restore_entry/<int:entry_id>/', views.restore_entry, name='restore_entry'),
    path('permanent_delete_topic/<int:topic_id>/', views.permanent_delete_topic, name='permanent_delete_topic'),
    path('permanent_delete_entry/<int:entry_id>/', views.permanent_delete_entry, name='permanent_delete_entry'),
    path('revisions/<int:topic_id>/<int:entry_id>/', views.entry_revisions, name='entry_revisions'),
    path('share/<int:topic_id>/', views.share_topic, name='share_topic'),
    path('reorder_topics/', views.reorder_topics, name='reorder_topics'),
    path('toggle_pin/<int:topic_id>/', views.toggle_pin_topic, name='toggle_pin_topic'),
    # 新功能
    path('toggle_like/<int:entry_id>/', views.toggle_like, name='toggle_like'),
    path('add_comment/<int:entry_id>/', views.add_comment, name='add_comment'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
]