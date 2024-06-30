import sys
import discord
import subprocess
from run import Bot
from discord import app_commands
from utils.log_manager import bot_log
from dao.bot_setting_dao import bot_setting
from core.cog_utils import CogExtension, CommandChecker


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
    @app_commands.command(name="load_conf", description="載入機器人設定")
    async def load_conf(self, interaction: discord.Interaction):
        user = interaction.user.name
        user_id = interaction.user.id

        bot_setting.read()

        await interaction.response.send_message("載入機器人設定")
        bot_log.info_cmd_load_conf(user, user_id)


async def setup(bot: Bot):
    await bot.add_cog(Admin(bot))
