"""
Utility functions for the reduction viewer models

Note: This file has a large number of pylint disable as it was un unit tested
at the time of fixing the pylint issues. Once unit tested properly, these disables
should be able to be removed. Many are relating to imports
"""
import datetime
import logging
import os
import sys
import time
import traceback

import django.core.exceptions
import django.http

from django.utils import timezone
from reduction_viewer.models import Instrument, Status, ReductionRun, DataLocation
from reduction_variables.models import RunVariable

sys.path.append(os.path.join("../", os.path.dirname(os.path.dirname(__file__))))
os.environ["DJANGO_SETTINGS_MODULE"] = "autoreduce_webapp.settings"
LOGGER = logging.getLogger('app')


class StatusUtils(object):
    """
    Utilities for the Status model
    """

    @staticmethod
    def _get_status(status_value):
        """
        Helper method that will try to get a status matching the given
        name or create one if it doesn't yet exist
        """
        # pylint:disable=no-member
        status = Status.objects.get(value=status_value)
        return status

    def get_error(self):
        """ :return: Error Status object """
        return self._get_status("Error")

    def get_completed(self):
        """ :return: Completed Status object """
        return self._get_status("Completed")

    def get_processing(self):
        """ :return: Processing Status object """
        return self._get_status("Processing")

    def get_queued(self):
        """ :return: Queued Status object """
        return self._get_status("Queued")

    def get_skipped(self):
        """ :return: Skipped Status object """
        return self._get_status("Skipped")


# pylint:disable=too-few-public-methods
class InstrumentUtils(object):
    """
    Utilities for the Instrument model
    """

    @staticmethod
    def get_instrument(instrument_name):
        """
        Helper method that will try to get an instrument matching the given name
        or create one if it doesn't yet exist
        """
        try:
            # pylint:disable=no-member
            instrument = Instrument.objects.get(name__iexact=instrument_name)
        except django.core.exceptions.ObjectDoesNotExist:
            raise django.http.Http404()
        return instrument


