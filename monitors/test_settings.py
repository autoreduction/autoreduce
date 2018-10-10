# pylint: skip-file
"""
Settings for End of run monitor
"""
import os

from utils.project.structure import get_project_root

# Config settings for cycle number, and instrument file arrangement
INST_FOLDER = os.path.join(get_project_root(), 'data-archive', 'NDX%s', 'Instrument')
DATA_LOC = os.path.join('data', 'cycle_%s')
SUMMARY_LOC = os.path.join('logs', 'journal', 'summary.txt')
LAST_RUN_LOC = os.path.join('logs', 'lastrun.txt')
LOG_FILE = os.path.join(get_project_root(), 'logs', 'monitor.log')
INSTRUMENTS = [{'name': 'WISH', 'use_nexus': True},
               {'name': 'GEM', 'use_nexus': True},
               {'name': 'OSIRIS', 'use_nexus': True},
               {'name': 'POLARIS', 'use_nexus': True},
               {'name': 'MUSR', 'use_nexus': True},
               {'name': 'POLREF', 'use_nexus': True}]
