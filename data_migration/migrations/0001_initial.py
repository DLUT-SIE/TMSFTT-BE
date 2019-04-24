# Generated by Django 2.1.5 on 2019-01-21 06:16
from random import random, randint, choice, sample
from datetime import timedelta

from faker import Faker
from django.db import migrations
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from training_event.models import EventCoefficient


faker = Faker('zh_CN')
faker.seed(0)


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


def _random_contents(record, RecordContent):
    return [RecordContent.objects.create(
        record=record,
        content_type=content_type,
        content=faker.text(100),
    ) for (content_type, _) in RecordContent.CONTENT_TYPE_CHOICES
        if random() > 0.7]


def _random_attachments(record, RecordAttachment):
    return [RecordAttachment.objects.create(
        record_id=record.id,
        attachment_type=attachment_type,
        path=faker.file_path(depth=3),
    ) for (attachment_type, _) in RecordAttachment.ATTACHMENT_TYPE_CHOICES
        if random() > 0.7]


def _random_status_change_logs(record, Record, StatusChangeLog):
    logs = []
    pre_status = record.status
    for (status, _) in Record.STATUS_CHOICES[1:]:
        if status == pre_status:
            continue
        if random() < 0.2:
            break
        logs.append(StatusChangeLog.objects.create(
            record_id=record.id,
            pre_status=pre_status,
            post_status=status,
            time=_random_datetime(),
            user_id=record.user_id,
        ))
        pre_status = status
    record.status = pre_status
    record.save()
    return logs


def _random_review_note(record, admins, Record, ReviewNote):
    if record.status in [Record.STATUS_SUBMITTED]:
        return []
    return [ReviewNote.objects.create(
        record_id=record.id,
        user_id=choice(admins).id,
        content=faker.text(20),
    )]


