import os
import unittest
from bot.core.log_viewer import LogPageViewer

TMP_DIR = "test_log_viewer_dir"


class TestLogViewer(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR)

    def tearDown(self):
        if os.path.exists(TMP_DIR):
            for file in os.listdir(TMP_DIR):
                os.remove(os.path.join(TMP_DIR, file))
            os.rmdir(TMP_DIR)

    def create_file(self, file_name, content):
        with open(file_name, "w") as f:
            f.write(content)

    def delete_file(self, file_name):
        os.remove(file_name)

    def test_split_string_by_char_limit(self):

        test_datas = [[
            "", 10, [""]
        ], [
            "234567890\n234567890\n234567890\n", 10,
            ["234567890", "234567890", "234567890"]
        ], [
            "234567890\n234567890\n234567890", 10,
            ["234567890", "234567890", "234567890"]
        ], [
            "234567890123456\n234590\n2345670", 10,
            ["23456", "7890123456", "234590", "2345670"]
        ], [
            "1234567890\n012\n3456\n23456\n7890\n2345\n670", 10,
            ["1234567890", "012\n3456", "23456\n7890", "2345\n670"]
        ], [
            "1234567890\n1234567890\n1234567890\n", 10,
            ["1234567890", "1234567890", "1234567890"]
        ], [
            "123456789012345678901234567890", 10,
            ["1234567890", "1234567890", "1234567890"]
        ], [
            "12345678901234567890\n1234567890", 10,
            ["1234567890", "1234567890", "1234567890"]
        ], [
            "123456  789  01234  56789012   34567890", 10,
            ["123456", "789  01234", "  56789012", "  34567890"]
        ], [
            "   3456   ", 10, ["3456"]
        ]]

        for data in test_datas:
            tmp_file = os.path.join(TMP_DIR, "test_file")
            self.create_file(tmp_file, data[0])

            log_viewer = LogPageViewer(tmp_file, data[1])
            self.assertEqual(data[2], log_viewer._pages)

            self.delete_file(tmp_file)
