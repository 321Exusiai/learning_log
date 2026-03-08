from django.contrib import admin
from .models import Topic, Entry, Tag, EntryImage, EntryAttachment

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'owner', 'created_at']
    list_filter = ['owner']
    search_fields = ['name']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['text', 'owner', 'date_added', 'is_deleted']
    list_filter = ['owner', 'is_deleted']
    search_fields = ['text']
    filter_horizontal = ['tags']

@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ['topic', 'date_added', 'is_deleted']
    list_filter = ['topic', 'is_deleted']
    search_fields = ['text']
    filter_horizontal = ['tags']

admin.site.register(EntryImage)
admin.site.register(EntryAttachment)