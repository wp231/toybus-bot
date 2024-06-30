import os
import unittest
from bot.utils.utils import get_config_file_path

TMP_CONFIG_DIR = "test_get_config_file_path"


class TestUtils(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(TMP_CONFIG_DIR):
            os.makedirs(TMP_CONFIG_DIR)

    def tearDown(self):
        if os.path.exists(TMP_CONFIG_DIR):
            for file in os.listdir(TMP_CONFIG_DIR):
                os.remove(os.path.join(TMP_CONFIG_DIR, file))
            os.rmdir(TMP_CONFIG_DIR)

    def test_get_config_file_path(self):

        # Test case 1: File with no priority suffix
        file_path = os.path.join(TMP_CONFIG_DIR, "config.ini")
        expected_output = os.path.join(TMP_CONFIG_DIR, "config.ini")
        self.assertEqual(get_config_file_path(file_path), expected_output)

        # Test case 2: File with priority suffix "dev"
        file_path = os.path.join(TMP_CONFIG_DIR, "config.ini")
        expected_output = os.path.join(
            TMP_CONFIG_DIR, "config_dev.ini")
        with open(expected_output, "w") as f:
            f.write("Test")
        self.assertEqual(get_config_file_path(file_path), expected_output)
        os.remove(expected_output)

        # Test case 3: File with priority suffix "development"
        file_path = os.path.join(TMP_CONFIG_DIR, "config.ini")
        expected_output = os.path.join(
            TMP_CONFIG_DIR, "config_development.ini")
        with open(expected_output, "w") as f:
            f.write("Test")
        self.assertEqual(get_config_file_path(file_path), expected_output)
        os.remove(expected_output)

        # Test case 4: File with priority suffix "prod"
        file_path = os.path.join(TMP_CONFIG_DIR, "config.ini")
        expected_output = os.path.join(
            TMP_CONFIG_DIR, "config_prod.ini")
        with open(expected_output, "w") as f:
            f.write("Test")
        self.assertEqual(get_config_file_path(file_path), expected_output)
        os.remove(expected_output)

        # Test case 5: File with priority suffix "production"
        file_path = os.path.join(TMP_CONFIG_DIR, "config.ini")
        expected_output = os.path.join(
            TMP_CONFIG_DIR, "config_production.ini")
        with open(expected_output, "w") as f:
            f.write("Test")
        self.assertEqual(get_config_file_path(file_path), expected_output)
        os.remove(expected_output)
