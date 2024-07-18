import os
from dao.base_dao import BaseDAO
from typing import List, Dict
from utils.utils import get_config_file_path
from utils.converters import pascal_to_snake

BOT_SETTING_FILE_PATH = get_config_file_path("./data/bot_setting.json")

bot_setting_config_format = {
    "log_dir_path": "./log",
    "admin_guild_ids": [],
    "admin_role_ids": [],
    "cog_auth": {}
}


class BotSettingDAO(BaseDAO):
    def __init__(self, file_path: str) -> None:
        super().__init__(file_path, bot_setting_config_format)

    def get_log_dir_path(self) -> str:
        '''獲取日誌文件的目錄'''
        path = os.path.normpath(self.jdata["log_dir_path"])
        return path

    def get_admin_guilds(self) -> List[int]:
        '''獲取可使用管理命令的伺服器'''
        return self.jdata["admin_guild_ids"]

    def get_admin_roles(self) -> List[int]:
        '''獲取可使用管理命令的身份組'''
        return self.jdata["admin_role_ids"]

    @staticmethod
    def __normalize_cog_name(func):
        '''規範 cog 的名稱'''

        def wrapper(self, cog_name: str, *args, **kwargs):
            if not cog_name.islower() and '_' not in cog_name:
                cog_name = pascal_to_snake(cog_name)
            return func(self, cog_name, *args, **kwargs)
        return wrapper

    @__normalize_cog_name
    def create_cog(self, cog_name: str) -> None:
        '''創建 cog 權限位'''
        if cog_name not in self.jdata["cog_auth"]:
            self.jdata["cog_auth"][cog_name] = {}
            self.jdata["cog_auth"][cog_name]["guilds"] = []
            self.jdata["cog_auth"][cog_name]["roles"] = []
            self.jdata["cog_auth"][cog_name]["permissions"] = {}
            self.jdata["cog_auth"][cog_name]["commands"] = {}
            self.write()

    @__normalize_cog_name
    def get_cog_guilds(self, cog_name: str) -> List[int]:
        '''獲取可使用該 cog 的伺服器'''
        try:
            return self.jdata["cog_auth"][cog_name]["guilds"]
        except:
            return []

    @__normalize_cog_name
    def get_cog_roles(self, cog_name: str) -> List[int]:
        '''獲取可使用該 cog 的身份組'''
        try:
            return self.jdata["cog_auth"][cog_name]["roles"]
        except:
            return []

    @__normalize_cog_name
    def get_cog_permissions(self, cog_name: str) -> Dict:
        '''獲取可使用該 cog 的權限'''
        try:
            return self.jdata["cog_auth"][cog_name]["permissions"]
        except:
            return {}

    @__normalize_cog_name
    def __create_cog_command_roles(self, cog_name: str, command: str):
        '''創建 cog 中 command 身份組位'''
        if command not in self.jdata["cog_auth"][cog_name]["commands"]:
            self.jdata["cog_auth"][cog_name]["commands"][command] = {}

        self.jdata["cog_auth"][cog_name]["commands"][command]["roles"] = []
        self.write()

    @__normalize_cog_name
    def get_cog_command_roles(self, cog_name: str, command: str) -> List[int]:
        '''獲取可使用該 cog 中 command 的身份組'''
        try:
            return self.jdata["cog_auth"][cog_name]["commands"][command]["roles"]
        except:
            self.__create_cog_command_roles(cog_name, command)
            return []

    @__normalize_cog_name
    def __create_cog_command_permissions(self, cog_name: str, command: str):
        '''創建 cog 中 command 權限位'''
        if command not in self.jdata["cog_auth"][cog_name]["commands"]:
            self.jdata["cog_auth"][cog_name]["commands"][command] = {}

        self.jdata["cog_auth"][cog_name]["commands"][command]["permissions"] = {}
        self.write()

    @__normalize_cog_name
    def get_cog_command_permissions(self, cog_name: str, command: str) -> Dict:
        '''獲取可使用該 cog 中 command 的權限'''
        try:
            return self.jdata["cog_auth"][cog_name]["commands"][command]["permissions"]
        except:
            self.__create_cog_command_permissions(cog_name, command)
            return {}


bot_setting = BotSettingDAO(BOT_SETTING_FILE_PATH)
