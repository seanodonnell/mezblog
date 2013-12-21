import os, sys

sys.path.append("/var/www/django")

os.environ['DJANGO_SETTINGS_MODULE'] = 'mezblog.prod_settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
