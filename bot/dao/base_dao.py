import os
import json

INDENT = 2


class BaseDAO:
    def __init__(self, file_path: str, format: dict | None = None, indent: int = INDENT) -> None:
        '''創建 json 檔案，有非 json 格式內容則不處理'''
        self.jdata: dict = {}
        self.file_path = file_path
        self.indent = indent

        # 檢查檔案存在
        if not os.path.exists(file_path):
            self.write()

        # 初始化空，避免讀取錯誤
        with open(file_path, 'r', encoding='utf8') as f:
            f_content = f.read().strip()
        if not f_content:
            self.write()

        # 檢查格式
        if not self.read():
            raise ValueError(f'File "{file_path}" is not json format.')

        # 無須初始化格式
        if format is None:
            return

        # 全空
        if not self.jdata:
            self.jdata = format
            self.write()
            return

        # 部分缺失
        for key in format:
            if self.jdata.get(key) is None:
                self.jdata[key] = format[key]
        self.write()

    def write(self):
        '''寫入檔案'''
        with open(self.file_path, 'w', encoding='utf8') as jfile:
            json.dump(self.jdata, jfile, indent=self.indent)

    def read(self) -> bool:
        '''讀取檔案'''
        try:
            with open(self.file_path, 'r', encoding='utf8') as jfile:
                self.jdata = json.load(jfile)
                return True
        except:
            return False
