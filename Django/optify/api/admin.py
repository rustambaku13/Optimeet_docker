from django.contrib import admin
from api import models
admin.site.register(models.User)
admin.site.register(models.Schedule)
admin.site.register(models.OGroup)
admin.site.register(models.Activity)
admin.site.register(models.ActivitySchedule)

