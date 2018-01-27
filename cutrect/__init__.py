from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app
from .celery import email_if_fails

__all__ = ['celery_app', 'email_if_fails']