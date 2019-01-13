'''Define how to register our models in admin console.'''
from django.contrib import admin

from training_event.models import (CampusEvent, OffCampusEvent, Enrollment)


class CampusEventAdmin(admin.ModelAdmin):
    '''Define how to register model CampusEvent in console.'''


class OffCampusEventAdmin(admin.ModelAdmin):
    '''Define how to register model OffCampusEvent in console.'''


class EnrollmentAdmin(admin.ModelAdmin):
    '''Define how to register model Enrollment in console.'''


REGISTER_ITEMS = [
    (CampusEvent, CampusEventAdmin),
    (OffCampusEvent, OffCampusEventAdmin),
    (Enrollment, EnrollmentAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
