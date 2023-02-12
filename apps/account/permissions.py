from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user == obj.user
    
class IsMentor(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_mentor == True:
            return True
        
