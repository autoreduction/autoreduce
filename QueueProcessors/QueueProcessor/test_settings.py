# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2019 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
# pylint: skip-file
import os
from utils.project.structure import get_project_root

FACILITY = 'ISIS'

MYSQL = {
    'HOST': 'localhost:3306',
    'USER': 'test-user',
    'PASSWD': 'pass',
    'DB': 'autoreduction'
}

# Logging
LOG_FILE = os.path.join(get_project_root(), 'logs', 'queue_processor.log')
DEBUG = False

if DEBUG:
    LOG_LEVEL = 'DEBUG'
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
        'queue_processor': {
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

# Directory Locations
if os.name == 'nt':
    # %(instrument)
    REDUCTION_DIRECTORY = r'\\isis\inst$\NDX%s\user\scripts\autoreduction'
    # %(instrument, cycle, experiment_number, run_number)
    ARCHIVE_DIRECTORY = r'\\isis\inst$\NDX%s\Instrument\data\cycle_%s\autoreduced\%s\%s'

    TEST_REDUCTION_DIRECTORY = r'\\reducedev\isis\output\NDX%s\user\scripts\autoreduction'
    TEST_ARCHIVE_DIRECTORY = r'\\isis\inst$\NDX%s\Instrument\data\cycle_%s\autoreduced\%s\%s'

else:
    # %(instrument)
    # REDUCTION_DIRECTORY = '/isis/NDX%s/user/scripts/autoreduction'
    REDUCTION_DIRECTORY = os.path.join(get_project_root(), 'data-archive', 'NDX%s',
                                       'user', 'scripts', 'autoreduction')
    # %(instrument, cycle, experiment_number, run_number)
    # ARCHIVE_DIRECTORY = '/isis/NDX%s/Instrument/data/cycle_%s/autoreduced/%s/%s'
    ARCHIVE_DIRECTORY = os.path.join(get_project_root(), 'data-archive', 'NDX%s',
                                     'Instrument', 'data', 'cycle_%s', 'autoreduced',
                                     '%s', '%s')

    TEST_REDUCTION_DIRECTORY = '/reducedev/isis/output/NDX%s/user/scripts/autoreduction'
    TEST_ARCHIVE_DIRECTORY = '/isis/NDX%s/Instrument/data/cycle_%s/autoreduced/%s/%s'

# Email for notifications
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'exchsmtp.stfc.ac.uk'
EMAIL_PORT = 25
EMAIL_ERROR_RECIPIENTS = ['YOUR-EMAIL']
EMAIL_ERROR_SENDER = 'autoreduce@reduce.isis.cclrc.ac.uk'
BASE_URL = 'http://reduce.isis.cclrc.ac.uk/'
