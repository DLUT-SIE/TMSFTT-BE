'''Provide CAS protocols.'''
from urllib.parse import urlencode, urljoin
from urllib.request import urlopen
try:
    from xml.etree import ElementTree
except ImportError:  # pragma: no cover
    from elementtree import ElementTree

from django.conf import settings


__all__ = ['CAS_PROTOCOLS']


def _verify_cas2(ticket, service):
    """Verifies CAS 2.0+ XML-based authentication ticket.

    Returns username on success and None on failure.
    """
    params = {'ticket': ticket, 'service': service}
    url = (urljoin(settings.CAS_SERVER_URL, 'proxyValidate') + '?' +
           urlencode(params))
    page = urlopen(url)
    try:
        response = page.read()
        tree = ElementTree.fromstring(response)
        if tree[0].tag.endswith('authenticationSuccess'):
            return tree[0][0].text, None
        return None, None
    finally:
        page.close()


CAS_PROTOCOLS = {
    '2': _verify_cas2,
}
