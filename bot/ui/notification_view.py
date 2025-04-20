import discord
from typing import cast
from typing import List
from core.bot import Bot
from dao.notification_dao import notification_dao


def get_original_content(func):
    '''取得原始訊息內容'''

    async def wrapper(self, interaction: discord.Interaction):
        if isinstance(interaction.message, discord.Message):
            original_content = interaction.message.content
        else:
            original_content = ""

        result = await func(self, interaction, original_content)

        return result
    return wrapper


class DaysSelect(discord.ui.Select):
    '''星期選擇'''

    def __init__(self, values: List[str] | None = None):
        self.view: NotificationView
        self.days:List[discord.SelectOption] = [
            discord.SelectOption(label="星期一", value="1"),
            discord.SelectOption(label="星期二", value="2"),
            discord.SelectOption(label="星期三", value="3"),
            discord.SelectOption(label="星期四", value="4"),
            discord.SelectOption(label="星期五", value="5"),
            discord.SelectOption(label="星期六", value="6"),
            discord.SelectOption(label="星期日", value="7")
        ]

        # 載入預設選項
        if values is not None:
            for i in range(len(self.days)):
                if self.days[i].value in values:
                    self.days[i].default = True

        super().__init__(
            placeholder="星期",
            options=self.days,
            max_values=len(self.days)
        )

    @get_original_content
    async def callback(self, interaction: discord.Interaction, original_content: str):
        self.values.sort()

        # 取消舊選擇
        for i in range(len(self.options)):
            if self.options[i].value in self.values:
                self.options[i].default = True
            else:
                self.options[i].default = False

        self.view.days_select = self.values
        await interaction.response.edit_message(content=original_content, view=self.view)


class HoursSelect(discord.ui.Select):
    '''小時選擇'''

    def __init__(self, value: str | None = None):
        self.view: NotificationView
        self.hours: List[discord.SelectOption] = []
        self.old_select_value: str | None = None

        for i in range(0, 24):
            self.hours.append(
                discord.SelectOption(label=f"{i} 時", value=f"{i}")
            )

            # 載入預設選項
            if value is not None and int(value) == i:
                self.hours[i].default = True
                self.old_select_value = str(i)
    
        super().__init__(placeholder="時", options=self.hours)

    @get_original_content
    async def callback(self, interaction: discord.Interaction, original_content: str):
        self.values.sort()

        # 取消舊選擇
        if self.old_select_value is not None:
            int_value = int(self.old_select_value)
            self.options[int_value].default = False

        self.options[int(self.values[0])].default = True
        self.old_select_value = self.values[0]

        self.view.hours_select = self.values[0]
        await interaction.response.edit_message(content=original_content, view=self.view)


class MinutesSelect(discord.ui.Select):
    '''分鐘選擇'''

    def __init__(self, value: str | None = None):
        self.view: NotificationView
        self.minutes: List[discord.SelectOption] = []
        self.old_select_value: str | None = None

        for i in range(0, 60, 5):
            self.minutes.append(
                discord.SelectOption(label=f"{i} 分", value=f"{i}")
            )

            # 載入預設選項
            if value is not None and int(value) == i:
                self.minutes[i // 5].default = True
                self.old_select_value = str(i)

        super().__init__(placeholder="分", options=self.minutes)

    @get_original_content
    async def callback(self, interaction: discord.Interaction, original_content: str):
        self.values.sort()

        # 取消舊選擇
        if self.old_select_value is not None:
            int_value = int(self.old_select_value)
            self.options[int_value // 5].default = False

        self.options[int(self.values[0]) // 5].default = True
        self.old_select_value = self.values[0]

        self.view.minutes_select = self.values[0]
        await interaction.response.edit_message(content=original_content, view=self.view)


class SaveButton(discord.ui.Button):
    '''儲存按鈕'''

    def __init__(self):
        self.view: NotificationView
        super().__init__(label="儲存", style=discord.ButtonStyle.blurple)

    @get_original_content
    async def callback(self, interaction: discord.Interaction, original_content: str):
        if (
            self.view.hours_select is None or
            self.view.minutes_select is None or
            self.view.days_select is None or
            self.view.user_id != interaction.user.id
        ):
            return

        for each in self.view.children:
            each.disabled = True

        if interaction.channel is None:
            content = original_content + "\n您無法在此頻道新增通知"
            await interaction.response.edit_message(content=content, view=self.view)
            return

        notification_dao.add_weekly_notification(
            user_id=interaction.user.id,
            message=self.view.message,
            hour=int(self.view.hours_select),
            minute=int(self.view.minutes_select),
            weekdays=[int(day) for day in self.view.days_select],
            channel_id=interaction.channel.id
        )

        bot = cast(Bot, interaction.client)
        if self.view.need_edit:
            # 編輯通知
            bot.notification_manager.del_notification_job(
                self.view.user_id,
                self.view.message
            )
            bot.notification_manager.add_notification_job(
                self.view.user_id,
                self.view.message
            )
        else:
            # 新增通知
            bot.notification_manager.add_notification_job(
                self.view.user_id,
                self.view.message
            )

        content = original_content + "\n儲存成功"
        await interaction.response.edit_message(content=content, view=self.view)


class CancelButton(discord.ui.Button):
    '''取消按鈕'''

    def __init__(self):
        self.view: NotificationView
        super().__init__(label="取消", style=discord.ButtonStyle.gray)

    async def callback(self, interaction: discord.Interaction):
        if isinstance(interaction.message, discord.Message):
            await interaction.message.delete()


class NotificationView(discord.ui.View):
    def __init__(self, message: str, user_id: int,  timeout: float | None = 300):
        super().__init__(timeout=timeout)

        self.message: str = message
        self.user_id: int = user_id
        self.hours_select: str | None = None
        self.minutes_select: str | None = None
        self.days_select: List[str] | None = None


        # ========== 判定編輯或新增通知 ==========
        hours_select = None
        minutes_select = None
        days_select = None
        self.need_edit: bool = False
        
        notifications = notification_dao.get_user_notifications(user_id)
        if message in notifications:

            notification = notification_dao.get_weekly_notification(user_id, message)
            if notification is not None:

                hours_select = str(notification.hour)
                minutes_select = str(notification.minute)
                days_select = [str(day) for day in notification.weekdays]

                self.need_edit = True
        # =======================================

        self.add_item(HoursSelect(hours_select))
        self.add_item(MinutesSelect(minutes_select))
        self.add_item(DaysSelect(days_select))
        self.add_item(SaveButton())
        self.add_item(CancelButton())

        self.children: list
