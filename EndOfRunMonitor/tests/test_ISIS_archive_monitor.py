"""
Unit tests and associated helpers to exercise the ISIS Archive Checker
"""
import unittest

from EndOfRunMonitor.database_client import ReductionRun
from EndOfRunMonitor.ISIS_archive_monitor import ArchiveMonitor
from EndOfRunMonitor.tests.data_archive_creator import DataArchiveCreator

from ..settings import INST_PATH


# List of variables to create a valid path and expected result _find_path_to_current_cycle
# [[start_year, end_year, current_cycle, expected_result], ...]
VALID_PATHS = [[0, 9, 3, 'cycle_09_3'],
               [1, 2, 5, 'cycle_02_5'],
               [10, 14, 1, 'cycle_14_1']]

# List of data to add to a directory and expected result from _find_most_recent_run
FILES_TO_TEST = [['TEST01.raw', 'TEST02.raw', 'TEST03.raw', 'TEST03.raw'],  # .raw
                 ['TEST01.RAW', 'TEST02.RAW', 'TEST03.RAW', 'TEST03.RAW'],  # .RAW
                 ['TEST01.raw', 'TEST02.RAW', 'TEST03.raw', 'TEST03.raw'],  # .raw/.RAW
                 ['TEST01.raw', 'TEST03.raw', 'TEST03.log', 'TEST03.raw'],  # .log file
                 ['TEST01.txt', 'TEST02.log', 'TEST01.out', None],  # no .raw
                 [None]]  # Empty file

# List of valid instruments
INST = ['TEST', 'WISH', 'GEM']


class TestISISArchiveChecker(unittest.TestCase):
    """
    Contains test cases for the ArchiveMonitor
    """

    def setUp(self):
        self.data_archive_creator = DataArchiveCreator('GEM')

    def tearDown(self):
        del self.data_archive_creator

    # ======================= init ======================== #

    def test_valid_init(self):
        monitor = ArchiveMonitor('GEM')
        self.assertIsInstance(monitor, ArchiveMonitor)
        self.assertEqual((INST_PATH.format('GEM')), monitor.instrument_path)

    def test_init_db_connection(self):
        monitor = ArchiveMonitor('GEM')
        self.assertIsNotNone(monitor.database_session)
        self.assertIsNotNone(monitor.database_session.query(ReductionRun).first())

    def test_init_with_invalid_inst(self):
        self.assertRaises(RuntimeError, ArchiveMonitor, 'not-instrument')

    def test_init_case_insensitive(self):
        self.assertIsNotNone(ArchiveMonitor('PoLaRiS'))

    def test_init_logging(self):
        _ = ArchiveMonitor('GEM')
        self.assertTrue('Starting new Archive Monitor for instrument: GEM'
                        in _get_last_line_in_log())

    # ============== get_most_recent_in_archive ============== #

    def test_valid_get_most_recent_in_archive(self):
        self.data_archive_creator.make_data_archive(VALID_PATHS[2][0], VALID_PATHS[2][1], VALID_PATHS[2][2])
        self.data_archive_creator.add_files_to_most_recent_cycle(FILES_TO_TEST[0])
        monitor = ArchiveMonitor('GEM')
        self.assertEqual(monitor.get_most_recent_in_archive(), 'TEST03.raw')
        self.data_archive_creator.remove_data_archive()

    # ============ get_most_recent_in_database =============== #

    def test_valid_get_most_recent_in_database(self):
        expected_runs = ['TEST1', 'WISH2', 'GEM3']
        for index, instrument in enumerate(INST):
            monitor = ArchiveMonitor(instrument)
            self.assertEqual(monitor.get_most_recent_run_in_database(),
                             expected_runs[index])

    # ========== compare_archive_and_database ================ #

    def test_valid_compare_archive_and_database(self):
        # overwrite data_archive
        self.data_archive_creator = DataArchiveCreator('GEM')
        self.data_archive_creator.make_data_archive(VALID_PATHS[2][0],
                                                    VALID_PATHS[2][1],
                                                    VALID_PATHS[2][2])
        self.data_archive_creator.add_files_to_most_recent_cycle(['GEM1.raw',
                                                                  'GEM2.raw',
                                                                  'GEM3.raw'])
        monitor = ArchiveMonitor('GEM')
        self.assertTrue(monitor.compare_most_recent_to_reduction_db())
        self.data_archive_creator.remove_data_archive()

    # ============== restart_reduction_run =================== #

    def test_valid_restart_reduction_run(self):
        raise RuntimeError('Unimplemented test')


class TestArchiveMonitorHelpers(unittest.TestCase):
    """
    Contains test cases for ArchiveMonitor helper functions
    The cases in here are for static members of the class
    """

    def setUp(self):
        self.data_archive_creator = DataArchiveCreator('GEM')

    # ========== find_path_to_current_cycle_in_archive ========= #

    def test_valid_find_path_to_current_cycle(self):
        """
        Test find_path_to_current_cycle_in_archive give the expected output
         given the input of VALID_PATHS
        """
        for item in VALID_PATHS:
            self.data_archive_creator.make_data_archive(item[0], item[1], item[2])
            actual = ArchiveMonitor._find_path_to_current_cycle_in_archive(
                self.data_archive_creator.get_data_archive_dir())
            self.assertEqual(item[3], actual)
            self.data_archive_creator.remove_data_archive()

    # ============= find_most_recent_run_in_archive ============ #

    def test_valid_find_most_recent_run(self):
        """
        Test that find_most_recent_run produces the expected output
        given the input of FILES_TO_TEST
        """
        self.data_archive_creator.make_data_archive(VALID_PATHS[2][0],
                                                    VALID_PATHS[2][1],
                                                    VALID_PATHS[2][2])
        for test_files in FILES_TO_TEST:
            self.data_archive_creator.add_files_to_most_recent_cycle(test_files[:-1])
            actual = ArchiveMonitor._find_most_recent_run_in_archive(
                self.data_archive_creator.get_path_to_most_recent_cycle())
            self.assertEqual(test_files[-1], actual)
            self.data_archive_creator.remove_files_from_most_recent_cycle()
        self.data_archive_creator.remove_data_archive()


# =========== Test helpers ============== #
def _get_last_line_in_log():
    """
    Reads the log file and returns the most recent input
    :return: String of the most recent log
    """
    file_handle = open('archive_monitor.log', "r")
    line_list = file_handle.readlines()
    file_handle.close()
    return line_list[-1]
