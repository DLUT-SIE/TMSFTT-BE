'''Unit tests for auth serializers.'''
from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase
from model_mommy import mommy

import auth.serializers as serializers
import auth.models as models


User = get_user_model()

# TODO: rewrite test_get_admins_no_role function
# TODO: rewrite test_get_admins function
