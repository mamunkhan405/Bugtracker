from rest_framework import permissions


class IsProjectMemberOrOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, 'bug'):
            project = obj.bug.project
        else:
            project = obj
        
        return (request.user == project.owner or request.user in project.members.all())


class IsBugAssigneeOrCreator(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.user == obj.created_by or 
                request.user == obj.assigned_to or
                request.user == obj.project.owner)