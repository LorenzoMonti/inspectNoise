import unittest
import os
import subprocess
import sys
import ast
import noise_observer as no
from utils import *
from config_manager import ConfigManager
from threading import Thread

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

    def test_record(self):
        """
            Test of record flag.
        """
        record_file = "record.wav"
        res = subprocess.run([sys.executable, ".test_record.py", "--record", record_file])
        with open(".test_record.txt", "r") as f:
            kargs = ast.literal_eval(f.read())
        self.assertEqual(kargs['record'], record_file)
        os.remove(".test_record.txt")

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

    def tearDown(self):
        os.remove(".test_seconds.py")
        os.remove(".test_calibrate.py")
        os.remove(".test_log.py")
        os.remove(".test_record.py")

class TestConfig(unittest.TestCase):
    """
        Test of config file reading and writing of index.
    """
    def test_setindex(self):
        """
            Test of setindex flag and correct update of configuration file.
        """
        index = 0
        res = subprocess.run([sys.executable, "inspect_noise.py", "--setindex", str(index)])
        cnf_manager = ConfigManager()
        self.assertEqual(int(cnf_manager.get_config_value("input_device_index")), index)

    def test_check_default_config_params(self):
        """
            Test of correct setting of default params.
            Change this method before
        """
        default_frames = 2048
        default_format = 8
        default_channels = 2
        default_input_device_index = 0
        default_rate = 44100
        default_audio_seg_length = 0.5

        config = ConfigManager()

        self.assertEqual(int(config.get_config_value("input_device_index")), default_input_device_index)
        self.assertEqual(int(config.get_config_value("frames_per_buffer")), default_frames)
        self.assertEqual(int(config.get_config_value("channels")), default_channels)
        self.assertEqual(int(config.get_config_value("format")), default_format)
        self.assertEqual(int(config.get_config_value("rate")), default_rate)
        self.assertEqual(float(config.get_config_value("audio_segment_length")), default_audio_seg_length)

class NoiseObserver(unittest.TestCase):
    """
        Test noise observer main loop.
    """
    def setUp(self):
        # Creates scripts for cli testing.
        create_run_script(".test_monitoring.py", ".test_monitoring.txt")

    def test_monitoring(self):
        """
            Test if the monitoring starts.
        """
        # Create runnable script.
        # This script is used to create dictionary using cli.
        res = subprocess.run([sys.executable, ".test_monitoring.py", "--trashesoutput"])
        with open(".test_monitoring.txt", "r") as f:
            kargs = ast.literal_eval(f.read())

        # Passing cli as parameter.
        del kargs["calibrate"]
        del kargs["showindex"]
        del kargs["setindex"]

        # Used thread to start monitoring in separated flow.
        noise_obs = no.NoiseObserver(**kargs)
        thread = Thread(target=noise_obs.start_monitoring)
        thread.start()

        self.assertTrue(noise_obs.is_monitoring())
        noise_obs.stop_monitoring()
        thread.join() # Wait until thread terminate work
        self.assertFalse(noise_obs.is_monitoring())
        os.remove(".test_monitoring.txt")

    def tearDown(self):
        os.remove(".test_monitoring.py")

if __name__ == '__main__':
    unittest.main()
