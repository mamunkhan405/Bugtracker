from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Project, Bug, Comment, ActivityLog


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    members_ids = serializers.ListField(
        child=serializers.IntegerField(), 
        write_only=True, 
        required=False
    )
    bug_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'owner', 'members', 'members_ids', 
                 'bug_count', 'created_at', 'updated_at']
    
    def get_bug_count(self, obj):
        return obj.bugs.count()
    
    def create(self, validated_data):
        members_ids = validated_data.pop('members_ids', [])
        project = Project.objects.create(**validated_data)
        if members_ids:
            project.members.set(members_ids)
        return project
    
    def update(self, instance, validated_data):
        members_ids = validated_data.pop('members_ids', None)
        instance = super().update(instance, validated_data)
        if members_ids is not None:
            instance.members.set(members_ids)
        return instance


class CommentSerializer(serializers.ModelSerializer):
    commenter = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'bug', 'commenter', 'message', 'created_at', 'updated_at']
        read_only_fields = ['commenter']


class BugSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    comments_count = serializers.SerializerMethodField()
    recent_comments = CommentSerializer(many=True, read_only=True, source='comments')
    
    class Meta:
        model = Bug
        fields = ['id', 'title', 'description', 'status', 'priority', 
                 'assigned_to', 'assigned_to_id', 'project', 'project_name',
                 'created_by', 'comments_count', 'recent_comments',
                 'created_at', 'updated_at']
        read_only_fields = ['created_by']
    
    def get_comments_count(self, obj):
        return obj.comments.count()
    
    def get_recent_comments(self, obj):
        return obj.comments.all()[:3]  # Get last 3 comments


class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = ActivityLog
        fields = ['id', 'project', 'user', 'action', 'description', 'bug', 'created_at']