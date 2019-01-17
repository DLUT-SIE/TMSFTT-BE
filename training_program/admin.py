'''Define how to register our models in admin console.'''
from django.contrib import admin

from training_program.models import ProgramCategory, ProgramForm, Program


class ProgramCategoryAdmin(admin.ModelAdmin):
    '''Define how to register model ProgramCategory in console.'''


class ProgramFormAdmin(admin.ModelAdmin):
    '''Define how to register model ProgramForm in console.'''


class ProgramAdmin(admin.ModelAdmin):
    '''Define how to register model Program in console.'''


REGISTER_ITEMS = [
    (ProgramCategory, ProgramCategoryAdmin),
    (ProgramForm, ProgramFormAdmin),
    (Program, ProgramAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
