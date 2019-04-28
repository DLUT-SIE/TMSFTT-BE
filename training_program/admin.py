'''Define how to register our models in admin console.'''
from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from training_program.models import Program


class ProgramAdmin(GuardedModelAdmin):
    '''Define how to register model Program in console.'''


REGISTER_ITEMS = [
    (Program, ProgramAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
