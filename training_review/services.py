'''Provide services of training program module.'''
from django.db import transaction

from auth.services import PermissionService
from infra.exceptions import BadRequest
from training_review.models import ReviewNote


class ReviewNoteService:
    '''Provide services for TrainingReview.'''
    @staticmethod
    def create_review_note(user=None, record=None, content=None):
        '''Create a TrainingReview with ObjectPermission.
        1. Assign object permission to the current user (the user,
        user's department_admin, school_admin etc.)
        2. Assign object permission to the record user who create the
        corresponding record.
        With the first 2 steps, both user and his admin has permissions
        [view hiself and the other's record_review_note]

        Parametsers
        ----------
        user: User
            The user who created the review note.

        record: Record
            The record to which the created review note is related.

        content: string
            The content represents what user want to say about the record.

        Returns
        -------
        review_note: ReviewNote
        '''

        with transaction.atomic():
            if content is None:
                raise BadRequest('审核提示内容不能为空！')
            review_note = ReviewNote.objects.create(user=user,
                                                    record=record,
                                                    content=content)
            PermissionService.assign_object_permissions(
                user, review_note)
            PermissionService.assign_object_permissions(
                record.user, review_note)
            return review_note
