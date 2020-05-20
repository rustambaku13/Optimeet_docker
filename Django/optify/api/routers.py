from rest_framework import routers
import api.views as views
router = routers.SimpleRouter()
router.register(r'users', views.UserViewSet)
urlpatterns = router.urls
