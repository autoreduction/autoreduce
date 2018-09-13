"""
Definition of Variable classes used for the WebApp model
"""
from django.db import models
from reduction_viewer.models import Instrument, ReductionRun


class Variable(models.Model):
    """
    Generic model class that should be treated as abstract
    """
    name = models.CharField(max_length=50, blank=False)
    value = models.CharField(max_length=300, blank=False)
    type = models.CharField(max_length=50, blank=False)
    is_advanced = models.BooleanField(default=False)
    help_text = models.TextField(blank=True, null=True, default='')

    def __unicode__(self):
        """ :return: GEM - variable-name=variable-value """
        # pylint:disable=no-member
        return u'%s - %s=%s' % (self.instrument.name, self.name, self.value)

    def sanitized_name(self):
        """
        Returns a HTMl-friendly name that can be used as element IDs or form input names
        """
        # pylint:disable=no-member
        return self.name.replace(' ', '-')


class InstrumentVariable(Variable):
    """
    Instrument specific variable class
    """
    instrument = models.ForeignKey(Instrument)
    experiment_reference = models.IntegerField(blank=True, null=True)
    start_run = models.IntegerField(blank=True, null=True)
    tracks_script = models.BooleanField(default=False)


class RunVariable(Variable):
    """
    Run specific Variable class
    """
    reduction_run = models.ForeignKey(ReductionRun, related_name="run_variables")
