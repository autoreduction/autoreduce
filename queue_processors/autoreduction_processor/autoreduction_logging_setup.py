# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
# pylint: skip-file
import logging.handlers
import os

from utils.project.structure import get_project_root

LOGGING_LEVEL = logging.INFO
LOGGING_LOC = os.path.join(get_project_root(), 'logs', 'autoreduction_processor.log')

logger = logging.getLogger('AutoreductionProcessor')
logger.setLevel(LOGGING_LEVEL)
handler = logging.handlers.RotatingFileHandler(LOGGING_LOC, maxBytes=104857600, backupCount=20)
handler.setLevel(LOGGING_LEVEL)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# Quiet the Stomp logs as they are quite chatty
logging.getLogger('stomp').setLevel(logging.INFO)
