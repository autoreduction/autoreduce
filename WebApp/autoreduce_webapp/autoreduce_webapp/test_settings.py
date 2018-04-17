# pylint: skip-file
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'YOUR-SECRET-KEY'

# SECURITY WARNING: don't run with these turned on in production!
DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = False

ALLOWED_HOSTS = ['localhost', 'reducedev2.isis.cclrc.ac.uk']
INTERNAL_IPS = ['localhost', '127.0.0.1']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'autoreduce_webapp',
    'reduction_viewer',
    'reduction_variables',
    'django_user_agents',
]

MIDDLEWARE_CLASSES = [

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django_user_agents.middleware.UserAgentMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'autoreduce_webapp.backends.UOWSAuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

LOGIN_URL = '/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = 'autoreduce_webapp.urls'

WSGI_APPLICATION = 'autoreduce_webapp.wsgi.application'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'autoreduction',
        'USER': 'test-user',
        'PASSWORD': 'pass',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'
STATIC_PATH = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [
    os.path.join('static'),
]

# Logging
# https://docs.python.org/2/howto/logging.html

LOG_FILE = os.path.join(BASE_DIR, 'autoreduction.log')
if DEBUG:
    LOG_LEVEL = 'INFO'
else:
    LOG_LEVEL = 'INFO'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.FileHandler',
            'filename': LOG_FILE,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'propagate': True,
            'level': LOG_LEVEL,
        },
        'app': {
            'handlers': ['file'],
            'propagate': True,
            'level': 'DEBUG',
        },
    }
}

# ActiveMQ

ACTIVEMQ = {
    'topics': [
        '/queue/DataReady',
        '/queue/ReductionStarted',
        '/queue/ReductionComplete',
        '/queue/ReductionError'
    ],
    'username': 'YOUR-ACTIVEMQ-USERNAME',
    'password': 'YOUR-ACTIVEMQ-PASSWORD',
    'broker': [("YOUR-ACTIVE-MQ-HOST", 61613)],
    'SSL': False
}

# File Locations

if os.name == 'nt':
    REDUCTION_DIRECTORY = r'\\isis\inst$\NDX%s\user\scripts\autoreduction'  # %(instrument)
    ARCHIVE_DIRECTORY = r'\\isis\inst$\NDX%s\Instrument\data\cycle_%s\autoreduced\%s\%s'  # %(instrument, cycle, experiment_number, run_number)

    TEST_REDUCTION_DIRECTORY = r'\\reducedev\isis\output\NDX%s\user\scripts\autoreduction'
    TEST_ARCHIVE_DIRECTORY = '\\isis\inst$\NDX%s\Instrument\data\cycle_%s\autoreduced\%s\%s'

else:
    REDUCTION_DIRECTORY = '/isis/NDX%s/user/scripts/autoreduction'  # %(instrument)
    ARCHIVE_DIRECTORY = '/isis/NDX%s/Instrument/data/cycle_%s/autoreduced/%s/%s'  # %(instrument, cycle, experiment_number, run_number)

    TEST_REDUCTION_DIRECTORY = '/reducedev/isis/output/NDX%s/user/scripts/autoreduction'
    TEST_ARCHIVE_DIRECTORY = '/isis/NDX%s/Instrument/data/cycle_%s/autoreduced/%s/%s'

# ICAT

ICAT = {
    'AUTH': 'YOUR-ICAT-AUTH',
    'URL': 'YOUR-ICAT-WSDL',
    'USER': 'YOUR-ICAT-USERNAME',
    'PASSWORD': 'YOUR-ICAT-PASSWORD'
}

# Outdated Browsers

OUTDATED_BROWSERS = {
    'IE': 9,
}

# UserOffice WebService

UOWS_URL = 'https://fitbaweb1.isis.cclrc.ac.uk:8443/UserOfficeWebService/UserOfficeWebService?wsdl'
UOWS_LOGIN_URL = 'https://users.facilities.rl.ac.uk/auth/?service=http://reduce.isis.cclrc.ac.uk&redirecturl='

# Email for notifications

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'exchsmtp.stfc.ac.uk'
EMAIL_PORT = 25
EMAIL_ERROR_RECIPIENTS = ['isisreduce@stfc.ac.uk']
EMAIL_ERROR_SENDER = 'autoreducedev@reduce.isis.cclrc.ac.uk'
BASE_URL = 'http://reduce.isis.cclrc.ac.uk/'
CERTIFICATE_LOCATION = 'C:\\certificates\\FITBAWEB1isiscclrcacuk.crt'

# Constant vars
SESSION_COOKIE_AGE = 3600  # The MAX length before user is logged out, 1 hour in seconds
FACILITY = "ISIS"
PRELOAD_RUNS_UNDER = 100  # If the index run list has fewer than this many runs to show the user, preload them all.
CACHE_LIFETIME = 3600  # Objects in ICATCache live this many seconds when ICAT is available to update them.
USER_ACCESS_CHECKS = False  # Should the webapp prevent users from accessing runs/instruments they're not allowed to?
DEVELOPMENT_MODE = True  # If the installation is in a development environment, set this variable to True so that
                         # we are not constrained by having to log in through the user office. This will authenticate
                         # anyone visiting the site as a super user
