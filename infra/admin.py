'''Define how to register our models in admin console.'''
from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from infra.models import OperationLog, Notification


class OperationLogAdmin(GuardedModelAdmin):
    '''Define how to register model OperationLog in console.'''


class NotificationAdmin(GuardedModelAdmin):
    '''Define how to register model Notification in console.'''


REGISTER_ITEMS = [
    (OperationLog, OperationLogAdmin),
    (Notification, NotificationAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
