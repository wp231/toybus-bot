import discord
from typing import TYPE_CHECKING, List
from discord import app_commands
from dao.notification_dao import notification_dao
from ui.notification_view import NotificationView
from core.cog_helpers.cog_extension import CogExtension
from core.cog_helpers.command_checker import CommandChecker

if TYPE_CHECKING:
    from core.bot import Bot


async def get_user_notifications(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice]:
    '''取得使用者的通知列表'''
    choices: List[app_commands.Choice] = []

    notifications = notification_dao.get_user_notifications(interaction.user.id)
    for notification in notifications:
        if current.lower() in notification.lower():
            choices.append(app_commands.Choice(name=notification, value=notification))

    return choices

class Notification(CogExtension):
    __doc__ = "通知功能"
    check = CommandChecker()

    @check.roleauth
    @app_commands.command(name="add_notification", description="添加新的通知訊息")
    @app_commands.describe(message="需要通知的訊息")
    async def add_notification(self, interaction: discord.Interaction, message: str):
        user_id = interaction.user.id
        
        notifications =  notification_dao.get_user_notifications(interaction.user.id)
        if message in notifications:
            await interaction.response.send_message("已經有這個通知了", ephemeral=True)
            return

        await interaction.response.send_message("# 新增通知", view=NotificationView(message, user_id), ephemeral=True)

    @check.roleauth
    @app_commands.command(name="edit_notification", description="編輯通知訊息")
    @app_commands.autocomplete(message=get_user_notifications)
    async def edit_notification(self, interaction: discord.Interaction, message: str):
        user_id = interaction.user.id
        
        notifications = notification_dao.get_user_notifications(interaction.user.id)
        if message not in notifications:
            await interaction.response.send_message("沒有這個通知", ephemeral=True)
            return
        
        await interaction.response.send_message("# 編輯通知", view=NotificationView(message, user_id), ephemeral=True)

    @check.roleauth
    @app_commands.command(name="del_notification", description="刪除通知訊息")
    @app_commands.autocomplete(message=get_user_notifications)
    async def del_notification(self, interaction: discord.Interaction, message: str):
        user_id = interaction.user.id

        notifications = notification_dao.get_user_notifications(interaction.user.id)
        if message not in notifications:
            await interaction.response.send_message("沒有這個通知", ephemeral=True)
            return

        notification_dao.del_user_notification(interaction.user.id, message)
        self.bot.notification_manager.del_notification_job(user_id, message)
        await interaction.response.send_message("已經刪除這個通知", ephemeral=True)


async def setup(bot: 'Bot'):
    await bot.add_cog(Notification(bot))
