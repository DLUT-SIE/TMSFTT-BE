'''Define how to register our models in admin console.'''
from django.contrib import admin

from auth.models import Department, UserProfile, UserPermission


class DepartmentAdmin(admin.ModelAdmin):
    '''Define how to register model Department in console.'''


class UserProfileAdmin(admin.ModelAdmin):
    '''Define how to register model UserProfile in console.'''


class UserPermissionAdmin(admin.ModelAdmin):
    '''Define how to register model UserPermission in console.'''
    list_select_related = ('permission', 'user')


REGISTER_ITEMS = [
    (Department, DepartmentAdmin),
    (UserProfile, UserProfileAdmin),
    (UserPermission, UserPermissionAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
