"""
WSGI config for s_store project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

if os.path.isfile(os.path.join(os.path.dirname(__file__), 's_store', 'local_settings.py')):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 's_store.local_settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 's_store.settings')

application = get_wsgi_application()
