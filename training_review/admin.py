from django.contrib import admin

from training_review.models import ReviewNote


class ReviewNoteAdmin(admin.ModelAdmin):
    pass


models = [
    (ReviewNote, ReviewNoteAdmin),
]
for model_class, admin_class in models:
    admin.site.register(model_class, admin_class)
