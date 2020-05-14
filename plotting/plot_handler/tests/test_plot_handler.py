# ############################################################################### #
# Autoreduction Repository : https://github.com/ISISScientificComputing/autoreduce
#
# Copyright &copy; 2020 ISIS Rutherford Appleton Laboratory UKRI
# SPDX - License - Identifier: GPL-3.0-or-later
# ############################################################################### #
"""
Unit tests for plot_handler
"""

# Core Dependencies
import unittest

from mock import patch, Mock

# Internal Dependencies
from plotting.plot_handler.plot_handler import DjangoDashApp


class TestDjangoDashApp(unittest.TestCase):
    """Unit tests for DjangoDashApp class in plot handler"""
    @patch("plotting.prepare_data.PrepareData.prepare_data")
    @patch("plotting.plot_meta_language.interpreter.Interpreter.interpret")
    @patch("plotting.plot_factory.plot_factory.PlotFactory")
    @patch("plotting.plot_factory.dashapp.DjangoDash")
    def test_get_dashapp(self, mock_dashapp, mock_plot_factory, mock_interpreter, mock_prepare):
        """
        Test:get_dashapp() is called returning an instance of DjangoDash DashApp object
        When: called with within DjangoDashApp() during class initialisation
        """
        mock_dash_obj = Mock()
        mock_dashapp.return_value = mock_dash_obj

        DjangoDashApp('plotting/multi_spectra_data_file.csv',
                      'plotting/plot_meta_language/plot_types/example.yaml',
                      "Instrument_Run_Number")

        mock_dashapp.assert_called_once()