class ReductionRunUtils(object):
    """
    Utilities for the ReductionRun model
    """

    # pylint:disable=invalid-name
    @staticmethod
    def cancelRun(reduction_run):
        """
        Try to cancel the run given, or the run that was scheduled as the next retry of the run.
        When we cancel, we send a message to the backend queue processor, telling it to ignore
        this run if it arrives (likely through a delayed message through ActiveMQ's scheduler).
        We also set statuses and error messages. If we can't do any of the above, we set the
        variable (retry_run.cancel) that tells the frontend to not schedule another retry
        if the next run fails.
        """
        from reduction_variables.utils import MessagingUtils

        def set_cancelled(run):
            """
            Set a run status to cancelled and update related variables
            :param run: The run to update
            """
            run.message = "Run cancelled by user"
            run.status = StatusUtils().get_error()
            run.finished = timezone.now().replace(microsecond=0)
            run.retry_when = None
            run.save()

        # This is the queued run, send the message to queueProcessor to cancel it
        if reduction_run.status == StatusUtils().get_queued():
            MessagingUtils().send_cancel(reduction_run)
            set_cancelled(reduction_run)

        # otherwise this run has already failed, and we're looking at a scheduled rerun of it
        elif not reduction_run.retry_run:
            # we don't actually have a rerun,
            # so just ensure the retry time is set to "Never" (None)
            reduction_run.retry_when = None

        # This run is being queued to retry, so send the message
        # to queueProcessor to cancel it, and set it as cancelled
        elif reduction_run.retry_run.status == StatusUtils().get_queued():
            MessagingUtils().send_cancel(reduction_run.retry_run)
            set_cancelled(reduction_run.retry_run)

        # we have a run that's retrying, so just make sure it doesn't retry next time
        elif reduction_run.retry_run.status == StatusUtils().get_processing():
            reduction_run.cancel = True
            reduction_run.retry_run.cancel = True

        else:  # the retry run already completed, so do nothing
            pass

        # save the run states we modified
        reduction_run.save()
        if reduction_run.retry_run:
            reduction_run.retry_run.save()

    # pylint:disable=invalid-name,too-many-arguments,too-many-locals
    @staticmethod
    def createRetryRun(reduction_run, overwrite=None, script=None,
                       variables=None, delay=0, username=None, description=''):
        """
        Create a run ready for re-running based on the run provided.
        If variables (RunVariable) are provided, copy them and associate
        them with the new one, otherwise use the previous run's.
        If a script (as a string) is supplied then use it, otherwise use the previous run's.
        """
        from reduction_variables.utils import InstrumentVariablesUtils

        run_last_updated = reduction_run.last_updated

        if username == 'super':
            username = 1

        # find the previous run version, so we don't create a duplicate
        last_version = -1
        # pylint:disable=no-member
        previous_run = ReductionRun.objects.filter(experiment=reduction_run.experiment,
                                                   run_number=reduction_run.run_number) \
            .order_by("-run_version").first()

        last_version = previous_run.run_version

        # get the script to use:
        script_text = script if script is not None else reduction_run.script

        # create the run object and save it
        new_job = ReductionRun(instrument=reduction_run.instrument,
                               run_number=reduction_run.run_number,
                               run_name=description,
                               run_version=last_version + 1,
                               experiment=reduction_run.experiment,
                               started_by=username,
                               status=StatusUtils().get_queued(),
                               script=script_text,
                               overwrite=overwrite)

        # Check record is safe to save
        try:
            new_job.full_clean()
        # pylint:disable=catching-non-exception
        except django.core.exceptions as exception:
            LOGGER.error(traceback.format_exc())
            LOGGER.error(exception)
            raise

        # Attempt to save
        try:
            new_job.save()
        except ValueError as exception:
            # This usually indicates a F.K. constraint mismatch. Maybe we didn't get a record in?
            LOGGER.error(traceback.format_exc())
            LOGGER.error(exception)
            raise

        reduction_run.retry_run = new_job
        reduction_run.retry_when = timezone.now().replace(microsecond=0) + datetime.timedelta(
            seconds=delay if delay else 0)
        reduction_run.save()

        # pylint:disable=no-member
        ReductionRun.objects.filter(id=reduction_run.id).update(last_updated=run_last_updated)

        # copy the previous data locations
        # pylint:disable=no-member
        for data_location in reduction_run.data_location.all():
            new_data_location = DataLocation(file_path=data_location.file_path,
                                             reduction_run=new_job)
            new_data_location.save()
            new_job.data_location.add(new_data_location)

        if variables is not None:
            # associate the variables with the new run
            for var in variables:
                var.reduction_run = new_job
                var.save()
        else:
            # provide variables if they aren't already
            InstrumentVariablesUtils().create_variables_for_run(new_job)

        return new_job

    @staticmethod
    def get_script_and_arguments(reduction_run):
        """
        Fetch the reduction script from the given run and return it as a string,
        along with a dictionary of arguments.
        """
        from reduction_variables.utils import VariableUtils

        script = reduction_run.script

        # pylint:disable=no-member
        run_variables = RunVariable.objects.filter(reduction_run=reduction_run)
        standard_vars, advanced_vars = {}, {}
        for variables in run_variables:
            value = VariableUtils().convert_variable_to_type(variables.value, variables.type)
            if variables.is_advanced:
                advanced_vars[variables.name] = value
            else:
                standard_vars[variables.name] = value

        arguments = {'standard_vars': standard_vars, 'advanced_vars': advanced_vars}

        return script, arguments


class ScriptUtils(object):
    """
    Utilities for the scripts field
    """

    @staticmethod
    def get_reduce_scripts(scripts):
        """
        Returns a tuple of (reduction script, reduction vars script),
        each one a string of the contents of the script, given a list of script objects.
        """
        script_out = None
        script_vars_out = None
        for script in scripts:
            if script.file_name == "reduce.py":
                script_out = script
            elif script.file_name == "reduce_vars.py":
                script_vars_out = script
        return script_out, script_vars_out

    def get_cache_scripts_modified(self, scripts):
        """
        :returns: The last time the scripts in the database were
        modified (in seconds since epoch).
        """
        script_modified = None
        script_vars_modified = None

        for script in scripts:
            if script.file_name == "reduce.py":
                script_modified = self._convert_time_from_string(str(script.created))
            elif script.file_name == "reduce_vars.py":
                script_vars_modified = self._convert_time_from_string(str(script.created))
        return script_modified, script_vars_modified

    @staticmethod
    def _convert_time_from_string(string_time):
        """
        :return: time as integer for epoch
        """
        time_format = "%Y-%m-%d %H:%M:%S"
        string_time = string_time[:string_time.find('+')]
        return int(time.mktime(time.strptime(string_time, time_format)))
