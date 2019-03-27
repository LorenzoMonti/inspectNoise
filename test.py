import unittest
import os
import subprocess
import sys
import ast
from utils import *
from config_manager import ConfigManager

class TestCli(unittest.TestCase):
    """
        Tests used to test command line interface.
        Tests are based on the execution of a new run-time generated python script
        that will use command line interface and print resulting dictionary with flags
        on a file.
    """
    def setUp(self):
        # Creates scripts for cli testing.
        create_run_script(".test_calibrate.py", ".test_calibrate.txt")
        create_run_script(".test_seconds.py", ".test_seconds.txt")
        create_run_script(".test_log.py", ".test_log.txt")
        create_run_script(".test_record.py", ".test_record.txt")

    def test_calibrate(self):
        """
            Test of calibrate flag.
        """
        res = subprocess.run([sys.executable, ".test_calibrate.py", "--calibrate"])
        with open(".test_calibrate.txt", "r") as f:
            kargs = ast.literal_eval(f.read())
        self.assertEqual(kargs['calibrate'], True)
        os.remove(".test_calibrate.txt")

    def test_seconds(self):
        """
            Test of seconds flag.
        """
        sec = 5
        res = subprocess.run([sys.executable, ".test_seconds.py", "--seconds", str(sec)])
        with open(".test_seconds.txt", "r") as f:
            kargs = ast.literal_eval(f.read())
        self.assertEqual(kargs['seconds'], sec)
        os.remove(".test_seconds.txt")

    def test_log(self):
        """
            Test of log flag.
        """
        log_file = ".log.log"
        res = subprocess.run([sys.executable, ".test_log.py", "--log", log_file])
        self.assertEqual(os.path.exists(log_file), True)
        os.remove(".test_log.txt")
        os.remove(log_file)

    def test_record(self):
        """
            Test of record flag.
        """
        record_file = ".record.wav"
        res = subprocess.run([sys.executable, ".test_record.py", "--record", record_file])
        self.assertEqual(os.path.exists(record_file), True)
        os.remove(".test_record.txt")
        os.remove(record_file)

    def tearDown(self):
        os.remove(".test_seconds.py")
        os.remove(".test_calibrate.py")
        os.remove(".test_log.py")
        os.remove(".test_record.py")

class TestConfig(unittest.TestCase):

    def test_setindex(self):
        """
            Test of setindex flag and correct update of configuration file.
        """
        index = 2
        res = subprocess.run([sys.executable, "inspect_noise.py", "--setindex", str(index)])
        cnf_manager = ConfigManager()
        self.assertEqual(int(cnf_manager.get_config_value("input_device_index")), index)

if __name__ == '__main__':
    unittest.main()
