from rest_framework import serializers
from api.serializers import UserDisplaySerializer,MinimaluserSerializer
from chat.models import RoomMembers,Room,Message
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        exclude = ["room"]
class RoomMembersSerializer (serializers.ModelSerializer):
    user = MinimaluserSerializer(read_only=True)
    class Meta:
        model = RoomMembers
        fields = "__all__"

class RoomSerializer(serializers.ModelSerializer):
    members = RoomMembersSerializer(many=True)    
    class Meta:
        model = Room
        fields = ("id","date_created","date_modified","members")