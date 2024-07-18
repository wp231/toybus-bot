import os
import unittest
from bot.dao.base_dao import BaseDAO

TMP_DIR = "test_base_dao_dir"


class TestBaseDAO(unittest.TestCase):
    def setUp(self):
        file_name = "test.json"
        self.format = {"test1": 1, "test2": [], "test3": {}}
        self.file_path = os.path.join(TMP_DIR, file_name)

        if not os.path.exists(TMP_DIR):
            os.makedirs(TMP_DIR)

    def tearDown(self):
        if os.path.exists(TMP_DIR):
            for file in os.listdir(TMP_DIR):
                os.remove(os.path.join(TMP_DIR, file))
            os.rmdir(TMP_DIR)

    def test_init_non_existing_file(self):
        '''測試初始化不存在的檔案'''
        base_dao = BaseDAO(self.file_path)
        self.assertTrue(os.path.exists(self.file_path))
        base_dao.read()
        self.assertEqual(base_dao.jdata, {})

        os.remove(self.file_path)

    def test_init_empty_file(self):
        '''測試初始化空檔案'''
        with open(self.file_path, "w") as f:
            pass

        base_dao = BaseDAO(self.file_path)
        base_dao.read()
        self.assertEqual(base_dao.jdata, {})

        os.remove(self.file_path)

    def test_init_empty_json(self):
        '''測試初始化空 json'''
        with open(self.file_path, "w") as f:
            f.write("{}")

        base_dao = BaseDAO(self.file_path)
        base_dao.read()
        self.assertEqual(base_dao.jdata, {})

        os.remove(self.file_path)

    def test_incorrect_format_json(self):
        '''測試初始化非 json 格式'''
        with open(self.file_path, "w") as f:
            f.write("Test")

        try:
            BaseDAO(self.file_path)
        except ValueError as e:
            self.assertEqual(
                str(e), f'File "{self.file_path}" is not json format.')
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "Test")

        os.remove(self.file_path)

    def test_incorrect_format_json_with_format(self):
        '''測試初始化非 json 格式且有 format'''
        with open(self.file_path, "w") as f:
            f.write("Test")

        try:
            BaseDAO(self.file_path, self.format)
        except ValueError as e:
            self.assertEqual(
                str(e), f'File "{self.file_path}" is not json format.')
        with open(self.file_path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "Test")

        os.remove(self.file_path)

    def test_non_existing_file_with_format(self):
        '''測試初始化不存在的檔案且有 format'''
        base_dao = BaseDAO(self.file_path, self.format)
        self.assertTrue(os.path.exists(self.file_path))
        base_dao.read()
        self.assertEqual(base_dao.jdata, self.format)

        os.remove(self.file_path)

    def test_empty_json_with_format(self):
        '''測試初始化空 json 且有 format'''
        with open(self.file_path, "w") as f:
            f.write("{}")

        base_dao = BaseDAO(self.file_path, self.format)
        base_dao.read()
        self.assertEqual(base_dao.jdata, self.format)

        os.remove(self.file_path)

    def test_missing_keys_json_with_format(self):
        '''測試初始化缺少 key 的 json 且有 format'''
        with open(self.file_path, "w") as f:
            f.write('{"test2": []}')

        base_dao = BaseDAO(self.file_path, self.format)
        base_dao.read()
        self.assertEqual(base_dao.jdata, self.format)

        os.remove(self.file_path)
