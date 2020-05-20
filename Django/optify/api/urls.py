from django.contrib import admin
from django.urls import path,include,re_path,include
import api.views as views
from rest_framework.authtoken import views as rest_view
import api as api
from api.routers import router
urlpatterns = [
    path('user/logout/',views.LogoutUserView.as_view()),
    path('api-token-auth/', rest_view.obtain_auth_token),    
    re_path(r'^', include(router.urls)),    
    # path
]
