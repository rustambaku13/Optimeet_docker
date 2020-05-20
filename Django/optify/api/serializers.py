from rest_framework import serializers
from generic_relations.relations import GenericRelatedField
from rest_framework.relations import PrimaryKeyRelatedField
import api.models as models
from api.algorithms.Scheduler import BruteForceAI,GradientDecentAI,AnotherAI,AnotherGradientAI

class FullUserSerializer(serializers.ModelSerializer):    
    class Meta:
        model = models.User
        exclude = ['password']
class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['email','username','password','first_name','last_name','profile_pic','timezone','deviceToken']
        extra_kwargs = {
            'password': {'write_only': True}
        }   

class UserDisplaySerializer(serializers.ModelSerializer):
     class Meta:
        model = models.User
        exclude = ['is_superuser','is_staff','user_permissions',"password"]
        depth = 1
class MinimaluserSerializer(serializers.ModelSerializer):
     class Meta:
        model = models.User
        exclude = ['is_superuser','is_staff','user_permissions',"password","groups","is_active","date_joined"]
        depth = 1        
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ["username","first_name","password","last_name","email","profile_pic","timezone"]
        extra_kwargs = {
            'password': {'write_only': True}
        }      
        

                
class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Activity
        fields="__all__"
        read_only_fields = ['id',"durations"]
    def validate(self, data):
        """
        Check that start is before finish.
        """
        l = len(data["start_times"])
        for i in range(l):
            if data["start_times"][i]>=data['end_times'][i]:
                raise serializers.ValidationError("Start times should come before end times")                    
        return data      
        
class SimpleScheduleActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ActivitySchedule
        exclude = ['schedule','id','activity']
  
class ActivityDetailsSerializer(serializers.ModelSerializer):
    """ Serailizer for adding a new activity with its details """
    activity = ActivitySerializer()
    class Meta:
        model=models.ActivitySchedule
        exclude = ['id','schedule']        
    def create(self,validated_data):
        activity_data = validated_data.pop('activity')
        activity = models.Activity.objects.create(**activity_data)
        activityschedule = models.ActivitySchedule.objects.create(**validated_data,activity=activity)
        return activityschedule
           
    def update(self,instance,validated_data):
        if "activity" in validated_data:
            activity_data = validated_data.pop('activity')
            activity = instance.activity
            activity_serializer = ActivitySerializer(instance=activity,data=activity_data,partial=self.partial)
            activity_serializer.is_valid()
            activity_serializer.save()
        super(ActivityDetailsSerializer,self).update(instance,validated_data)
        return instance

class ScheduleActivityViewSerializer(serializers.ModelSerializer):
    """ Serializer to view the activities with their details """
    activity = ActivitySerializer()
    class Meta:
        model = models.ActivitySchedule
        exclude = ['schedule',"id"]
   



class ScheduleViewSerializer(serializers.ModelSerializer):
    """ Serializer to view the schedule """
    activities = ScheduleActivityViewSerializer(many=True,read_only=True)
    owner = GenericRelatedField({
        models.User: UserDisplaySerializer()
    })
    class Meta:
        model = models.Schedule
        fields = ['id',"title","activities","owner"]
        read_only_fields = ['id','title',"activities","owner"]

class RequestContactsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Contacts
        fields = ["reciever"]

class GetContactsSerializer(serializers.ModelSerializer):
    requester = UserDisplaySerializer(read_only=True)
    reciever = UserDisplaySerializer(read_only=True)
    class Meta:
        model = models.Contacts
        fields = ['id',"requester","reciever","state"]
        read_only_fields = ['id',"requester","reciever","state"]

class GroupMemberSerializer(serializers.ModelSerializer):       
    class Meta:
        model = models.OGroupMembers
        fields = ['member',"priveledges"]
        

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OGroup
        fields = ['id','name','description','profile_pic','cover_pic']
        read_only_fields = ['id']

class MinimalScheduleSerializer(serializers.ModelSerializer):   
    class Meta:
        model = models.Schedule
        exclude = ['object_id','content_type']
        read_only_fields = ['id'] 

class GetGroupSerializer(serializers.ModelSerializer):
    groupmembers = GroupMemberSerializer(many=True,read_only=True)
    
    class Meta:
        model = models.OGroup
        fields = ['id','name','description','profile_pic','cover_pic','groupmembers']
        read_only_fields = ['id','name','description','profile_pic','cover_pic','groupmembers']  
    def to_representation(self,instance):
        data = super(GetGroupSerializer,self).to_representation(instance)
        sc = instance.schedule.get()
        data['schedule'] = MinimalScheduleSerializer(sc).data
        return data

class MinimalGroupSerializer(serializers.ModelSerializer):
    # groupmembers = GroupMemberSerializer(many=True,read_only=True)
    
    class Meta:
        model = models.OGroup
        fields = ['id','name','description','profile_pic','cover_pic']
        read_only_fields = ['id','name','description','profile_pic','cover_pic']  



class ScheduleSerializer(serializers.ModelSerializer):
    owner = GenericRelatedField({
        models.User: UserDisplaySerializer(),
        models.OGroup:MinimalGroupSerializer()
    },read_only=True)
    class Meta:
        model = models.Schedule
        exclude = ['object_id','content_type']
        read_only_fields = ['id',"owner"] 

class ScheduleActivitySerializer(serializers.ModelSerializer):
    schedule = ScheduleSerializer(required=True)
    activity = ActivitySerializer(required=True)
    class Meta:
        model = models.ActivitySchedule
        fields = ['priority','privacy','schedule','activity']   
    def create(self,validated_data):   
        assert 'id' in self.initial_data['schedule'],"Schedule id was not found"
        schedule = models.Schedule.objects.get(pk = self.initial_data['schedule']['id'])        
        activity_data = validated_data.pop('activity')
        validated_data.pop("schedule")   
        activity = None  
        act_sch = None                                       
        try:
            activity = models.Activity.objects.create(**activity_data)                
            act_sch = models.ActivitySchedule.objects.create(activity=activity,schedule=schedule,**validated_data)            
        except:
            if activity:
                activity.delete()   
        return act_sch

    def update(self,instance,validated_data):
        print(self.initial_data)
        assert 'id' in self.initial_data['schedule'] and 'id' in self.initial_data['myactivity'],"Schedule id was not found"
        schedule = models.Schedule.objects.get(pk = self.initial_data['schedule']['id'])  
        activity = models.Activity.objects.get(pk=self.initial_data['myactivity']['id'])  
        activityser = ActivitySerializer(data=validated_data.pop("activity"))
        activityser.is_valid()
        activityser.update(activity,activityser.validated_data)                
        return instance 




class AIConstraintsSerializer(serializers.Serializer):
    def __init__(self,schedule=None,*args,**kwargs):     
        self.schedule = schedule
        super(AIConstraintsSerializer,self).__init__(*args,**kwargs)

    duration = serializers.DurationField(required=True)
    start_time = serializers.TimeField(required=True)
    end_time = serializers.TimeField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)      
    def SimpleBruteForceSearch(self):
        start_time = self.validated_data['start_time']
        end_time = self.validated_data['end_time']
        start_date = self.validated_data['start_date']
        end_date = self.validated_data['end_date']
        duration = self.validated_data['duration'] 
        assert self.schedule, "No Schedule error"
        return GradientDecentAI(start_time=start_time,end_time=end_time,start_date = start_date,end_date=end_date,duration=duration,schedule = self.schedule,timezone = self.schedule.owner.timezone)       
        

