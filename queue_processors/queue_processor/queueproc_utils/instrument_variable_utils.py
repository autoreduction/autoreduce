# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Module for dealing with instrument reduction variables.
"""
import importlib.util as imp
import io
import logging.config
import os
import html

import chardet

# pylint:disable=no-name-in-module,import-error
from queue_processors.queue_processor.settings import REDUCTION_DIRECTORY, LOGGING
from queue_processors.queue_processor.queueproc_utils.variable_utils import VariableUtils

from model.database import access as db

# Set up logging and attach the logging to the right part of the config.
logging.config.dictConfig(LOGGING)
logger = logging.getLogger("queue_processor")  # pylint: disable=invalid-name


class DataTooLong(ValueError):
    """ Error class used for when reduction variables are too long. """


class InstrumentVariablesUtils:
    """ Class used to parse and process instrument reduction variables. """
    @staticmethod
    def log_error_and_notify(message):
        """
        Helper method to log an error and save a notification
        """
        logger.error(message)
        model = db.start_database().data_model
        notification = model.Notification(is_active=True,
                                          is_staff_only=True,
                                          severity='e',
                                          message=message)
        db.save_record(notification)

    def show_variables_for_run(self, instrument_name, run_number=None):
        """
        Look for the applicable variables for the given run number. If none are set, return an empty
        list (or QuerySet) anyway.
        """
        instrument = db.get_instrument(instrument_name)
        variable_run_number = 0

        # If we haven't been given a run number, we should try to find it.
        model = db.start_database().variable_model
        if not run_number:
            applicable_variables = model.InstrumentVariable.objects \
                .filter(instrument_id=instrument.id) \
                .order_by('-start_run')
            if applicable_variables:
                variable_run_number = applicable_variables[0].start_run
        else:
            variable_run_number = run_number

        # Find variable records associated with instrument variables
        variables = self.find_var_records_for_inst_vars(instrument.id, variable_run_number)

        # If we have found some variables then we want to use them by first making copies of them
        # and sending them back to be used. This means we don't alter the previous set of variables.
        # If we haven't found any variables, just return an empty list.
        if variables:
            self._update_variables(variables)
            new_variables = []
            for variable in variables:
                new_variables.append(VariableUtils().copy_variable(variable))
            return new_variables
        return []

    def get_default_variables(self, instrument_name, reduce_script=None):
        """
        Creates and returns a list of variables from the reduction script on disk for the
        instrument. If reduce_script is supplied, return variables using that script instead of the
        one on disk.
        """
        if not reduce_script:
            reduce_script = self._load_reduction_vars_script(instrument_name)

        reduce_vars_module = self._read_script(reduce_script,
                                               os.path.join(self._reduction_script_location(
                                                   instrument_name), 'reduce_vars.py'))

        if not reduce_vars_module:
            return []

        instrument = db.get_instrument(instrument_name)
        variables = []
        # pylint:disable=no-member
        if 'standard_vars' in dir(reduce_vars_module):
            variables.extend(
                self._create_variables(instrument,
                                       reduce_vars_module,
                                       reduce_vars_module.standard_vars,
                                       False))

        if 'advanced_vars' in dir(reduce_vars_module):
            variables.extend(
                self._create_variables(instrument,
                                       reduce_vars_module,
                                       reduce_vars_module.advanced_vars,
                                       True))

        logger.error("**********************************************")
        logger.error("After creating variables we have:")
        logger.error("**********************************************")
        for var in variables:
            logger.error("%s with id: %s, and name: %s and value: %s",
                         var, var.id, var.name, var.value)
            var.tracks_script = True

        model = db.start_database().variable_model
        applicable_variables = model.InstrumentVariable.objects \
            .filter(instrument_id=instrument.id) \
            .order_by('-start_run')
        variable_run_number = applicable_variables[0].start_run

        variables = self.find_var_records_for_inst_vars(instrument.id, variable_run_number)

        return variables

    @staticmethod
    def find_var_records_for_inst_vars(instrument_id, start_run):
        """
        Returns a list of the variables that are associated with a given instrument instance
        e.g. return all the Variable objects that are associated with a given set of
             InstrumentVariables with a start run of 123
        :param instrument_id: (int) The id of the instrument to use
        :param start_run: (int) The start run of the instrument variable
        :return: (list) of all Variable objects matching the criteria
        """
        model = db.start_database().variable_model
        instrument_var_records = model.InstrumentVariable.objects \
            .filter(instrument_id=instrument_id) \
            .filter(start_run=start_run)
        variables = []
        for record in instrument_var_records:
            variables.append(model.Variable.objects.filter(id=record.variable_ptr_id).first())
        return variables

    def _update_variables(self, variables, save=True):
        """
        Updates all variables with tracks_script to their value in the script, and append any new
        ones. This assumes that the variables all belong to the same instrument, and that the list
        supplied is complete. If no variables have tracks_script set, we won't do anything at all.
        variables should be a list; it needs to be mutable so that this function can add/remove
        variables. If the 'save' option is true, it will save/delete the variables from the
        database as required.
        """
        if not any([hasattr(var, "tracks_script") and var.tracks_script for var in variables]):
            return

        # New variable set from the script
        defaults = self.get_default_variables(variables[0].instrument.name) if variables else []

        def update_variable(old_var):
            """ Update the existing variables. """
            old_var.keep = True
            # Find the new variable from the script.
            matching_vars = [variable for variable in defaults if old_var.name == variable.name]

            # Check whether we should and can update the old one.
            if matching_vars and old_var.tracks_script:
                new_var = matching_vars[0]
                map(lambda name: setattr(old_var, name, getattr(new_var, name)),
                    ["value", "type", "is_advanced",
                     "help_text"])  # Copy the new one's important attributes onto the old variable.
                if save:
                    db.save_record(old_var)
            elif not matching_vars:
                # Or remove the variable if it doesn't exist any more.
                if save:
                    db.save_record(old_var)
                old_var.keep = False
            return old_var

        variables = list(map(update_variable, variables))
        variables[:] = [var for var in variables if var.keep]

        # Add any new ones
        current_names = [var.name for var in variables]
        new_vars = [var for var in defaults if var.name not in current_names]

        def copy_metadata(new_var):
            """ Copy the source variable's metadata to the new one. """
            source_var = variables[0]
            model = db.start_database().variable_model
            if isinstance(source_var, model.InstrumentVariable):
                map(lambda name: setattr(new_var, name, getattr(source_var, name)),
                    ["instrument", "experiment_reference", "start_run"])
            elif isinstance(source_var, model.RunVariable):
                # Create a run variable.
                VariableUtils().derive_run_variable(new_var, source_var.reduction_run)
            else:
                return
            db.save_record(new_var)

        map(copy_metadata, new_vars)
        variables += list(new_vars)

    @staticmethod
    def _reduction_script_location(instrument_name):
        """ Get reduction script location. """
        return REDUCTION_DIRECTORY % instrument_name

    def _load_reduction_script(self, instrument_name):
        """ Loads reduction script. """
        return self._load_script(os.path.join(self._reduction_script_location(instrument_name),
                                              'reduce.py'))

    def _load_reduction_vars_script(self, instrument_name):
        """ Loads reduction variables script. """
        return self._load_script(os.path.join(self._reduction_script_location(instrument_name),
                                              'reduce_vars.py'))

    def _read_script(self, script_text, script_path):
        """
        Takes a python script as a text string, and returns it loaded as a module.
        Failure will return None, and notify.
        """
        if not script_text or not script_path:
            return None

        # file name without extension
        module_name = os.path.basename(script_path).split(".")[0]
        try:
            spec = imp.spec_from_file_location(module_name, script_path)
            module = imp.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except ImportError as exp:
            self.log_error_and_notify(
                "Unable to load reduction script %s due to missing import. (%s)" % (script_path,
                                                                                    exp))
            return None
        except SyntaxError:
            self.log_error_and_notify("Syntax error in reduction script %s" % script_path)
            return None

    def _create_variables(self, instrument, script, variable_dict, is_advanced):
        """ Create variables in the database. """
        variables = []
        logging.warning("Creating variable")
        for key, value in list(variable_dict.items()):
            str_value = str(value).replace('[', '').replace(']', '')
            if len(str_value) > 300:
                raise DataTooLong
            model = db.start_database().variable_model
            logging.warning("name=%s", key)
            logging.warning("value=%s", str_value)
            logging.warning("type=%s", VariableUtils().get_type_string(value))
            logging.warning("is_advanced=%s", is_advanced)
            logging.warning("help_text=%s", self._get_help_text('standard_vars',
                                                                key,
                                                                instrument.name,
                                                                script))

            variable = model.Variable(name=key,
                                      value=str_value,
                                      type=VariableUtils().get_type_string(value),
                                      is_advanced=is_advanced,
                                      help_text=self._get_help_text('standard_vars',
                                                                    key,
                                                                    instrument.name,
                                                                    script))

            logger.error("before create fake var")
            fake_var = model.Variable(name='elliot',
                                      value='val',
                                      type='str',
                                      is_advanced=False,
                                      help_text='help text')
            logger.error("fake var before save: %s", fake_var)
            db.save_record(fake_var)
            logger.error("fake_var after save: %s", fake_var)

            logger.error("created variable: %s", variable)

            db.save_record(variable)

            logger.error("Saved record: %s", variable)

            retrieve_var = model.Variable.objects.filter(id=variable.id).first()
            logger.error("Found var: %s with id: %s and name: % and value: %s",
                         retrieve_var,
                         retrieve_var.id,
                         retrieve_var.name,
                         retrieve_var.value)

            instrument_variable = model.InstrumentVariable(start_run=0,
                                                           instrument_id=instrument.id,
                                                           variable_ptr_id=variable.id,
                                                           tracks_script=1)

            db.save_record(instrument_variable)
            retrieve_var = model.InstrumentVariable.objects.filter(id=instrument_variable.id).first()
            logger.error("Found var: %s with inst: %s and variable: s% ",
                         retrieve_var,
                         retrieve_var.instrument,
                         retrieve_var.variable)

            variables.append(instrument_variable)
        return variables

    def get_current_script_text(self, instrument_name):
        """
        Fetches the reduction script and variables script for the given
        instrument, and returns each as a string.
        """
        script_text = self._load_reduction_script(instrument_name)
        script_vars_text = self._load_reduction_vars_script(instrument_name)
        return script_text, script_vars_text

    def _load_script(self, path):
        """
        First detect the file encoding using chardet.
        Then load the relevant reduction script and return back the text of the script.
        If the script cannot be loaded, None is returned.
        """
        try:
            # Read raw bytes and determine encoding
            f_raw = io.open(path, 'rb')
            encoding = chardet.detect(f_raw.read(32))["encoding"]

            # Read the file in decoded; io is used for the encoding kwarg
            f_decoded = io.open(path, 'r', encoding=encoding)
            script_text = f_decoded.read()
            return script_text
        except Exception as exp:  # pylint: disable = broad-except
            self.log_error_and_notify("Unable to load reduction script %s - %s" % (path, exp))
            return None

    def create_variables_for_run(self, reduction_run):
        """
        Finds the appropriate InstrumentVariables for the given reduction run, and creates
        RunVariables from them. If the run is a re-run, use the previous run's variables.
        If instrument variables set for the run's experiment are found, they're used.
        Otherwise if variables set for the run's run number exist, they'll be used.
        If not, the instrument's default variables will be used.
        """
        instrument_name = reduction_run.instrument.name

        variables = []

        if not variables:
            logger.info('Finding variables from experiment')
            # No previous run versions. Find the instrument variables we want to use.
            variables = self.\
                show_variables_for_experiment(instrument_name,
                                              reduction_run.experiment.reference_number)
            logger.warning('variables from stage 1: %s', str(variables))

        if not variables:
            logger.info('Finding variables from run number')
            # No experiment-specific variables, so let's look for variables set by run number.
            variables = self.show_variables_for_run(instrument_name, reduction_run.run_number)
            logger.warning('variables from stage 2: %s', str(variables))

        if not variables:
            logger.info('Using default variables')
            # No variables are set, so we'll use the defaults, and set them them while we're at it.
            variables = self.get_default_variables(instrument_name)
            logger.warning('variables from stage 3: %s', str(variables))
            logger.info('Setting the variables for the run')
            self.set_variables_for_runs(instrument_name, variables, reduction_run.run_number)

        logger.info('Saving the found variables')
        # Create run variables from these instrument variables, and return them.
        return VariableUtils().save_run_variables(variables, reduction_run)

    def set_variables_for_runs(self, instrument_name, variables, start_run=0, end_run=None):
        """
        Given a list of variables, we set them to be the variables used for subsequent runs in the
        given run range. If end_run is not supplied, these variables will be ongoing indefinitely.
        If start_run is not supplied, these variables will be set for all run numbers going
        backwards.
        """
        instrument = db.get_instrument(instrument_name)

        # Ensure that the variables we set will be the only ones used for the range given.
        model = db.start_database().variable_model
        applicable_variables = model.InstrumentVariable.objects \
            .filter(instrument_id=instrument.id) \
            .filter(start_run=start_run)

        final_variables = []
        if end_run:
            applicable_variables = applicable_variables.filter(start_run__lte=end_run)
            # pylint: disable=no-member
            after_variables = model.InstrumentVariable.objects \
                .filter(instrument_id=instrument.id) \
                .filter(start_run=end_run + 1) \
                .order_by('start_run')

            # pylint: disable=no-member
            previous_variables = model.InstrumentVariable.objects \
                .filter(instrument_id=instrument.id) \
                .filter(start_run__lt=start_run)

            if applicable_variables and not after_variables:
                # The last set of applicable variables extends outside our range.

                # Find the last set.
                final_start = applicable_variables.order_by('-start_run').first().start_run
                final_variables = list(applicable_variables.filter(start_run=final_start))
                applicable_variables = applicable_variables.exclude(
                    start_run=final_start)  # Don't delete the final set.

            elif not applicable_variables and not after_variables and previous_variables:
                # There is a previous set that applies but doesn't start or end in the range.

                # Find the last set.
                final_start = previous_variables.order_by('-start_run').first().start_run
                # Set them to apply after our variables.
                # pylint: disable=expression-not-assigned,no-member
                final_variables = list(
                    previous_variables.filter(start_run=final_start))
                [VariableUtils().copy_variable(var).save() for var in
                 final_variables]  # Also copy them to apply before our variables.

            elif not applicable_variables and not after_variables and not previous_variables:
                # There are instrument defaults which apply after our range.
                final_variables = self.get_default_variables(instrument_name)

        # Delete all currently saved variables that apply to the range.
        map(lambda var: var.delete(), applicable_variables)

        # Modify the range of the final set to after the specified range, if there is one.
        for var in final_variables:
            var.start_run = end_run + 1
            db.save_record(var)

        # Then save the new ones.
        for var in variables:
            var.start_run = start_run
            db.save_record(var)

    def show_variables_for_experiment(self, instrument_name, experiment_reference):
        """
        Look for currently set variables for the experiment.
        If none are set, return an empty list (or QuerySet) anyway.
        """
        instrument = db.get_instrument(instrument_name)
        model = db.start_database().variable_model
        ins_vars = model.InstrumentVariable.objects \
            .filter(instrument_id=instrument.id) \
            .filter(experiment_reference=experiment_reference)
        self._update_variables(ins_vars)
        return [VariableUtils().copy_variable(ins_var) for ins_var in ins_vars]

    def _get_help_text(self, dictionary, key, instrument_name, reduce_script=None):
        """ Get variable help text. """
        if not dictionary or not key:
            return ""
        if not reduce_script:
            reduce_script = self._load_reduction_vars_script(instrument_name)
        if 'variable_help' in dir(reduce_script):
            if dictionary in reduce_script.variable_help:
                if key in reduce_script.variable_help[dictionary]:
                    return self._replace_special_chars(reduce_script.variable_help[dictionary][key])
        return ""

    @staticmethod
    def _replace_special_chars(help_text):
        """ Remove any special chars in the help text. """
        help_text = html.escape(help_text)  # Remove any HTML already in the help string
        help_text = help_text.replace('\n', '<br>').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;')
        return help_text
