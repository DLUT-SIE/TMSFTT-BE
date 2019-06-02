#!/usr/bin/env python
import os
import sys
import logging

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        os.environ['DJANGO_SETTINGS_MODULE'] = 'TMSFTT.settings_ci'
        logging.disable(logging.WARN)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TMSFTT.settings_dev')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
