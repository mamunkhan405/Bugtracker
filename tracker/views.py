from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import models

from .models import Project, Bug, Comment, ActivityLog
from .serializers import (
    ProjectSerializer, BugSerializer, CommentSerializer, 
    ActivityLogSerializer, UserSerializer
)
from .permissions import IsProjectMemberOrOwner, IsBugAssigneeOrCreator


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    
    def get_queryset(self):
        # Users can only see projects they own or are members of
        return Project.objects.filter(
            models.Q(owner=self.request.user) | 
            models.Q(members=self.request.user)
        ).distinct()
    
    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        # Add owner as a member
        project.members.add(self.request.user)
        
        # Log activity
        ActivityLog.objects.create(
            project=project,
            user=self.request.user,
            action='project_created',
            description=f'Project "{project.name}" was created'
        )
    #Get all bugs for a each project
    @action(detail=True, methods=['get'])
    def bugs(self, request, pk=None):
        project = self.get_object()
        bugs = project.bugs.all()
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            bugs = bugs.filter(status=status_filter)
        
        serializer = BugSerializer(bugs, many=True)
        return Response(serializer.data)
    
    #Get activity log for a specific project
    @action(detail=True, methods=['get'])
    def activities(self, request, pk=None):
        project = self.get_object()
        activities = project.activities.all()[:50]  # Last 50 activities
        serializer = ActivityLogSerializer(activities, many=True)
        return Response(serializer.data)


class BugViewSet(viewsets.ModelViewSet):
    serializer_class = BugSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'assigned_to', 'project']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    
    def get_queryset(self):
        # Users can only see bugs from projects they have access to
        user_projects = Project.objects.filter(
            models.Q(owner=self.request.user) | 
            models.Q(members=self.request.user)
        )
        return Bug.objects.filter(project__in=user_projects)
    
    def perform_create(self, serializer):
        bug = serializer.save(created_by=self.request.user)
        
        # Log activity
        ActivityLog.objects.create(
            project=bug.project,
            user=self.request.user,
            action='bug_created',
            description=f'Bug "{bug.title}" was created',
            bug=bug
        )
        
        # Send WebSocket notification
        self.send_websocket_notification(bug.project.id, {
            'type': 'bug_created',
            'bug': BugSerializer(bug).data,
            'message': f'New bug created: {bug.title}'
        })
    
    def perform_update(self, serializer):
        old_bug = Bug.objects.get(pk=serializer.instance.pk)
        bug = serializer.save()
        
        # Check what changed and log accordingly
        changes = []
        if old_bug.status != bug.status:
            changes.append(f'status changed from {old_bug.get_status_display()} to {bug.get_status_display()}')
        if old_bug.assigned_to != bug.assigned_to:
            old_assigned = old_bug.assigned_to.username if old_bug.assigned_to else 'unassigned'
            new_assigned = bug.assigned_to.username if bug.assigned_to else 'unassigned'
            changes.append(f'assigned from {old_assigned} to {new_assigned}')
        
        if changes:
            description = f'Bug "{bug.title}" updated: {", ".join(changes)}'
            action_type = 'bug_closed' if bug.status == 'resolved' else 'bug_updated'
            
            ActivityLog.objects.create(
                project=bug.project,
                user=self.request.user,
                action=action_type,
                description=description,
                bug=bug
            )
            
            # Send WebSocket notification
            self.send_websocket_notification(bug.project.id, {
                'type': 'bug_updated',
                'bug': BugSerializer(bug).data,
                'message': description
            })
            
    #"Get bugs assigned to the current user
    @action(detail=False, methods=['get'])
    def assigned_to_me(self, request):
        bugs = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(bugs, many=True)
        return Response(serializer.data)
    
    def send_websocket_notification(self, project_id, data):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'project_{project_id}',
            {
                'type': 'bug_notification',
                'data': data
            }
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectMemberOrOwner]

    # Users can only see comments from bugs they have access to
    def get_queryset(self):
        user_projects = Project.objects.filter(
            models.Q(owner=self.request.user) | 
            models.Q(members=self.request.user)
        )
        return Comment.objects.filter(bug__project__in=user_projects)
    
    def perform_create(self, serializer):
        comment = serializer.save(commenter=self.request.user)
        
        # Log activity
        ActivityLog.objects.create(
            project=comment.bug.project,
            user=self.request.user,
            action='comment_added',
            description=f'Comment added to bug "{comment.bug.title}"',
            bug=comment.bug
        )
        
        # Send WebSocket notification
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'project_{comment.bug.project.id}',
            {
                'type': 'comment_notification',
                'data': {
                    'type': 'comment_added',
                    'comment': CommentSerializer(comment).data,
                    'bug_id': comment.bug.id,
                    'message': f'New comment on: {comment.bug.title}'
                }
            }
        )