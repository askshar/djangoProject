from django.contrib import admin
from .models import Room, Topic, Message

# Register your models here.


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created']


admin.site.register(Topic)
admin.site.register(Message)