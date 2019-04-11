'''Define how to register our models in admin console.'''
from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from training_record.models import (
    Record, RecordContent, RecordAttachment, StatusChangeLog)


class RecordAdmin(GuardedModelAdmin):
    '''Define how to register model Record in console.'''


class RecordContentAdmin(GuardedModelAdmin):
    '''Define how to register model RecordContent in console.'''


class RecordAttachmentAdmin(GuardedModelAdmin):
    '''Define how to register model RecordAttachment in console.'''


class StatusChangeLogAdmin(GuardedModelAdmin):
    '''Define how to register model StatusChangeLog in console.'''


REGISTER_ITEMS = [
    (Record, RecordAdmin),
    (RecordContent, RecordContentAdmin),
    (RecordAttachment, RecordAttachmentAdmin),
    (StatusChangeLog, StatusChangeLogAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
