from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_projects')
    members = models.ManyToManyField(User, related_name='projects', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']


class Bug(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_bugs')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='bugs')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_bugs')
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"[{self.project.name}] {self.title}"
    
    class Meta:
        ordering = ['-created_at']


class Comment(models.Model):
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE, related_name='comments')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Comment by {self.commenter.username} on {self.bug.title}"
    
    class Meta:
        ordering = ['created_at']

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('bug_created', 'Bug Created'),
        ('bug_updated', 'Bug Updated'),
        ('bug_closed', 'Bug Closed'),
        ('comment_added', 'Comment Added'),
        ('bug_assigned', 'Bug Assigned'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs_user')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE, related_name='bug_activity', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()}"
    
    class Meta:
        ordering = ['-created_at']

class TypingIndicator(models.Model):
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE, related_name='typing_indicators')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='typing_user')
    is_typing = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['bug', 'user']