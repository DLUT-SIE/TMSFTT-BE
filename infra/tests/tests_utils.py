'''Unit tests for infra utils.'''
import random
import string

from django.test import TestCase

import infra.utils as utils


class TestPositiveInt(TestCase):
    def test_positive_int(self):
        '''Should return int.'''
        expected = 5
        ret = utils.positive_int(f'{expected}')

        self.assertIsInstance(ret, int)
        self.assertEqual(ret, expected)

    def test_positive_int_with_cutoff(self):
        '''Should cut off int.'''
        expected = 5
        ret = utils.positive_int(f'{expected + 100}', cutoff=5)

        self.assertIsInstance(ret, int)
        self.assertEqual(ret, expected)

    def test_negative_int(self):
        '''Should raise exception if int is negative.'''
        with self.assertRaises(ValueError):
            utils.positive_int('-10')

    def test_zero_with_strict(self):
        '''Should raise exception if int is zero and with strict setting.'''
        with self.assertRaises(ValueError):
            utils.positive_int('0', strict=True)

    def test_zero_without_strict(self):
        '''Should return 0 if int is zero and without strict setting.'''
        expected = 0
        ret = utils.positive_int(f'{expected}', strict=False)

        self.assertIsInstance(ret, int)
        self.assertEqual(ret, expected)


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
            res = utils.format_file_size(size_in_bytes)

            self.assertEqual(res, expected_str)

    def test_format_size_is_too_large(self):
        '''Should raise ValueError if size is too large.'''
        with self.assertRaisesMessage(ValueError, '参数超出转换范围'):
            utils.format_file_size(512 * 1024**6)

    def test_format_size_is_negative(self):
        '''Should raise ValueError if size is negative.'''
        with self.assertRaisesMessage(ValueError, '参数超出转换范围'):
            utils.format_file_size(-100)


class TestEncryptionandDecryption(TestCase):
    '''Unit tests for encrypt() and decrypt().'''
    @staticmethod
    def random_string(length):
        '''Generate random string.'''
        return ''.join(random.SystemRandom().choice(
            string.ascii_uppercase + string.digits) for _ in range(length))

    def test_should_return_same_value(self):
        '''Value should be the same after encrypt-decrypt.'''
        raw_values = (self.random_string(random.randint(i + 10, i + 100))
                      for i in range(20))
        for raw_value in raw_values:
            encrypted = utils.encrypt(raw_value)
            decrypted = utils.decrypt(encrypted)
            self.assertEqual(decrypted, raw_value)

    def test_decrypt_corrupted_data(self):
        '''Should raise ValueError if data is corrupted.'''
        encrypted = utils.encrypt('some data')
        encrypted = encrypted[:-1] + '0'

        with self.assertRaisesMessage(ValueError, '已被篡改的内容'):
            utils.decrypt(encrypted)
