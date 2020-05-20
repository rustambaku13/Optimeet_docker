from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator,MaxValueValidator
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType
import django.contrib.postgres.fields as pos_fields
from django.db.models.signals import post_save
import pytz
class User(AbstractUser):
    def timezone_choices():
        x = list()
        for i in pytz.common_timezones:
            x.append([i,i])
        return x    
    profile_pic = models.ImageField(verbose_name="Avatar",null=True,blank=True)    
    schedule = GenericRelation("Schedule",on_delete=models.PROTECT)
    deviceToken = models.CharField(verbose_name="Mobile Device Id", default="None", max_length=600, blank=True)
    @property
    def myschedule(self):
        return self.schedule.get()
    timezone = models.CharField(max_length=50,verbose_name="Time zone of the User",default="UTC",choices=timezone_choices())
    def save(self, *args, **kwargs): 
        """ Adds the Schedule upon User Creation """
        if len(self.schedule.all()):
            schedule = self.schedule.all()[0]
            schedule.title = self.first_name+'\'s Schedule'
            schedule.save()
            super(User, self).save(*args, **kwargs)  
            return                    
        self.set_password(self.password)        
        super(User, self).save(*args, **kwargs)
        x = Schedule(title=self.first_name+'\'s Schedule',owner=self)
        x.save()        
class Contacts(models.Model):
    CONTACT_STATE_CHOICES = [
        ("req", 'Requested'),        
        ("acc", 'Accepted'),       
    ]
    requester = models.ForeignKey(User,on_delete=models.CASCADE,related_name="requested_contacts")
    reciever = models.ForeignKey(User,on_delete=models.CASCADE,related_name="recieved_contacts")
    state = models.CharField(max_length=4,verbose_name="State of connection",choices=CONTACT_STATE_CHOICES,db_index=True)
    class Meta:
        unique_together = [("requester","reciever")]
        
    
class Schedule(models.Model):
    title = models.CharField(verbose_name="Name for the Schedule",max_length=200)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    owner = GenericForeignKey('content_type', 'object_id')
    def defaultPermission():
        return {"general":"private","exceptions":[]}
    permission = pos_fields.JSONField(verbose_name="Permission details of a Schedule",default=defaultPermission)
    def __str__(self):
        return self.title
class OGroupMembers(models.Model):
    def defaultPrivaledges():
        return {"type":"regular","priority":50}
    group = models.ForeignKey("OGroup",related_name="groupmembers",on_delete=models.CASCADE)
    member = models.ForeignKey(User,on_delete=models.CASCADE,related_name="ogroups")
    date_joined = models.DateTimeField(verbose_name="Date joined",auto_now_add=True)
    priveledges = pos_fields.JSONField(verbose_name="User's priveledges in the group",default=defaultPrivaledges)
    class Meta:
        unique_together = [['group', 'member']]
class OGroup(models.Model):

    name = models.CharField(verbose_name="Group Name",max_length=200)
    members = models.ManyToManyField(User,through=OGroupMembers)
    description = models.TextField(verbose_name="Group Description",null=True,blank=True)
    profile_pic = models.ImageField(verbose_name="Circular Profile Pic for group",null=True,blank=True)
    cover_pic = models.ImageField(verbose_name="Background cover pic for group",null=True,blank=True)    
    schedule = GenericRelation("Schedule",on_delete=models.PROTECT)
    @property
    def myschedule(self):
        return self.schedule.get()
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs): 
        """ Adds the Schedule upon Group Creation """
        if len(self.schedule.all()):
            schedule = self.schedule.all()[0]
            schedule.title = self.name+'\'s Schedule'
            schedule.save()
            super(OGroup, self).save(*args, **kwargs)  
            return
        super(OGroup, self).save(*args, **kwargs)     
        x = Schedule(title=self.name+'\'s Schedule',owner=self)                  
        x.save()


class ActivitySchedule(models.Model):
    categories = [("Routine","Routine"),("Academic","Academic"),("Social","Social"),("Professional","Professional"),("Recreational","Recreational"),("Sport","Sport")]
    def default_privacy():
        return dict(privacy="friends")
    activity = models.ForeignKey("Activity",on_delete=models.CASCADE,related_name="schedules")
    schedule = models.ForeignKey(Schedule,on_delete=models.CASCADE,related_name="activities")
    priority = models.PositiveIntegerField(verbose_name='Priority of the event [0..100]',validators=[MaxValueValidator(100)])
    privacy = pos_fields.JSONField(verbose_name="Privacy Settings",default=default_privacy)
    #category = models.CharField(verbose_name="Type of activity",default="Default",max_length=100,choices=categories)
    class Meta:
        unique_together = [['activity', 'schedule']]

class Activity(models.Model):
    def weekday_choices():
       return [("Monday","Monday"),("Tuesday","Tuesday"),("Wednesday","Wednesday"),("Thursday","Thursday"),("Friday","Friday"),("Saturday","Saturday"),("Sunday","Sunday")]
    title = models.CharField(verbose_name="Title for the activity",max_length=200)
    start_times = pos_fields.ArrayField(models.DateTimeField(verbose_name="Starting DateTime for the activity"))    
    end_times = pos_fields.ArrayField(models.DateTimeField(verbose_name="Ending DateTime for the activity"))
    weekdays = pos_fields.ArrayField(models.CharField(max_length=20,verbose_name="Weekdays of the event",choices=weekday_choices()),blank=True,null=True)
    durations = pos_fields.ArrayField(models.DurationField(verbose_name="Duration of each start end pair"),null=True,blank=True)
    recurring = models.BooleanField(verbose_name="Is the Activity repeating",default=False)
    repetition = pos_fields.JSONField(verbose_name="Details of repetition",blank=True,null=True)        
    def save(self,*args,**kwargs):
        """ Computes the TimeDelta and saves as durations array in the Acitivity """
        i=0
        self.durations=[]
        for time in self.end_times:
            delta = time - self.start_times[i]
            self.durations.append(delta)
            i+=1
        super(Activity,self).save(*args,**kwargs)
    def __str__(self):
        return self.title

    
    
