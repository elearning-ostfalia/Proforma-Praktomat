
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# This application object is used by the development server
# as well as any WSGI server configured to use this file.

import django.core.handlers.wsgi

#print 'wsgi in praktomat/src'

application = django.core.handlers.wsgi.WSGIHandler()


#as opposed to later versions, who's wsgi.py looks like:

#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mobile_loans.settings")

#from django.core.wsgi import get_wsgi_application
#application = get_wsgi_application()