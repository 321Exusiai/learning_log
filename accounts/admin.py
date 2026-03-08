from django.contrib import admin
from .models import Profile, ProfileAlbum

class ProfileAlbumInline(admin.TabularInline):
    model = ProfileAlbum
    extra = 1

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'gender', 'age', 'location', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['user__username', 'bio', 'location']
    inlines = [ProfileAlbumInline]

@admin.register(ProfileAlbum)
class ProfileAlbumAdmin(admin.ModelAdmin):
    list_display = ['profile', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['profile__user__username', 'caption']
