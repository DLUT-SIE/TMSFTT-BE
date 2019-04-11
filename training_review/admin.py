'''Define how to register our models in admin console.'''
from django.contrib import admin
from guardian.admin import GuardedModelAdmin

from training_review.models import ReviewNote


class ReviewNoteAdmin(GuardedModelAdmin):
    '''Define how to register model ReviewNote in console.'''


REGISTER_ITEMS = [
    (ReviewNote, ReviewNoteAdmin),
]
for model_class, admin_class in REGISTER_ITEMS:
    admin.site.register(model_class, admin_class)
