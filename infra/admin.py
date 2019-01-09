from django.contrib import admin

from infra.models import OperationLog, Notification


class OperationLogAdmin(admin.ModelAdmin):
    pass


class NotificationAdmin(admin.ModelAdmin):
    pass


models = [
    (OperationLog, OperationLogAdmin),
    (Notification, NotificationAdmin),
]
for model_class, admin_class in models:
    admin.site.register(model_class, admin_class)
