"""
WSGI config for mojprojekt project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/

Usage:
  Production server (e.g. Gunicorn):
    gunicorn mojprojekt.wsgi:application

  Development server (manage.py):
    python manage.py runserver   <-- preferred for development
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mojprojekt.settings')

application = get_wsgi_application()