def populate_initial_data(apps, _):  # pylint: disable=all
    '''This function populates models data for development.'''
    assert settings.DEBUG, (
        'This migration should only be used during development environment,'
        ' but found DEBUG=False')
    print('Populate auth')
    print('Populate Department')
    num_departments = 5
    Department = apps.get_model('tmsftt_auth.Department')
    departments = [Department.objects.create(
        name=faker.company_prefix(),
        raw_department_id=f'{idx}'
    ) for idx in range(1, 1 + num_departments)]

    print('Populate User')
    num_users = 20
    User = get_user_model()
    admin = User.objects.create_superuser(
        id=1,
        username='root',
        password='root',
        email='root@root.com',
        department_id=departments[0].id,
    )
    usernames = set([faker.profile()['username'] for _ in range(num_users)])
    while len(usernames) < num_users:
        usernames.add(faker.profile()['username'])
    usernames = list(usernames)
    users = [User.objects.create_user(
        id=idx,
        username=usernames[idx-2],
        department_id=departments[idx].id if idx < num_departments else choice(departments).id,
        age=randint(20, 60),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
    ) for idx in range(2, 2 + num_users)]

    print('Populate infra')
    print('Populate Notification')
    num_notifications = 200
    Notification = apps.get_model('infra.Notification')
    notifications = [Notification.objects.create(
        time=_random_datetime(),
        sender_id=choice(users).id,
        recipient_id=choice(users).id,
        content=faker.text(100),
        read_time=now() if idx % 4 != 0 else None,
    ) for idx in range(num_notifications)]

    print('Populate training_program')
    print('Populate ProgramCategory')
    category_names = ('教学培训', '教学促进', '教育技术', '青年教师助课', '其他')
    ProgramCategory = apps.get_model('training_program.ProgramCategory')
    program_categotires = [ProgramCategory.objects.create(
        name=category_name) for category_name in category_names]

    print('Populate ProgramForm')
    form_names = ('参与', '主讲', '评委')
    ProgramForm = apps.get_model('training_program.ProgramForm')
    program_forms = [ProgramForm.objects.create(
        name=form_name) for form_name in form_names]

    print('Populate Program')
    num_programs = 15
    Program = apps.get_model('training_program.Program')
    programs = [Program.objects.create(
        name=faker.text(10),
        department_id=choice(departments).id,
        category_id=choice(program_categotires).id,
    ) for _ in range(num_programs)]

    print('Populate training_event')
    print('Populate CampusEvent')
    num_campus_events = 30
    CampusEvent = apps.get_model('training_event.CampusEvent')
    campus_events = [CampusEvent.objects.create(
        name=faker.text(10),
        time=_random_datetime(False, True),
        location=faker.street_address(),
        num_hours=random() * 4,
        num_participants=randint(10, 100),
        program_id=choice(programs).id,
        deadline=now(),
        description=faker.text(100),
    ) for _ in range(num_campus_events)]

    print('Populate OffCampusEvent')
    num_off_campus_events = 50
    OffCampusEvent = apps.get_model('training_event.OffCampusEvent')
    off_campus_events = [OffCampusEvent.objects.create(
        name=faker.text(10),
        time=_random_datetime(False, True),
        location=faker.street_address(),
        num_hours=random() * 4,
        num_participants=randint(10, 100),
    ) for _ in range(num_off_campus_events)]

    print('Populate EventCoefficient')
    for campus_event in campus_events:
        EventCoefficient.objects.create(
            coefficient=1, hours_option=0, workload_option=0,
            campus_event_id=campus_event.id)
    for off_campus_event in off_campus_events:
        EventCoefficient.objects.create(
            coefficient=0, hours_option=0, workload_option=0,
            off_campus_event_id=off_campus_event.id)

    print('Populate Enrollment')
    num_enrollments = 200
    enrollments = []
    from training_event.models import Enrollment
    enroll_methods = Enrollment.ENROLL_METHOD_CHOICES
    Enrollment = apps.get_model('training_event.Enrollment')
    Enrollment.ENROLL_METHOD_CHOICES = enroll_methods
    for campus_event in campus_events:
        enrolled_users = sample(users, randint(2, num_users - 5))
        enrollments.extend([Enrollment.objects.create(
            campus_event_id=campus_event.id,
            user_id=user.id,
            enroll_method=choice(Enrollment.ENROLL_METHOD_CHOICES)[0],
            is_participated=faker.boolean(80),
        ) for user in enrolled_users])

    print('Populate training_record')
    from training_record.models import Record
    record_statuses = Record.STATUS_CHOICES
    record_status_submitted = Record.STATUS_SUBMITTED
    Record = apps.get_model('training_record.Record')
    Record.STATUS_CHOICES = record_statuses
    Record.STATUS_SUBMITTED = record_status_submitted
    off_campus_event_records = [Record.objects.create(
        off_campus_event_id=off_campus_event.id,
        user_id=choice(users).id,
        event_coefficient_id=EventCoefficient.objects.get(
            off_campus_event_id=off_campus_event.id).id
    ) for off_campus_event in off_campus_events]

    campus_event_records = [Record.objects.create(
        campus_event_id=enrollment.campus_event_id,
        user_id=enrollment.user_id,
        event_coefficient_id=EventCoefficient.objects.get(
            campus_event_id=enrollment.campus_event.id).id
    ) for enrollment in enrollments]

    records = off_campus_event_records + campus_event_records

    print('Populate RecordContent')
    from training_record.models import RecordContent
    content_types = RecordContent.CONTENT_TYPE_CHOICES
    RecordContent = apps.get_model('training_record.RecordContent')
    RecordContent.CONTENT_TYPE_CHOICES = content_types
    contents = []
    for record in records:
        contents.extend(_random_contents(record, RecordContent))

    print('Populate RecordAttachment')
    attachments = []
    from training_record.models import RecordAttachment
    attachment_types = RecordAttachment.ATTACHMENT_TYPE_CHOICES
    RecordAttachment = apps.get_model('training_record.RecordAttachment')
    RecordAttachment.ATTACHMENT_TYPE_CHOICES = attachment_types
    for record in records:
        attachments.extend(_random_attachments(record, RecordAttachment))

    print('Populate StatusChangeLog')
    status_change_logs = []
    StatusChangeLog = apps.get_model('training_record.StatusChangeLog')
    for record in records:
        status_change_logs.extend(_random_status_change_logs(
            record, Record, StatusChangeLog))

    print('Populate training_review')
    print('Populate ReviewNote')
    review_notes = []
    ReviewNote = apps.get_model('training_review.ReviewNote')
    for record in records:
        review_notes.extend(_random_review_note(
            record, users[:num_departments], Record, ReviewNote))


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tmsftt_auth', '0001_initial'),
        ('infra', '0002_auto_20190424_1129'),
        ('training_program', '0001_initial'),
        ('training_event', '0001_initial'),
        ('training_record', '0001_initial'),
        ('training_review', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_initial_data),
    ]