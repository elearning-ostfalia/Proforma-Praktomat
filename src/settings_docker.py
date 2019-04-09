# -*- coding: utf-8 -*-
# settings which depend on the machine django runs on 
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
# This will show debug information in the browser if an exception occurs.
# Note that there are always going to be sections of your debug output that 
# are inappropriate for public consumption. File paths, configuration options, 
# and the like all give attackers extra information about your server.
# Never deploy a site into production with DEBUG turned on.
if os.getenv('DJANGO_ENV') == 'prod':
    DEBUG = False
    ALLOWED_HOSTS = ["*", ]
else:
    DEBUG = True
    ALLOWED_HOSTS = ["*", ]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de'

# The name that will be displayed on top of the page and in emails.
SITE_NAME = 'Praktomat'

# The URL where this site is reachable. 'http://localhost:8000/' in case of the development server.
BASE_URL = 'http://localhost:80/'

# URL that serves the static media files (CSS, JavaScript and images) of praktomat contained in 'media/'.
# Make sure to use a trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = BASE_URL + 'media/'

# URL prefix for the administration site media (CSS, JavaScript and images) contained in the django package. 
# Make sure to use a trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'
# where to put static django admin files 
STATIC_ROOT='/praktomat/media/'

STATIC_URL=BASE_URL[:-1] +ADMIN_MEDIA_PREFIX

# Absolute path to the directory that shall hold all uploaded files as well as files created at runtime.
# Example: "/home/media/media.lawrence.com/"
UPLOAD_ROOT = "/praktomat/upload"


ADMINS = [
          # ('Your Name', 'your_email@domain.com'),
          ]
if 'DB_NAME' in os.environ:
    # Running the Docker image
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ['DB_NAME'],
            'USER': os.environ['DB_USER'],
            'PASSWORD': os.environ['DB_PASS'],
            'HOST': os.environ['DB_DOCKER_SERVICE'],
            'PORT': os.environ['DB_PORT']
        }
    }
else:
    # Building the Docker image
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# uncomment to activate sendmail
# EMAIL_BACKEND = 'django_sendmail_backend.backends.EmailBackend'
# DEFAULT_FROM_EMAIL = "localhost"

#DEFAULT_FROM_EMAIL = ""
#EMAIL_HOST = "smtp.googlemail.com"
#EMAIL_PORT = 587
#EMAIL_HOST_USER = ""
#EMAIL_HOST_PASSWORD = ""
#EMAIL_USE_TLS = True

# Private key used to sign uploaded solution files in submission confirmation email
PRIVATE_KEY = ''

MANAGERS = ADMINS

# Length of timeout applied whenever an external check that runs a students
# submission is executed,
# for example: JUnitChecker
TEST_TIMEOUT = 15

# Maximal size (in kbyte) of files created whenever an external check that
# runs a students submission is executed,
# for example: JUnitChecker, DejaGnuChecker
TEST_MAXFILESIZE = 64

# Maximal size (in kbyte) of checker logs accepted. This setting is
# respected currently only by:
# JUnitChecker, ScriptChecker,
TEST_MAXLOGSIZE = 64

# The Compiler binaries used to compile a submitted solution
JAVAP = 'javap'
JCLASSINFO = 'jclassinfo'
C_BINARY = 'gcc'
CXX_BINARY = 'c++'
JAVA_BINARY = 'javac'
JAVA_BINARY_SECURE = 'javac'
JAVA_GCC_BINARY = 'gcj'
JVM = 'java'
JVM_SECURE = '/praktomat/src/checker/scripts/java'
FORTRAN_BINARY = 'g77'
DEJAGNU_RUNTEST = 'runtest'
CHECKSTYLEALLJAR = '/praktomat/extra/checkstyle-6.2-all.jar'
JUNIT38 = 'junit'
JAVA_LIBS = {'junit3': '/praktomat/extra/junit-3.8.jar',
             'junit4': '/praktomat/extra/junit-4.10.jar',
             'junit4.12': '/praktomat/extra/junit-4.12.jar:'
             '/praktomat/extra/hamcrest-core-1.3.jar',
             'junit4.12-gruendel': '/praktomat/extra/junit-4.12.jar:/praktomat/extra/JUnit4AddOn.jar:/praktomat/extra/hamcrest-core-1.3.jar'}
CHECKSTYLE_VER = {'check-6.2': '/praktomat/extra/checkstyle-6.2-all.jar',
                  'check-7.6': '/praktomat/extra/checkstyle-7.6-all.jar',
                  'check-5.4': '/praktomat/extra/checkstyle-7.6-all.jar'}
JCFDUMP = 'jcf-dump'
SETLXJAR = '/praktomat/extra/setlX.jar'


# Enable to run all scripts (checker) as the unix user 'tester'. Therefore put 'tester' as well
# as the Apache user '_www' (and your development user account) into a new group called praktomat. Also edit your
# sudoers file with "sudo visudo". Add the following lines to the end of the file to allow the execution of 
# commands with the user 'tester' without requiring a password:
# "_www    		ALL=(tester)NOPASSWD:ALL"
# "developer	ALL=(tester)NOPASSWD:ALL"
USEPRAKTOMATTESTER = False


