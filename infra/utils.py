'''Provide useful utilities shared among modules.'''
from rest_framework.renderers import BrowsableAPIRenderer


def format_file_size(size_in_bytes):
    '''Format human-readable file size.'''
    if size_in_bytes < 0 or size_in_bytes >= 1024**6:
        raise ValueError('参数超出转换范围')
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    val = size_in_bytes
    unit_idx = 0
    while val / 1024 > 1:
        unit_idx += 1
        val /= 1024
    return '{:.2f} {}'.format(val, units[unit_idx])


class BrowsableAPIRendererWithoutForms(
        BrowsableAPIRenderer):  # pragma: no cover
    """Renders the browsable api, but excludes the forms."""

    # pylint: disable=arguments-differ
    def get_context(self, *args, **kwargs):
        ctx = super().get_context(*args, **kwargs)
        ctx['display_edit_forms'] = False
        return ctx

    def show_form_for_method(self, view, method, request, obj):
        """We never want to do this! So just return False."""
        return False

    def get_rendered_html_form(self, data, view, method, request):
        """Why render _any_ forms at all. This method should return
        rendered HTML, so let's simply return an empty string.
        """
        return ''
