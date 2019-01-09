from django.contrib import admin

from training_program.models import ProgramCatgegory, ProgramForm, Program


class ProgramCatgegoryAdmin(admin.ModelAdmin):
    pass


class ProgramFormAdmin(admin.ModelAdmin):
    pass


class ProgramAdmin(admin.ModelAdmin):
    pass


models = [
    (ProgramCatgegory, ProgramCatgegoryAdmin),
    (ProgramForm, ProgramFormAdmin),
    (Program, ProgramAdmin),
]
for model_class, admin_class in models:
    admin.site.register(model_class, admin_class)
