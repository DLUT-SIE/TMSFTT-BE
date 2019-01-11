'''Define how to register our models in admin console.'''
from django.contrib import admin

from auth.models import Department, UserProfile


class DepartmentAdmin(admin.ModelAdmin):
    '''Define how to register model Department in console.'''


class UserProfileAdmin(admin.ModelAdmin):
    '''Define how to register model UserProfile in console.'''


REGISTER_ITEMS = [
    (Department, DepartmentAdmin),
    (UserProfile, UserProfileAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
