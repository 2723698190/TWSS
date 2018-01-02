"""
WSGI config for MyLittleWebsite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
# import sys

from django.core.wsgi import get_wsgi_application

# sys.path.append('/home/demand_jango')
# sys.path.append('/root/.pyenv/versions/3.6.3/lib/python3.6/site-packages')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MyLittleWebsite.settings")

application = get_wsgi_application()
