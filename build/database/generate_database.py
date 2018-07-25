"""
Python wraps to windows/linux schema generation scripts for services
"""
from __future__ import print_function

import os
import subprocess
import sys

from build.utils.process_runner import run_process_and_log

PATH_TO_DIR = os.path.dirname(os.path.realpath(__file__))


def run_sql_file(sql_file_location, logger):
    """
    Runs a sql file on the localhost database
    :param sql_file_location: file path to the sql file
    :param logger: log handler
    :return: True: exit code of script was 0
             False: exit code of script was non-zero
    """
    from build.settings import DB_ROOT_PASSWORD  # Must be imported at run-time for migrate test settings to work
    logger.info("Running script: %s" % sql_file_location)
    with open(sql_file_location, 'r') as input_file:
        password = ''
        if DB_ROOT_PASSWORD:
            password = 'MYSQL_PWD=%s ' % DB_ROOT_PASSWORD
        access_string = "mysql -u{0} {1}".format('root', password)
        mysql_process = subprocess.Popen(access_string,
                                         stdin=input_file, shell=True,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
        process_output, process_err = mysql_process.communicate()
        if process_output != '':
            logger.info(process_output)
        if process_err != '':
            logger.error(process_err)
            print("Script did not complete. Check build.log for more details.")
            print(process_err, file=sys.stderr)
            return False
    logger.info("Script completed successfully")
    return True


def generate_schema(project_root_path, logger):
    """
    Call django migrations to create testing database schema
    :param project_root_path: The full path to the root directory of the project
    :param logger: log handler
    :return: True: exit code of script was 0
             False: exit code of script was non-zero
    """
    path_to_manage = os.path.join(project_root_path, 'WebApp', 'autoreduce_webapp', 'manage.py')
    for database in ['admin', 'sessions', 'auth', 'reduction_viewer', 'reduction_variables']:
        logger.info("Migrating %s" % database)
        if run_process_and_log(['python', path_to_manage, 'makemigrations', database]) is False:
            logger.error("Error encountered when makingmigrations for %s" % database)
            return False
        if run_process_and_log(['python', path_to_manage, 'migrate', database]) is False:
            logger.error("Error encountered when migrating %s" % database)
            return False

    logger.info("Adding super user")
    # Custom manage.py command
    if run_process_and_log(['python', path_to_manage, 'add_super']) is False:
        logger.error("Error encountered when adding super user")
        return False
    logger.info("Database migrated successfully")
    return True

def add_test_user(logger):
    # Must be imported at run-time for migrate test settings to work
    from build.settings import DB_ROOT_PASSWORD
    from utils.settings import MYSQL
    user_to_add = MYSQL["USER"]
    logger.info("Adding user: {0}".format(user_to_add))
    sql_commands = ["GRANT ALL ON *.* TO '{0}'@'localhost' IDENTIFIED BY '{1}';".format(user_to_add, MYSQL["PASSWD"]),
                    "FLUSH PRIVILEGES;"]

    to_exec = '\n'.join(sql_commands)

    # This is duplicated from above, ideally we should switch to using Python-MySQL connectors
    password = '' if not DB_ROOT_PASSWORD else 'MYSQL_PWD=%s ' % DB_ROOT_PASSWORD
    access_string = "mysql -u{0} {1}".format('root', password)
    mysql_process = subprocess.Popen(access_string,
                                     stdin=subprocess.PIPE, shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE)
    process_output, process_err = mysql_process.communicate(input=to_exec)
    if process_output != '':
        logger.info(process_output)
    if process_err != '':
        logger.error(process_err)
        print("Script did not complete. Check build.log for more details.")
        print(process_err, file=sys.stderr)
        return False
    return True
