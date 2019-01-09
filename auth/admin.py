from django.contrib import admin

from auth.models import Department, UserProfile


class DepartmentAdmin(admin.ModelAdmin):
    pass


class UserProfileAdmin(admin.ModelAdmin):
    pass


models = [
    (Department, DepartmentAdmin),
    (UserProfile, UserProfileAdmin),
]
for model_class, admin_class in models:
    admin.site.register(model_class, admin_class)
