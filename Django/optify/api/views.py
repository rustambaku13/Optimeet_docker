from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view,action
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import PermissionDenied,NotFound,APIException,ValidationError
import api.permissions as pm
from django.contrib.auth.models import AnonymousUser 
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser,NOT,SingleOperandHolder,OperandHolder,OR
from rest_framework.renderers import JSONRenderer
from rest_framework.generics import CreateAPIView,GenericAPIView,ListAPIView,RetrieveAPIView
from rest_framework import mixins
from rest_framework import viewsets
import rest_framework.mixins
from django.db.models import Q
import api.models as models
import api.serializers as serializers
import io
import api.mixins as mymixins
from api.algorithms.Scheduler import BruteForceAI

class GenericScheduleViewSet(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.ListModelMixin, viewsets.GenericViewSet):
    pass





class UserViewSet(mymixins.GetSerializerPermissionClassMixin,viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.UserDisplaySerializer    
    serializer_action_classes = {
        'list': serializers.FullUserSerializer,
        'create':serializers.UserRegisterSerializer,
        'update':serializers.UserUpdateSerializer,
        'partial_update':serializers.UserUpdateSerializer,
        'destroy':serializers.FullUserSerializer
    }
    permission_action_classes = {
        
        'create':[SingleOperandHolder(NOT,IsAuthenticated)],
        'update':[IsAuthenticated,pm.ItisMeorAdminPermission],
        'partial_update':[IsAuthenticated,pm.ItisMeorAdminPermission],
        'destroy':[IsAuthenticated,pm.ItisMeorAdminPermission]
    } 
    @action(detail=False,methods=['get'], name='My Profile')
    def me(self,request):
        return Response(self.serializer_class(instance=request.user).data)

class LogoutUserView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request,*args,**kwargs):
        try:
            mytok = Token.objects.get(user=request.user)
            mytok.delete()
            return Response({"detail":"Successfully logged out"})
        except:
            return Response({"detail":"Token not found"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ScheduleViewSet(mymixins.GetSerializerPermissionClassMixin,GenericScheduleViewSet):
    queryset = models.Schedule.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ScheduleSerializer
    serializer_action_classes = {
        # 'retrieve':serializers.ScheduleViewSerializer,
        # 'add':serializers.ActivityDetailsSerializer
    }
    permission_action_classes = {
        'list': [IsAdminUser],
        'update':[IsAuthenticated,pm.MyScheduleorAdminPermission],
        'partial_update':[IsAuthenticated,pm.MyScheduleorAdminPermission],
        # "add":[IsAuthenticated,pm.MyScheduleorAdminPermission]
    }   
    @action(detail=False, methods=['get'], name='My Schedule')
    def my(self,request):
        schedule = request.user.myschedule
        return Response(serializers.ScheduleSerializer(instance=schedule).data)

class ActivityViewSet(mymixins.GetSerializerPermissionClassMixin,viewsets.ModelViewSet):
    lookup_field2 = "sched_id"
    lookup_field = "activity"
    schedule_permission = pm.SchedulePermission()
    schedule_permission_exceptions=[]
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ActivityDetailsSerializer
    serializer_action_classes = {
       'ai':serializers.AIConstraintsSerializer
    }
    permission_action_classes = {   
               
    }   
    schedule_object = None
    def get_queryset(self):
        self.get_schedule_object()                                      
        return models.ActivitySchedule.objects.filter(schedule=self.schedule_object)
    def get_schedule_object(self):
        assert self.lookup_field2 in self.kwargs, "Include the Schedule Id"
        sched_id = self.kwargs.get(self.lookup_field2)
        try:
            self.schedule_object = models.Schedule.objects.get(pk=sched_id)
        except:
            self.schedule_object = None
            raise NotFound()     
        if self.action in self.schedule_permission_exceptions:
            return self.schedule_object
        if not self.schedule_permission.has_object_permission(self.request,self,self.schedule_object):
            self.permission_denied(
                    self.request, message=getattr(self.schedule_permission, 'message', None)
                )
        return self.schedule_object

    def create(self,request,sched_id):
        # try:
        schedule = self.get_schedule_object()    
        # except PermissionDenied:   
        #     return Response({"details":"You do not have permission for this action"},status=status.HTTP_404_NOT_FOUND)   
        # except:
        #     return Response({"details":"Schedule does not exist"},status=status.HTTP_404_NOT_FOUND)       
        serializer = self.get_serializer(data=request.data)    
        try:           
            serializer.is_valid(raise_exception=True)
            serializer.save(schedule=schedule)           
        except:
            return Response(serializer.errors,status=400)    
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_update(self, serializer):
        serializer.save()
    @action(detail=False, methods=['post'], name='AI Scheduler')
    def ai(self,request,sched_id):
        schedule = self.get_schedule_object()  
        ser = serializers.AIConstraintsSerializer(schedule,data=request.data)
        try:
            ser.is_valid(raise_exception=True)
        except:
            return Response(ser.errors)
        ai = ser.SimpleBruteForceSearch()
        return Response(ai.Search())
    @action(detail=False,name="test data")        
    def data(self,request,sched_id):
        schedule = self.get_schedule_object() 
        import csv
        with open('schedule_data.csv', mode='w') as employee_file:
            employee_writer = csv.writer(employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            employee_writer.writerow(['Title', 'Duration', 'Day Portion',"Weekday"])            
            for i in schedule.activities.all():
                time = i.activity.start_times[0].time()
                # time = time.minute + time.hour*60
                # print(time)
                employee_writer.writerow([i.activity.title,i.activity.durations[0].total_seconds(),match_portion(time),i.activity.weekdays[0]])


class ContactsViewSet(mymixins.GetSerializerPermissionClassMixin,mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin, 
                   mixins.DestroyModelMixin,                                     
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.RequestContactsSerializer
    ordering_fields = ['state']
    serializer_action_classes = {
        'list':serializers.GetContactsSerializer
        
        # 'retrieve':serializers.ScheduleViewSerializer,
        # 'add':serializers.ActivityDetailsSerializer
    }
    permission_action_classes = {

    }   

    def get_queryset(self):
        return models.Contacts.objects.filter(Q(requester=self.request.user)|Q(reciever=self.request.user)) 

    def create(self,request):
        item = self.get_serializer(data=request.data)
        try:            
            item.is_valid(raise_exception=True)
            item.save(requester=request.user,state='req')
            return Response({"details":"Request Sent"})            
        except APIException:
            return Response(item.errors,status=400)
        except:
            return Response({"details":"User is already in your friend list"},status=400)
    @action(detail=True,methods=['post'],name="Respond to contract")  
    def respond(self,request,*args, **kwargs):
        try:
            item = self.get_object()
            assert 'response' in request.data
            response = request.data['response']
            assert response=="acc" or response=='del'
            if response=='del':
                item.delete()
                return Response({"details":"Success"})
            if item.reciever != request.user:
                return Response({"details":"You cannot accept your request"})
            item.state = response
            item.save()
            return Response({"details":"Success"})
        except AssertionError:
            return Response({"details":"Include the response parameter with domain (acc,del)"},status=400)  
        except:
            return Response({"details":"Contract does not exist"},status=400)  


class GroupsViewSet(mymixins.GetSerializerPermissionClassMixin,viewsets.ModelViewSet):
    serializer_class = serializers.GetGroupSerializer
    permission_classes = [IsAuthenticated]
    serializer_action_classes = {
        'create':serializers.GroupSerializer
        
        # 'retrieve':serializers.ScheduleViewSerializer,
        # 'add':serializers.ActivityDetailsSerializer
    }
    permission_action_classes = {
        
    }   
    def get_queryset(self):
        return models.OGroup.objects.filter(members = self.request.user)
    def create(self,request):
        item = self.get_serializer(data = request.data)
        try:
            item.is_valid(raise_exception=True)                             
            group = item.save()
            member = models.OGroupMembers(group=group,member=request.user,priveledges={"type":"admin","priority":100})
            member.save()
            return Response(item.data)  
        except ValidationError:
            return Response(item.errors,status=400)
        except Exception:
            group.delete()
            return Response({"details":"Internal Server Error"},status=500)
    @action(detail=True,methods=['post'],name="Invite to group")
    def invite(self,request,**kwargs):
        try:
            group = self.get_object()
            memberser = serializers.GroupMemberSerializer(data=request.data)
            memberser.is_valid(raise_exception=True)
            memberser.save(group=group)
            return Response(memberser.data)            
        except AssertionError:
            return Response({"detail":"User is missing"},status=400)     
        except ValidationError:
            return Response(memberser.errors,status=400)            
        except:
            raise NotFound
    @action(detail=True,methods=['post'],name="Kick from Group")
    def kick(self,request,**kwargs):
        try:
            group = self.get_object()
            assert "member" in request.data
            member_id = int(request.data.get("member",0))
            if member_id==0:
                raise NotFound
            models.OGroupMembers.objects.get(member=member_id,group=group).delete()
            return Response({'details':"Success"})
        except AssertionError:
            return Response({"detail":"member field is missing"},status=400)  
        except NotFound:
            raise
        except:
            return Response({"detail":"Internal Server Error"},status=500)

    
        
            


    





def match_portion(t):
    from datetime import time
    if t > time(hour=18):
        return "evening"
    elif t > time(hour=13):
        return "midday"
    elif t > time(hour=8):
        return "morning"
    elif t > time(hour=5):
        return "early_morning"
    elif t > time(hour=3):    
        return "deep_night"                         
    return "night"        

             
        
           


