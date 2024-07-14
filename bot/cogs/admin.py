import os
import sys
import discord
import subprocess
from run import Bot
from typing import List
from discord import app_commands
from utils.log_manager import bot_log
from core.log_viewer import LogPageViewer
from dao.bot_setting_dao import bot_setting
from ui.log_viewer_view import LogViewerView
from core.cog_utils import CogExtension, CommandChecker


async def get_log_filenames(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice]:
    '''取得日誌檔案名稱列表'''
    log_dir_path = bot_setting.get_log_dir_path()
    filenames = os.listdir(log_dir_path)
    choices = [
        app_commands.Choice(name=filename, value=filename)
        for filename in filenames
    ]
    return choices


class Admin(CogExtension):
    __doc__ = "管理員指令"
    check = CommandChecker()

    @check.roleauth
    @app_commands.command(name="stop_bot", description="關閉機器人")
    async def stop_bot(self, interaction: discord.Interaction):
        user = interaction.user.name
        user_id = interaction.user.id

        await interaction.response.send_message("Bot is going to stop")
        bot_log.info_cmd_stop_bot(user, user_id)

        subprocess.Popen(
            [sys.executable, "main.py", "stop"],
            stdout=sys.stdout,
            stderr=sys.stderr
        )

    @check.roleauth
    @app_commands.command(name="restart_bot", description="重啟機器人")
    async def restart_bot(self, interaction: discord.Interaction):
        user = interaction.user.name
        user_id = interaction.user.id

        await interaction.response.send_message("Bot is going to restart")
        bot_log.info_cmd_restart_bot(user, user_id)

        subprocess.Popen(
            [sys.executable, "main.py", "restart"],
            stdout=sys.stdout,
            stderr=sys.stderr
        )

    @check.roleauth
    @app_commands.command(name="update_bot", description="更新機器人")
    async def update_bot(self, interaction: discord.Interaction):
        user = interaction.user.name
        user_id = interaction.user.id

        await interaction.response.send_message("Bot is going to update")
        bot_log.info_cmd_update_bot(user, user_id)

        subprocess.Popen(
            [sys.executable, "main.py", "update"],
            stdout=sys.stdout,
            stderr=sys.stderr
        )

    @check.roleauth
    @app_commands.command(name="load_conf", description="載入機器人設定")
    async def load_conf(self, interaction: discord.Interaction):
        user = interaction.user.name
        user_id = interaction.user.id

        bot_setting.read()

        await interaction.response.send_message("載入機器人設定")
        bot_log.info_cmd_load_conf(user, user_id)

    @check.roleauth
    @app_commands.command(name="log_viewer", description="日誌檢視器")
    @app_commands.autocomplete(filename=get_log_filenames)
    async def log_viewer(self, interaction: discord.Interaction, filename: str):
        log_dir_path = bot_setting.get_log_dir_path()
        log_file_path = os.path.join(log_dir_path, filename)

        log_page_viewer = LogPageViewer(log_file_path, 1990)
        view = LogViewerView(log_page_viewer)
        content = f"```js\n{log_page_viewer.get_page_content()}\n```"

        await interaction.response.send_message(content, view=view)


async def setup(bot: Bot):
    await bot.add_cog(Admin(bot))
