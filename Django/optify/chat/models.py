from django.db import models
from django.db.models.signals import post_save
import uuid
from django.conf import settings
from optify.settings import AUTH_USER_MODEL as User
from django.db.models.signals import post_save
# Create your models here.



class DateTimeModel(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
class RoomMembers(models.Model):
    room = models.ForeignKey("Room",related_name="members",verbose_name="Room",on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name="User",on_delete=models.CASCADE)
    unread_count = models.PositiveIntegerField(default=0)
    online = models.BooleanField(default=False,verbose_name="User is online")
class Room(DateTimeModel):
    id = models.UUIDField(primary_key=True,
            default=uuid.uuid4,
            editable=False)    
    member_users = models.ManyToManyField(User,through=RoomMembers,related_name="rooms")
    def __str__(self):
        memberset = self.members.all()
        members_list = []
        for member in memberset:
            members_list.append(member.username)

        return ", ".join(members_list) 
    class Meta:
        ordering = ['-date_modified']

class Message(DateTimeModel):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, related_name='sender')
    room = models.ForeignKey(Room, on_delete=models.CASCADE,related_name="messages")
    text = models.TextField()
    recipients = models.ManyToManyField(settings.AUTH_USER_MODEL,
        related_name='recipients')
        
    def __str__(self):
        return f'{self.text} sent by "{self.sender}" in Room "{self.room}"'
    class Meta:
        ordering = ['-id']

