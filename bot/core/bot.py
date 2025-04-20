import os
import discord
from discord import app_commands
from discord.ext import commands
from utils.log_manager import bot_log
from typing import List, Dict, Optional
from discord.ext.commands.cog import Cog
from dao.bot_setting_dao import bot_setting
from utils.converters import guild_ids_to_guilds, list_to_table
from .notification_manager import NotificationManager
from .cog_manager.load_cog_contral_commands import LoadCogContralCommands


COG_PATH = bot_setting.get_cog_dir_path()


class Bot(commands.Bot):

    def __init__(self, intents: discord.Intents) -> None:
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

        self.notification_manager = NotificationManager(self)
        self.cog_contral_commands: List[app_commands.Command] = []


    async def add_cog(self, cog: Cog):
        cog_name = cog.__cog_name__
        guild_ids = bot_setting.get_cog_guilds(cog_name)

        if guild_ids:
            guilds = guild_ids_to_guilds(guild_ids)
            await super().add_cog(cog, guilds=guilds)
        else:
            await super().add_cog(cog)

    
    async def sync_to_server(self, guild_id: Optional[int] = None) -> Optional[Dict]:
        '''同步 Slash commands 到伺服器

        Parameters
        -----------
        guild_id: int
            同步到指定伺服器的 guild_id
            未設定時全部同步

        Returns
        --------
            None 代表同步成功
            返回同步失敗的 {伺服器 ID: 錯誤訊息}
            返回 ID 為 {None: ...} 代表同步全局命令失敗
        '''

        # 獲取伺服器 guild
        guilds: List[Optional[discord.Guild]]
        if guild_id is None:
            guilds = [None]
            guilds.extend(self.guilds)
        else:
            guilds = [await self.fetch_guild(guild_id)]

        error_sync_guilds = {}
        # 同步到所有伺服器
        for guild in guilds:
            server_name = "Global" if guild is None else guild.name

            try:
                success_commands = await self.tree.sync(guild=guild)
            except Exception as e:
                error_sync_guilds[guild.id if guild else None] = str(e)
                bot_log.error_sync_command(server_name, e)
                continue

            table_data = [
                [
                    f"name: {command.name}",
                    f"guild: {command.guild}",
                    f"guild_id: {command.guild_id}"
                ]
                for command in success_commands
            ]
            table = list_to_table(table_data)
            bot_log.info_sync_command(server_name, len(success_commands), table)

        # 同步失敗的伺服器
        return None if error_sync_guilds == {} else error_sync_guilds


    async def setup_hook(self) -> None:

        # 載入預設命令
        LoadCogContralCommands(self)
            
        # 載入 cog 命令
        for filename in os.listdir(COG_PATH):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    bot_log.info_load_cog(filename[:-3])
                except Exception as e:
                    bot_log.error_load_cog(filename[:-3], e)


    async def on_ready(self) -> None:
        # await self.sync_to_server()
        await self.notification_manager.start()
        bot_log.info_start()


    async def close(self) -> None:
        bot_log.info_stop()

        if self.notification_manager:
            self.notification_manager.stop()

        await super().close()
        
    
    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        user = interaction.user.name
        user_id = interaction.user.id

        if interaction.command is not None and hasattr(interaction.command, 'name'):
            command = interaction.command.name
        else:
            command = "Unknown Command"

        if isinstance(error, app_commands.MissingAnyRole):
            await interaction.response.send_message("您的身份組無法使用此命令", ephemeral=True)
            bot_log.info_missing_any_role(command, user, user_id)
            return
        elif isinstance(error, app_commands.NoPrivateMessage):
            await interaction.response.send_message("無法在私訊中使用此命令", ephemeral=True)
            bot_log.info_no_private_message(command, user, user_id)
            return
        elif isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("您的權限不足無法使用此命令", ephemeral=True)
            bot_log.info_missing_permissions(command, user, user_id)
            return

        bot_log.error_cmd(command, user, user_id, error)