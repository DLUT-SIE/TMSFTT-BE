'''Define how to register our models in admin console.'''
from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from auth.models import Department, User, UserPermission


class DepartmentAdmin(GuardedModelAdmin):
    '''Define how to register model Department in console.'''


class UserAdmin(GuardedModelAdmin):
    '''Define how to register model User in console.'''


class UserPermissionAdmin(GuardedModelAdmin):
    '''Define how to register model UserPermission in console.'''
    list_select_related = ('permission', 'user')


REGISTER_ITEMS = [
    (User, UserAdmin),
    (Department, DepartmentAdmin),
    (UserPermission, UserPermissionAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
