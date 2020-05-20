from rest_framework.permissions import BasePermission
import api.models as models


class ItisMeorAdminPermission(BasePermission):
    # Premission to control 
    def has_object_permission(self, request, view, obj): 
        admin = bool(request.user and request.user.is_staff)
        if admin:
            return True
        if request.user == obj:
            return True
        return False    

class MyScheduleorAdminPermission(BasePermission):        
    def has_object_permission(self, request, view, obj):
        # return False
        admin = bool(request.user and request.user.is_staff)
        if admin:
            return True
        if obj.owner == request.user:
            return True
        return False  
class SchedulePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        # return False
        admin = bool(request.user and request.user.is_staff)
        if obj.owner == request.user:
            return True
        if admin:
            return True            
        if obj.permission["general"]=="public":
            return True
        if request.user.username in obj.permission['exceptions']:
            return True                            
        return True         
class MySchedulePermission(BasePermission):
    pass

class ActivityisinSchedulePermission(BasePermission):
    def has_object_permission(self, request, view, activity,schedule):        
        return schedule.activities.filter(activity=activity)
        