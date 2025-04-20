import re
import discord
from typing import TYPE_CHECKING
from discord import app_commands
from utils.log_manager import bot_log
from dao.bot_setting_dao import bot_setting
from utils.converters import guild_ids_to_guilds
from .cog_info_inspector import CogInfoInspector
from .sync_message_handler import SyncMessageHandler

if TYPE_CHECKING:
    from ..bot import Bot


ADMIN_ROLES = bot_setting.get_admin_roles()
ADMIN_GUILD_IDS = bot_setting.get_admin_guilds()
ADMIN_GUILDS = guild_ids_to_guilds(ADMIN_GUILD_IDS)


class LoadCogContralCommands():
    '''加載 Cog 控制指令'''

    @staticmethod
    def check_roleauth(func):
        '''設置指令伺服器和身份組'''
        if ADMIN_GUILDS:
            func = app_commands.guilds(*ADMIN_GUILDS)(func)
        if ADMIN_ROLES:
            func = app_commands.checks.has_any_role(*ADMIN_ROLES)(func)
        return func

    def __init__(self, bot: 'Bot'):
        self.bot = bot

        async def unload_cogs_to_options(interaction: discord.Interaction, current: str = ""):
            '''轉換未載入 cogs 為命令選項'''
            if ADMIN_ROLES and not (
                isinstance(interaction.user, discord.Member) and
                any(role.id in ADMIN_ROLES for role in interaction.user.roles)
            ):
                return []

            cog_info_inspector = CogInfoInspector(self.bot)
            unload_cogs = cog_info_inspector.get_unload_cogs()

            cogs = []
            for cog in unload_cogs:
                if current.lower() in cog.lower():
                    cogs.append(app_commands.Choice(name=cog, value=cog))
            return cogs


        async def load_cogs_to_options(interaction: discord.Interaction, current: str = ""):
            '''轉換載入 cogs 為命令選項'''
            if ADMIN_ROLES and not (
                isinstance(interaction.user, discord.Member) and
                any(role.id in ADMIN_ROLES for role in interaction.user.roles)
            ):
                return []

            cog_info_inspector = CogInfoInspector(self.bot)
            load_cogs = cog_info_inspector.get_load_cogs()

            cogs = []
            for cog in load_cogs:
                if current.lower() in cog.lower():
                    cogs.append(app_commands.Choice(name=cog, value=cog))
            return cogs


        async def get_bot_guilds_options(interaction: discord.Interaction, current: str):
            '''轉換伺服器為命令選項'''
            if ADMIN_ROLES and not (
                isinstance(interaction.user, discord.Member) and
                any(role.id in ADMIN_ROLES for role in interaction.user.roles)
            ):
                return []

            guilds = [app_commands.Choice(name="全部伺服器", value="全部伺服器")]
            for guild in self.bot.guilds:
                guild = f"{guild.name} ({str(guild.id)})"
                guilds.append(app_commands.Choice(name=guild, value=guild))
            return guilds


        @self.bot.tree.command(name='print_cogs', description='顯示所有可用的 Cogs')
        @LoadCogContralCommands.check_roleauth
        async def print_cogs(interaction: discord.Interaction):
            cog_info_inspector = CogInfoInspector(self.bot)

            def format_cogs(cogs):
                return "\n".join(
                    f"> 🔹 **{cog}: **\n> 　　{cog_info_inspector.get_cog_doc(cog) or '無描述'}"
                    for cog in cogs
                ) or "> 　**（無）**"

            loaded = format_cogs(cog_info_inspector.get_load_cogs())
            unloaded = format_cogs(cog_info_inspector.get_unload_cogs())

            embed = discord.Embed(
                title="**🛠️ 可用的模組**",
                color=discord.Color.blurple()
            )
            embed.add_field(name="已加載", value=loaded, inline=False)
            embed.add_field(name="未加載", value=unloaded, inline=False)

            await interaction.response.send_message(embed=embed)

        @self.bot.tree.command(name='load_cog', description='加載 cogs')
        @LoadCogContralCommands.check_roleauth
        @app_commands.autocomplete(cog_name=unload_cogs_to_options)
        @app_commands.choices(sync=[app_commands.Choice(name='True', value=1)])
        async def load_cog(interaction: discord.Interaction, cog_name: str, sync: int = 0):
            user = interaction.user.name
            user_id = interaction.user.id
            sync_message_handler = SyncMessageHandler(self.bot)

            try:
                await self.bot.load_extension(f"cogs.{cog_name}")
                msg = f"加載 {cog_name} 成功"
                await interaction.response.send_message(msg)
                bot_log.info_cmd_load_cog(cog_name, user, user_id)

                if sync:
                    await sync_message_handler.sync_message(interaction, msg)
            except Exception as e:
                bot_log.error_cmd_load_cog(cog_name, user, user_id, e)
                await interaction.response.send_message(f"加載 {cog_name} 失敗\n```{e}```")


        @self.bot.tree.command(name='reload_cog', description='重新加載 cogs')
        @LoadCogContralCommands.check_roleauth
        @app_commands.autocomplete(cog_name=load_cogs_to_options)
        @app_commands.choices(sync=[app_commands.Choice(name='True', value=1)])
        async def reload_cog(interaction: discord.Interaction, cog_name: str, sync: int = 0):
            user = interaction.user.name
            user_id = interaction.user.id
            sync_message_handler = SyncMessageHandler(self.bot)

            try:
                await self.bot.reload_extension(f"cogs.{cog_name}")
                msg = f"重新加載 {cog_name} 成功"
                await interaction.response.send_message(msg)
                bot_log.info_cmd_reload_cog(cog_name, user, user_id)

                if sync:
                    await sync_message_handler.sync_message(interaction, msg)
            except Exception as e:
                bot_log.error_cmd_reload_cog(cog_name, user, user_id, e)
                await interaction.response.send_message(f"重新加載 {cog_name} 失敗\n```{e}```")


        @self.bot.tree.command(name='unload_cog', description='卸載 cogs')
        @LoadCogContralCommands.check_roleauth
        @app_commands.autocomplete(cog_name=load_cogs_to_options)
        @app_commands.choices(sync=[app_commands.Choice(name='True', value=1)])
        async def unload_cog(interaction: discord.Interaction, cog_name: str, sync: int = 0):
            user = interaction.user.name
            user_id = interaction.user.id
            sync_message_handler = SyncMessageHandler(self.bot)

            try:
                await self.bot.unload_extension(f"cogs.{cog_name}")
                msg = f"卸載 {cog_name} 成功"
                await interaction.response.send_message(msg)
                bot_log.info_cmd_unload_cog(cog_name, user, user_id)

                if sync:
                    await sync_message_handler.sync_message(interaction, msg)
            except Exception as e:
                bot_log.error_cmd_unload_cog(cog_name, user, user_id, e)
                await interaction.response.send_message(f"卸載 {cog_name} 失敗\n```{e}```")


        @self.bot.tree.command(name="sync_commands", description="同步指令至伺服器")
        @LoadCogContralCommands.check_roleauth
        @app_commands.autocomplete(server=get_bot_guilds_options)
        async def sync_commands(interaction: discord.Interaction, server: str):
            user = interaction.user.name
            user_id = interaction.user.id
            sync_message_handler = SyncMessageHandler(self.bot)

            # 判定同步範圍
            if server == "全部伺服器":
                guild_id = None
            else:
                guild = re.search(r"\((\d*)\)$", server)
                guild_id = guild.group(1) if guild else ""
                server = server.replace(guild_id, "")[:-3]
                guild_id = int(guild_id)

            await interaction.response.send_message("開始同步")
            bot_log.info_cmd_sync_command(server, user, user_id)

            await sync_message_handler.sync_message(interaction, guild_id=guild_id)