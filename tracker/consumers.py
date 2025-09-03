import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Project, TypingIndicator


class ProjectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.project_group_name = f'project_{self.project_id}'
        self.user = self.scope['user']
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Check if user has access to this project
        has_access = await self.check_project_access()
        if not has_access:
            await self.close()
            return
        
        # Join project group
        await self.channel_layer.group_add(
            self.project_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to project {self.project_id}'
        }))
    
    async def disconnect(self, close_code):
        # Leave project group
        await self.channel_layer.group_discard(
            self.project_group_name,
            self.channel_name
        )
        
        # Clear typing indicators
        await self.clear_typing_indicators()
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'typing_start':
                await self.handle_typing_start(data)
            elif message_type == 'typing_stop':
                await self.handle_typing_stop(data)
            elif message_type == 'ping':
                await self.send(text_data=json.dumps({'type': 'pong'}))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def handle_typing_start(self, data):
        bug_id = data.get('bug_id')
        if bug_id:
            await self.set_typing_indicator(bug_id, True)
            
            # Broadcast typing indicator to group
            await self.channel_layer.group_send(
                self.project_group_name,
                {
                    'type': 'typing_indicator',
                    'data': {
                        'bug_id': bug_id,
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'is_typing': True
                    }
                }
            )
    
    async def handle_typing_stop(self, data):
        bug_id = data.get('bug_id')
        if bug_id:
            await self.set_typing_indicator(bug_id, False)
            
            # Broadcast typing indicator to group
            await self.channel_layer.group_send(
                self.project_group_name,
                {
                    'type': 'typing_indicator',
                    'data': {
                        'bug_id': bug_id,
                        'user_id': self.user.id,
                        'username': self.user.username,
                        'is_typing': False
                    }
                }
            )
    
    # WebSocket message handlers
    async def bug_notification(self, event):
        await self.send(text_data=json.dumps(event['data']))
    
    async def comment_notification(self, event):
        await self.send(text_data=json.dumps(event['data']))

    # Don't send typing indicator back to the sender
    async def typing_indicator(self, event):
        if event['data']['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'data': event['data']
            }))
    
    async def activity_notification(self, event):
        await self.send(text_data=json.dumps(event['data']))
    
    # Database operations
    @database_sync_to_async
    def check_project_access(self):
        try:
            project = Project.objects.get(id=self.project_id)
            return (self.user == project.owner or 
                   self.user in project.members.all())
        except Project.DoesNotExist:
            return False
    
    @database_sync_to_async
    def set_typing_indicator(self, bug_id, is_typing):
        try:
            indicator, created = TypingIndicator.objects.get_or_create(
                bug_id=bug_id,
                user=self.user,
                defaults={'is_typing': is_typing}
            )
            if not created:
                indicator.is_typing = is_typing
                indicator.save()
        except Exception:
            pass
    
    @database_sync_to_async
    def clear_typing_indicators(self):
        TypingIndicator.objects.filter(user=self.user).update(is_typing=False)