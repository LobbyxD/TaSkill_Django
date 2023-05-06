from django.contrib import admin

from .models import (
    Board,
    Organization,
    Task,
    Task_status,
    Task_status_link,
)

# Register your models here.

admin.site.register(Organization)
admin.site.register(Task)
admin.site.register(Task_status)
admin.site.register(Task_status_link)
admin.site.register(Board)