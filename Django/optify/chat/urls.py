from django.contrib import admin
from django.urls import path,include,re_path,include
from django.conf.urls import url
from rest_framework.authtoken import views as rest_view
from chat.views import ViewRooms,GetRoom,GetMessages,ReadChatsTillNow,GetChat,ReadLastChats
urlpatterns = [
    url(r'chats/$',ViewRooms.as_view(),name="Get Room"),
    url(r'chats/(?P<room_uuid>[\w,-]+)',GetChat.as_view(),name="Get Chat"),
    url(r'chat/(?P<id>\d+)',GetRoom.as_view(),name="Get/Create Room id"),
    url('chat/messages',GetMessages.as_view(),name="Get Messages Room"),
    
]
