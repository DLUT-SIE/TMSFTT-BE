# Generated by Django 2.1.5 on 2019-01-21 06:16
from random import random, randint, choice, sample
from datetime import timedelta

from faker import Faker
from django.db import migrations
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.timezone import now

from auth.models import Department, UserProfile
from infra.models import Notification
from training_program.models import ProgramCategory, ProgramForm, Program
from training_event.models import CampusEvent, OffCampusEvent, Enrollment
from training_record.models import (
    Record, RecordAttachment, RecordContent, StatusChangeLog)
from training_review.models import ReviewNote


faker = Faker('zh_CN')

def _random_datetime(before=True, after=False):
    if before and after:
        scale = 2 * random() - 1
    elif before:
        scale = random() - 1
    else:
        scale = random()
    shift = timedelta(
        days=scale * 60,
        seconds=3600 * 12,
        hours=scale * 12,
        microseconds=randint(0, 1000000-1),
    )
    return now() + shift


def _random_contents(record):
    return [RecordContent.objects.create(
        record=record,
        content_type=content_type,
        content=faker.text(100),
    ) for (content_type, _) in RecordContent.CONTENT_TYPE_CHOICES
        if random() > 0.7]

def _random_attachments(record):
    return [RecordAttachment.objects.create(
        record=record,
        attachment_type=attachment_type,
        path=faker.file_path(depth=3),
    ) for (attachment_type, _) in RecordAttachment.ATTACHMENT_TYPE_CHOICES
        if random() > 0.7]


def _random_status_change_logs(record):
    logs = []
    pre_status = record.status
    for (status, _) in Record.STATUS_CHOICES[1:]:
        if status == pre_status:
            continue
        if random() < 0.2:
            break
        logs.append(StatusChangeLog.objects.create(
            record=record,
            pre_status=pre_status,
            post_status=status,
            time=_random_datetime(),
            user=record.user,
        ))
        pre_status = status
    record.status = pre_status
    record.save()
    return logs


def _random_review_note(record, admins):
    if record.status in (Record.STATUS_SUBMITTED, Record.STATUS_PRESUBMIT):
        return []
    fields = ('name', 'time', 'location', 'num_hours', 'num_participants')
    return [ReviewNote.objects.create(
        record=record,
        field_name=field_name,
        user=choice(admins),
        content=faker.text(20),
    ) for field_name in fields if random() < 0.3]


def populate_initial_data(apps, _):  # pylint: disable=all
    '''This function populates models data for development.'''
    print('Populate django.contrib.auth')
    print('Populate User')
    num_users = 20
    users = [User.objects.create_user(
        id=id,
        username=faker.profile()['username'],
        first_name=faker.first_name(),
        last_name=faker.last_name()) for id in range(1, 1 + num_users)]

    print('Populate auth')
    print('Populate Department')
    num_departments = 4
    departments = [Department.objects.create(
        name=faker.company_prefix()) for id in range(num_departments)]
    # Set admins
    admins = []
    for department in departments:
        _admins = sample(users, randint(1, 3))
        department.admins.add(*_admins)
        department.save()
        admins.extend(_admins)

    print('Populate UserProfile')
    user_profiles = [UserProfile.objects.create(
        user=user,
        department=choice(departments),
        age=randint(30, 50)) for user in users]

    print('Populate infra')
    print('Populate Notification')
    num_notifications = 100
    notifications = [Notification.objects.create(
        time=_random_datetime(),
        sender=choice(users),
        recipient=choice(users),
        content=faker.text(100),
        read_time=now() if idx % 5 == 0 else None,
    ) for idx in range(num_notifications)]

    print('Populate training_program')
    print('Populate ProgramCategory')
    category_names = ('教学培训', '教学促进', '教育技术', '青年教师助课', '其他')
    program_categotires = [ProgramCategory.objects.create(
        name=category_name) for category_name in category_names]

    print('Populate ProgramForm')
    form_names = ('参与', '主讲', '评委')
    program_forms = [ProgramForm.objects.create(
        name=form_name) for form_name in form_names]

    print('Populate Program')
    num_programs = 10
    programs = [Program.objects.create(
        name=faker.text(10),
        department=choice(departments),
        category=choice(program_categotires),
    ) for _ in range(num_programs)]

    print('Populate training_event')
    print('Populate CampusEvent')
    num_campus_events = 20
    campus_events = [CampusEvent.objects.create(
        name=faker.text(10),
        time=_random_datetime(False, True),
        location=faker.street_address(),
        num_hours=random() * 4,
        num_participants=randint(10, 100),
        program=choice(programs),
        description=faker.text(100),
    ) for _ in range(num_campus_events)]

    print('Populate OffCampusEvent')
    num_off_campus_events = 300
    off_campus_events = [OffCampusEvent.objects.create(
        name=faker.text(10),
        time=_random_datetime(False, True),
        location=faker.street_address(),
        num_hours=random() * 4,
        num_participants=randint(10, 100),
    ) for _ in range(num_off_campus_events)]

    print('Populate Enrollment')
    num_enrollments = 200
    enrollments = [Enrollment.objects.create(
        campus_event=choice(campus_events),
        user=choice(users),
        enroll_method=choice(Enrollment.ENROLL_METHOD_CHOICES)[0],
        is_participated=faker.boolean(80),
    ) for _ in range(num_enrollments)]

    print('Populate training_record')
    off_campus_event_records = [Record.objects.create(
        off_campus_event=off_campus_event,
        user=choice(users),
    ) for off_campus_event in off_campus_events]

    campus_event_records = [Record.objects.create(
        campus_event=enrollment.campus_event,
        user=enrollment.user,
    ) for enrollment in enrollments]

    records = off_campus_event_records + campus_event_records

    print('Populate RecordContent')
    contents = []
    for record in records:
        contents.extend(_random_contents(record))

    print('Populate RecordAttachment')
    attachments = []
    for record in records:
        attachments.extend(_random_attachments(record))

    print('Populate StatusChangeLog')
    status_change_logs = []
    for record in records:
        status_change_logs.extend(_random_status_change_logs(record))

    print('Populate training_review')
    print('Populate ReviewNote')
    review_notes = []
    for record in records:
        review_notes.extend(_random_review_note(record, admins))


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tmsftt_auth', '0001_initial'),
        ('infra', '0001_initial'),
        ('training_program', '0001_initial'),
        ('training_event', '0001_initial'),
        ('training_record', '0001_initial'),
        ('training_review', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_initial_data),
    ]
