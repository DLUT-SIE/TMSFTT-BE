import hashlib
import os.path as osp
from itertools import product
from unittest.mock import Mock

from django.test import TestCase
from django.utils import timezone

from infra.utils import CustomHashPath


class TestCustomHashPath(TestCase):
    def test_eq(self):
        combinations = list(product(
            ['base0', 'base1'],
            [True, False],
            [True, False]))

        for args0 in combinations:
            for args1 in combinations:
                hash_path0 = CustomHashPath(*args0)
                hash_path1 = CustomHashPath(*args1)
                self.assertEqual(hash_path0 == hash_path1, args0 == args1)

    def test_call(self):
        base = 'uploads'
        filename = 'abc.txt'
        file_content = b'123'
        user_id = 1
        combinations = list(product(
            [True, False],
            [True, False]))

        def generate_path_format(base, by_date, by_user):
            path_format = '{base}'
            if by_date:
                path_format = osp.join(path_format, '{date}')
            if by_user:
                path_format = osp.join(path_format, 'user_{user}')
            path_format = osp.join(path_format, '{fname}_{fingerprint}.{ext}')
            return path_format

        for by_date, by_user in combinations:
            expected_path_format = generate_path_format(base, by_date, by_user)
            hasher = hashlib.md5()
            hasher.update(file_content)
            fingerprint = hasher.hexdigest()
            date = timezone.now().strftime('%Y/%m/%d')
            fname, ext = osp.splitext(filename)
            expected_path = expected_path_format.format(
                base=base,
                date=date,
                user=user_id,
                fname=fname,
                fingerprint=fingerprint,
                ext=ext)
            mocked_instance = Mock()
            mocked_instance.path.read.return_value = file_content
            mocked_instance.user.id = user_id

            hash_path = CustomHashPath(base, by_date, by_user)
            path = hash_path(mocked_instance, filename)

            self.assertEqual(path, expected_path)
