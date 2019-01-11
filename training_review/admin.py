'''Define how to register our models in admin console.'''
from django.contrib import admin

from training_review.models import ReviewNote


class ReviewNoteAdmin(admin.ModelAdmin):
    '''Define how to register model ReviewNote in console.'''


REGISTER_ITEMS = [
    (ReviewNote, ReviewNoteAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
