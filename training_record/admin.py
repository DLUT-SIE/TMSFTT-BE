from django.contrib import admin

from training_record.models import (
    Record, RecordContent, RecordAttachment, StatusChangeLog)


class RecordAdmin(admin.ModelAdmin):
    pass


class RecordContentAdmin(admin.ModelAdmin):
    pass


class RecordAttachmentAdmin(admin.ModelAdmin):
    pass


class StatusChangeLogAdmin(admin.ModelAdmin):
    pass


models = [
    (Record, RecordAdmin),
    (RecordContent, RecordContentAdmin),
    (RecordAttachment, RecordAttachmentAdmin),
    (StatusChangeLog, StatusChangeLogAdmin),
]
for model_class, admin_class in models:
    admin.site.register(model_class, admin_class)
