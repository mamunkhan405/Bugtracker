
from django.contrib import admin
from .models import Project, Bug, Comment, ActivityLog, TypingIndicator

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['members']

@admin.register(Bug)
class BugAdmin(admin.ModelAdmin):
    list_display = ['title', 'project', 'status', 'priority', 'assigned_to', 'created_by', 'created_at']
    list_filter = ['status', 'priority', 'project', 'created_at']
    search_fields = ['title', 'description']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['bug', 'commenter', 'created_at']
    list_filter = ['created_at']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['project', 'user', 'action']
    list_filter = ['action']

@admin.register(TypingIndicator)
class TypingIndicatorAdmin(admin.ModelAdmin):
    list_display = ['bug', 'user', 'is_typing', 'updated_at']