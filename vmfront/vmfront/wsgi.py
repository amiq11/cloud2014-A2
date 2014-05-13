"""
WSGI config for vmfront project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os

"sys.path.append('/home/user/cloud2014-A2/vmfront/vmfront')"
"sys.path.append('/home/user/cloud2014-A2/vmfront/vmmanager')"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vmfront.settings")


from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()



