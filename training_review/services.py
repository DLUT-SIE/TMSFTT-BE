'''Provide services of training program module.'''
from django.db import transaction

from auth.services import PermissonsService
from training_review.models import ReviewNote
from training_record.models import Record

class ReviewNoteService:
    '''Provide services for TrainingReview.'''
    @staticmethod
    def create_review_note(review_note_data):
        '''Create a TrainingReview with ObjectPermission.
        1. Assign object permission to the current user (the user,
        user's department_admin, school_admin etc.)
        2. Assign object permission to the record user who create the
        corresponding record.
        With the first 2 steps, both user and his admin has permissions
        [view hiself and the other's record_review_note]

        Parametsers
        ----------
        review_note_data: dict
            This dict should have full information needed to
            create a ReviewNote.

        Returns
        -------
        review_note: ReviewNote
        '''

        with transaction.atomic():
            review_note = ReviewNote.objects.create(**review_note_data)
            PermissonsService.assigin_object_permissions(
                review_note_data['user'], review_note)
            PermissonsService.assigin_object_permissions(
                review_note_data['record'].user, review_note)
            return review_note
