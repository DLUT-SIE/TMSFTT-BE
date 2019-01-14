'''Unit tests for django_cas cas_protocols.'''
from unittest.mock import patch, Mock
from django.test import TestCase


from django_cas.cas_protocols import _verify_cas2


class TestCASProtocol2(TestCase):
    '''Unit tests for CAS 2.0+ XML-based authentication.'''
    @patch('django_cas.cas_protocols.urlopen')
    def test_verification_succeed(self, mocked_urlopen):
        '''Should return tag text when verification succeed.'''
        username = 'username'
        page = Mock()
        page.read.return_value = '''
<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
    <cas:authenticationSuccess>
        <cas:username>{}</cas:username>
        </cas:authenticationSuccess>
</cas:serviceResponse>
        '''.format(username)
        mocked_urlopen.return_value = page

        result = _verify_cas2('ticket', 'service')

        self.assertEqual(result, (username, None))

    @patch('django_cas.cas_protocols.urlopen')
    def test_verification_failed(self, mocked_urlopen):
        '''Should return tag text when verification succeed.'''
        page = Mock()
        page.read.return_value = '''
<cas:serviceResponse xmlns:cas='http://www.yale.edu/tp/cas'>
    <cas:authenticationFailure>
        Invalid user.
    </cas:authenticationFailure>
</cas:serviceResponse>
        '''
        mocked_urlopen.return_value = page

        result = _verify_cas2('ticket', 'service')

        self.assertEqual(result, (None, None))
