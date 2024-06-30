import os
import inspect
from run import Bot
from discord import app_commands
from discord.ext import commands
from dao.bot_setting_dao import bot_setting


class CogExtension(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot


class CommandChecker:
    def __init__(self) -> None:
        '''初始化 Cog 名稱，並創建 Cog 設定'''
        file_path = inspect.stack()[1].filename
        filename = os.path.basename(file_path)
        filename, _ = os.path.splitext(filename)
        self.cog_name = filename
        bot_setting.create_cog(self.cog_name)

    def roleauth(self, func: app_commands.Command):
        '''斜線指令添加權限判定'''
        # 身份組
        roles = bot_setting.get_cog_command_roles(
            self.cog_name, func.name)
        if not roles:
            roles = bot_setting.get_cog_roles(self.cog_name)
        if roles == [None]:
            # 拒絕所有身分組
            func = app_commands.checks.has_any_role()(func)
            func.extras["roles"] = [None]
        elif roles:
            # 添加身份組判定
            func = app_commands.checks.has_any_role(*roles)(func)
            func.extras["roles"] = roles

        # 權限
        permissions = bot_setting.get_cog_command_permissions(
            self.cog_name, func.name)
        if not permissions:
            permissions = bot_setting.get_cog_permissions(self.cog_name)
        if permissions:
            # 添加權限判定
            func = app_commands.checks.has_permissions(**permissions)(func)
            func.extras["permissions"] = permissions

        return func
