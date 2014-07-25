import os
import sys

path = '/var/www/html/django'
if path not in sys.path:
    sys.path.append(path)
print sys.path

os.environ['PYTHON_EGG_CACHE'] = '/var/www/html/django/eggs'
os.environ['DJANGO_SETTINGS_MODULE'] = 'gltest.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
