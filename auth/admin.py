'''Define how to register our models in admin console.'''
from django.contrib import admin

from auth.models import Department, User, UserPermission, Role


class DepartmentAdmin(admin.ModelAdmin):
    '''Define how to register model Department in console.'''


class UserAdmin(admin.ModelAdmin):
    '''Define how to register model User in console.'''


class RoleAdmin(admin.ModelAdmin):
    '''Define how to register model Role in console.'''


class UserPermissionAdmin(admin.ModelAdmin):
    '''Define how to register model UserPermission in console.'''
    list_select_related = ('permission', 'user')


REGISTER_ITEMS = [
    (User, UserAdmin),
    (Role, RoleAdmin),
    (Department, DepartmentAdmin),
    (UserPermission, UserPermissionAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
