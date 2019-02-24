'''Unit tests for infra utils.'''
from django.test import TestCase

from infra.utils import format_file_size


class TestFormatFileSize(TestCase):
    '''Unit tests for format_file_size().'''

    def test_format_bytes(self):
        '''Should format size in bytes.'''
        test_cases = (
            (512, '512.00 B'),  # 512 B
            (512 * 1024**1, '512.00 KB'),  # 512 KB
            (512 * 1024**2, '512.00 MB'),  # 512 MB
            (512 * 1024**3, '512.00 GB'),  # 512 GB
            (512 * 1024**4, '512.00 TB'),  # 512 TB
            (512 * 1024**5, '512.00 PB'),  # 512 PB
        )

        for size_in_bytes, expected_str in test_cases:
            res = format_file_size(size_in_bytes)

            self.assertEqual(res, expected_str)

    def test_format_size_is_too_large(self):
        '''Should raise ValueError if size is too large.'''
        with self.assertRaisesMessage(ValueError, '参数超出转换范围'):
            format_file_size(512 * 1024**6)

    def test_format_size_is_negative(self):
        '''Should raise ValueError if size is negative.'''
        with self.assertRaisesMessage(ValueError, '参数超出转换范围'):
            format_file_size(-100)
