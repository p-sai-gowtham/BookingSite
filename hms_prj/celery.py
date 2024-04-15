import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hms_prj.settings')

app = Celery('hms_prj')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
