'''Define how to register our models in admin console.'''
from django.contrib import admin

from training_record.models import (
    Record, RecordContent, RecordAttachment, StatusChangeLog)


class RecordAdmin(admin.ModelAdmin):
    '''Define how to register model Record in console.'''


class RecordContentAdmin(admin.ModelAdmin):
    '''Define how to register model RecordContent in console.'''


class RecordAttachmentAdmin(admin.ModelAdmin):
    '''Define how to register model RecordAttachment in console.'''


class StatusChangeLogAdmin(admin.ModelAdmin):
    '''Define how to register model StatusChangeLog in console.'''


REGISTER_ITEMS = [
    (Record, RecordAdmin),
    (RecordContent, RecordContentAdmin),
    (RecordAttachment, RecordAttachmentAdmin),
    (StatusChangeLog, StatusChangeLogAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
