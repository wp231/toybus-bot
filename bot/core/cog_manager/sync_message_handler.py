import discord
from typing import Optional, TYPE_CHECKING
from utils.converters import list_to_table

if TYPE_CHECKING:
    from ..bot import Bot

class SyncMessageHandler:
    """
    Slash 指令同步訊息處理器

    方法
    ------
    sync_message(interaction, msg, guild_id)
        發送同步提示訊息，並更新為同步結果訊息
    """

    def __init__(self, bot: 'Bot') -> None:
        self.bot = bot

    async def __guild_ids_to_str(self, ids) -> str:
        '''sync_to_server 函數的返回值專用

        將儲存同步錯誤的伺服器 ID 字典轉換成錯誤資訊字串用於顯示

        Returns: str
        --------
        output_str = """
                伺服器名、伺服器名、伺服器名
                ```
                伺服器名:
                同步錯誤訊息...
                伺服器名:
                同步錯誤訊息...
                伺服器名:
                同步錯誤訊息...
                ```
        """
        '''

        if ids is None:
            return ""

        error_info = ""
        guild_names = []

        if None in ids:
            guild_names = ["全局"]
            error_info = f"{error_info}全局:\n{ids[None]}\n"
            del ids[None]

        for error_id in ids:
            guild_name = (await self.bot.fetch_guild(error_id)).name
            guild_names.append(guild_name)
            error_info = f"{error_info}{guild_name}:\n{ids[error_id]}\n"

        name = "、".join(guild_names)

        return f"{name}\n```\n{error_info}```"


    async def sync_message(self, interaction: discord.Interaction, msg: str = "", guild_id: Optional[int] = None) -> None:
        '''進行同步後修改原始訊息用'''
        if msg:
            msg = f"{msg}\n"

        await interaction.edit_original_response(content=f"{msg}正在同步至伺服器，請稍等...")

        result = await self.__guild_ids_to_str(await self.bot.sync_to_server(guild_id=guild_id))

        if result == "":
            result = f"成功同步"
        else:
            result = f"無法同步至 {result}"

        await interaction.edit_original_response(content=f"{msg}{result}")
