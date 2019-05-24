'''Define how to register our models in admin console.'''
from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from auth.models import Department, User


class DepartmentAdmin(GuardedModelAdmin):
    '''Define how to register model Department in console.'''


class UserAdmin(GuardedModelAdmin):
    '''Define how to register model User in console.'''


REGISTER_ITEMS = [
    (User, UserAdmin),
    (Department, DepartmentAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
