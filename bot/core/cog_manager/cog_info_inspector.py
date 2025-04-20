import os
import re
from typing import List, TYPE_CHECKING
from dao.bot_setting_dao import bot_setting
from utils.converters import pascal_to_snake

if TYPE_CHECKING:
    from ..bot import Bot


COG_PATH = bot_setting.get_cog_dir_path()

class CogInfoInspector:
    '''檢查 cogs 的資訊'''

    def __init__(self, bot: 'Bot'):
        self.bot = bot

    
    def get_load_cogs(self) -> List[str]:
        '''獲取載入的 cogs'''
        load_cogs = []
        for cog in self.bot.cogs:
            cog = pascal_to_snake(cog)
            load_cogs.append(cog)
        load_cogs.sort()
        return load_cogs


    def get_unload_cogs(self) -> List[str]:
        '''獲取未載入的 cogs'''
        unload_cogs = []
        for filename in os.listdir(COG_PATH):
            if filename.endswith('.py') and filename[:-3] not in self.get_load_cogs():
                unload_cogs.append(filename[:-3])
        unload_cogs.sort()
        return unload_cogs


    def get_cog_doc(self, cog_name: str) -> str:
        '''獲取 cogs 說明資訊'''
        with open(f"{COG_PATH}/{cog_name}" + ".py", "r", encoding="UTF-8") as f:
            code = f.read()
        cog_info = re.search(r'__doc__.?=.?"(.+)"', code)

        return cog_info.group(1) if cog_info else ""