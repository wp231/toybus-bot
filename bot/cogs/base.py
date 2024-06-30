import discord
from typing import Dict, List
from discord import app_commands
from run import Bot, admin_commands
from dao.bot_setting_dao import bot_setting
from utils.converters import pascal_to_space
from core.cog_utils import CogExtension, CommandChecker

check = CommandChecker()


class Base(CogExtension):
    __doc__ = "基本指令"

    def check_roles(self, interaction: discord.Interaction, roles: List[int]) -> bool:
        '''檢查使用者是否屬於指定身份組'''
        if isinstance(interaction.user, discord.Member) and \
                any(role.id in roles for role in interaction.user.roles):
            return True
        return False

    def check_permissions(self, interaction: discord.Interaction, perms: Dict) -> bool:
        '''檢查使用者是否有指定權限'''
        permissions = interaction.permissions
        missing = [perm for perm, value in perms.items(
        ) if getattr(permissions, perm) != value]

        if not missing:
            return True
        return False

    def check_command_roleauth(self, interaction: discord.Interaction, command: app_commands.Command):
        '''檢查使用者是否符合使用命令的權限'''
        has_role = True
        roles = command.extras.get("roles")
        if roles:
            has_role = self.check_roles(interaction, roles)

        has_perm = True
        perms = command.extras.get("permissions")
        if perms:
            has_perm = self.check_permissions(interaction, perms)

        return has_role and has_perm

    @check.roleauth
    @app_commands.command(name='help', description='查看指令幫助說明')
    async def help(self, interaction: discord.Interaction):
        msg = ""

        # 獲取管理指令
        for command in admin_commands:
            if isinstance(command, app_commands.Command) and \
                    self.check_command_roleauth(interaction, command):
                msg = msg + "\t" + command.name + ': ' + command.description + '\n'
        if msg:
            msg = "Admin commands:\n" + msg

        cogs = sorted(self.bot.cogs.values(),
                      key=lambda x: x.__class__.__name__)
        for cog in cogs:
            cog_name: str = cog.__class__.__name__

            # 判斷用戶與 cog 的同步伺服器
            cog_guilds = bot_setting.get_cog_guilds(cog_name)
            if cog_guilds and interaction.guild_id not in cog_guilds:
                continue

            # 獲取 cog 描述訊息
            cog_name = pascal_to_space(cog_name)
            cog_name = cog_name + ": " + getattr(cog, "__doc__", "")
            msg = msg + cog_name

            # 顯示 cog 中的所有指令和描述
            old_msg = msg
            for command in cog.get_app_commands():
                if isinstance(command, app_commands.Command) and \
                        self.check_command_roleauth(interaction, command):
                    msg = msg + '\n\t' + command.name + ': ' + command.description
            if msg == old_msg:
                msg = msg.replace(cog_name, "")

            msg = msg + '\n'

        if not msg:
            await interaction.response.send_message(f"無可用指令", ephemeral=True)
            return

        await interaction.response.send_message(f"當前可用指令幫助說明：```\n{msg}```", ephemeral=True)

    @check.roleauth
    @app_commands.command(name='pong', description='碰!!!')
    async def pong(self, interaction: discord.Interaction):
        delay_time = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong!!!  {delay_time} ms")

    @check.roleauth
    @app_commands.command(name='say', description='使用機器人說')
    async def say(self, interaction: discord.Interaction, string: str):
        try:
            await interaction.channel.send(string)
            await interaction.response.send_message("發送成功", ephemeral=True)
        except:
            await interaction.response.send_message("發送失敗", ephemeral=True)


async def setup(bot: Bot):
    await bot.add_cog(Base(bot))
