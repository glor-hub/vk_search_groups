from __future__ import absolute_import

import os

from celery import Celery

# settings.configure()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vksearch.settings")


celery_app = Celery("vksearch")

celery_app.config_from_object("django.conf:settings", namespace="CELERY")

celery_app.autodiscover_tasks()
