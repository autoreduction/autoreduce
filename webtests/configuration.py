# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Module containing configuration functions. Configuration file must be used as a thread safe way to
share values between xdist workers does not currently exist.
"""
import json
import sys
from pathlib import Path
from shutil import copyfile

from utils.project.structure import get_project_root

CONFIG_PATH = Path(get_project_root(), "webtests/config.json")
TEMP_CONFIG_PATH = Path(get_project_root(), "webtests/temp_config.json")


def store_original_config():
    """
    Make a copy of the config file to a temporary file. This prevents arguments given to the test
     entrypoint being persisted to the config file.
    """
    try:
        copyfile(CONFIG_PATH, TEMP_CONFIG_PATH)
    except FileNotFoundError:
        sys.exit(f"Config is missing please create: {CONFIG_PATH}")


def is_local_environment():
    """
    Returns true if the environment type in the config is set to local
    :return: (bool) True if the environment type in the config is set to local
    """
    return load_config_file()["environment_type"].lower() == "local"


def get_url():
    """
    Returns the url to test against from the config
    :return: (str) The url to test against from the config
    """

    return load_config_file()["url"]


def is_headless():
    """
    Returns the headless boolean from the config
    :return: (bool) The headless boolean from the config
    """
    return load_config_file()["run_headless"]


def set_environment(environment):
    """
    Set the environment type in the config. Either local or remote
    :param environment: (str) the environment type to be set
    """
    config = load_config_file()
    config["environment_type"] = environment
    dump_to_config_file(config)


def set_url(url):
    """
    Set the url to test against in the config. IPs must be prefixed with http/https still
    :param url: (str) The url to test against
    """
    config = load_config_file()
    config["url"] = url
    dump_to_config_file(config)


def set_headless(headless):
    """
    Set the headless option in the config to decide whether or not to use a headless driver
    :param headless: (bool) the headless bool option
    """
    config = load_config_file()
    config["run_headless"] = headless
    dump_to_config_file(config)


def cleanup_config():
    """
    Copy the original values back to the original config file, so as not to persist arguments given
    to test runner
    """
    copyfile(TEMP_CONFIG_PATH, CONFIG_PATH)
    if TEMP_CONFIG_PATH.exists():
        TEMP_CONFIG_PATH.unlink()


def load_config_file():
    """
    Load the config file into a python dictionary
    :return: (dict) The config file as a python dictionary
    """
    try:
        with open(CONFIG_PATH) as fle:
            return json.load(fle)
    except FileNotFoundError:
        sys.exit(f"Config file is missing. Please create: {str(CONFIG_PATH)}")


def dump_to_config_file(config_dict):
    """
    Dump the given dictionary to the config file
    :param config_dict: (dict) the dictionary to be dumped.
    """
    with open(CONFIG_PATH, "w") as fle:
        json.dump(config_dict, fle, indent=4)
