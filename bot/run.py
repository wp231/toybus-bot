import os
import re
import signal
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from utils.utils import init_env
from utils.log_manager import bot_log
from typing import Dict, List, Optional
from discord.ext.commands.cog import Cog
from dao.bot_setting_dao import bot_setting
from utils.converters import list_to_table, guild_ids_to_guilds, pascal_to_snake

init_env()

COG_PATH = "./bot/cogs"
BOT_TOKEN = os.getenv("BOT_TOKEN") or ""
INFO_LOG_PATH = bot_setting.get_log_dir_path()

ADMIN_ROLES = bot_setting.get_admin_roles()
ADMIN_GUILD_IDS = bot_setting.get_admin_guilds()
ADMIN_GUILDS = guild_ids_to_guilds(ADMIN_GUILD_IDS)


class Bot(commands.Bot):
    def __init__(self, intents: discord.Intents) -> None:
        super().__init__(command_prefix=commands.when_mentioned, intents=intents)

    async def add_cog(self, cog: Cog):
        cog_name = cog.__cog_name__
        guild_ids = bot_setting.get_cog_guilds(cog_name)

        if guild_ids:
            guilds = guild_ids_to_guilds(guild_ids)
            await super().add_cog(cog, guilds=guilds)
        else:
            await super().add_cog(cog)

    async def setup_hook(self) -> None:
        for filename in os.listdir(COG_PATH):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    bot_log.info_load_cog(filename[:-3])
                except Exception as e:
                    bot_log.error_load_cog(filename[:-3], e)

    async def on_ready(self) -> None:
        bot_log.info_start()


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = Bot(intents=intents)


def get_load_cogs() -> List[str]:
    '''獲取載入的 cogs'''
    load_cogs = []
    for cog in bot.cogs:
        cog = pascal_to_snake(cog)
        load_cogs.append(cog)
    load_cogs.sort()
    return load_cogs


def get_unload_cogs() -> List[str]:
    '''獲取未載入的 cogs'''
    unload_cogs = []
    for filename in os.listdir(COG_PATH):
        if filename.endswith('.py') and filename[:-3] not in get_load_cogs():
            unload_cogs.append(filename[:-3])
    unload_cogs.sort()
    return unload_cogs


def get_cog_doc(cog_name: str) -> str:
    '''獲取 cogs 說明資訊'''
    with open(f"{COG_PATH}/{cog_name}" + ".py", "r", encoding="UTF-8") as f:
        code = f.read()
    cog_info = re.search(r'__doc__.?=.?"(.+)"', code)

    return cog_info.group(1) if cog_info else ""


async def unload_cogs_to_options(interaction: discord.Interaction, current: str):
    '''轉換未載入 cogs 為命令選項'''
    # 不屬於管理身份組，不給予返回
    if ADMIN_ROLES and not (
        isinstance(interaction.user, discord.Member) and
        any(role.id in ADMIN_ROLES for role in interaction.user.roles)
    ):
        return []

    unload_cogs = get_unload_cogs()
    cogs = []
    for cog in unload_cogs:
        cogs.append(app_commands.Choice(name=cog, value=cog))
    return cogs


async def load_cogs_to_options(interaction: discord.Interaction, current: str):
    '''轉換載入 cogs 為命令選項'''
    # 不屬於管理身份組，不給予返回
    if ADMIN_ROLES and not (
        isinstance(interaction.user, discord.Member) and
        any(role.id in ADMIN_ROLES for role in interaction.user.roles)
    ):
        return []

    load_cogs = get_load_cogs()
    cogs = []
    for cog in load_cogs:
        cogs.append(app_commands.Choice(name=cog, value=cog))
    return cogs


def check_roleauth(func):
    '''設置指令伺服器和身份組'''
    if ADMIN_GUILDS:
        func = app_commands.guilds(*ADMIN_GUILDS)(func)
    if ADMIN_ROLES:
        func = app_commands.checks.has_any_role(*ADMIN_ROLES)(func)
    return func


# 管理員指令
admin_commands: List[app_commands.Command] = []


def add_to_admin_command_list(func: app_commands.Command):
    '''將指令加入管理員指令列表'''
    admin_commands.append(func)
    func.extras["roles"] = ADMIN_ROLES
    return func


@add_to_admin_command_list
@bot.tree.command(name='print_cogs', description='顯示所有可用的 Cogs')
@check_roleauth
async def print_cogs(interaction: discord.Interaction):
    load_cogs_str = ""
    for cog in get_load_cogs():
        load_cogs_str = f"{load_cogs_str}{cog} : {get_cog_doc(cog)}\n"
    unload_cogs_str = ""
    for cog in get_unload_cogs():
        unload_cogs_str = f"{unload_cogs_str}{cog} : {get_cog_doc(cog)}\n"

    embed = discord.Embed(title="可用的 Cogs", color=0x0062ff)
    if load_cogs_str != "":
        embed.add_field(name="已加載的 Cogs", value=load_cogs_str, inline=False)
    if unload_cogs_str != "":
        embed.add_field(name="未加載的 Cogs", value=unload_cogs_str, inline=False)
    await interaction.response.send_message(embed=embed)


async def sync_to_server(guild_id: Optional[int] = None) -> Optional[Dict]:
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
        guilds.extend(bot.guilds)
    else:
        guilds = [await bot.fetch_guild(guild_id)]

    error_sync_guilds = {}
    # 同步到所有伺服器
    for guild in guilds:
        server_name = "Global" if guild is None else guild.name

        try:
            success_commands = await bot.tree.sync(guild=guild)
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


async def guild_ids_to_str(ids) -> str:
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
        guild_name = (await bot.fetch_guild(error_id)).name
        guild_names.append(guild_name)
        error_info = f"{error_info}{guild_name}:\n{ids[error_id]}\n"

    name = "、".join(guild_names)

    return f"{name}\n```\n{error_info}```"


async def sync_message(interaction: discord.Interaction, msg: str = "", guild_id: Optional[int] = None) -> None:
    '''進行同步後修改原始訊息用'''
    if msg:
        msg = f"{msg}\n"

    await interaction.edit_original_response(content=f"{msg}正在同步至伺服器，請稍等...")

    result = await guild_ids_to_str(await sync_to_server(guild_id=guild_id))

    if result == "":
        result = f"成功同步"
    else:
        result = f"無法同步至 {result}"

    await interaction.edit_original_response(content=f"{msg}{result}")


@add_to_admin_command_list
@bot.tree.command(name='load_cog', description='加載 cogs')
@check_roleauth
@app_commands.autocomplete(cog_name=unload_cogs_to_options)
@app_commands.choices(sync=[app_commands.Choice(name='True', value=1)])
async def load_cog(interaction: discord.Interaction, cog_name: str, sync: int = 0):
    user = interaction.user.name
    user_id = interaction.user.id
    try:
        await bot.load_extension(f"cogs.{cog_name}")
        msg = f"加載 {cog_name} 成功"
        await interaction.response.send_message(msg)
        bot_log.info_cmd_load_cog(cog_name, user, user_id)

        if sync:
            await sync_message(interaction, msg)
    except Exception as e:
        bot_log.error_cmd_load_cog(cog_name, user, user_id, e)
        await interaction.response.send_message(f"加載 {cog_name} 失敗\n```{e}```")


@add_to_admin_command_list
@bot.tree.command(name='reload_cog', description='重新加載 cogs')
@check_roleauth
@app_commands.autocomplete(cog_name=load_cogs_to_options)
@app_commands.choices(sync=[app_commands.Choice(name='True', value=1)])
async def reload_cog(interaction: discord.Interaction, cog_name: str, sync: int = 0):
    user = interaction.user.name
    user_id = interaction.user.id
    try:
        await bot.reload_extension(f"cogs.{cog_name}")
        msg = f"重新加載 {cog_name} 成功"
        await interaction.response.send_message(msg)
        bot_log.info_cmd_reload_cog(cog_name, user, user_id)

        if sync:
            await sync_message(interaction, msg)
    except Exception as e:
        bot_log.error_cmd_reload_cog(cog_name, user, user_id, e)
        await interaction.response.send_message(f"重新加載 {cog_name} 失敗\n```{e}```")


@add_to_admin_command_list
@bot.tree.command(name='unload_cog', description='卸載 cogs')
@check_roleauth
@app_commands.autocomplete(cog_name=load_cogs_to_options)
@app_commands.choices(sync=[app_commands.Choice(name='True', value=1)])
async def unload_cog(interaction: discord.Interaction, cog_name: str, sync: int = 0):
    user = interaction.user.name
    user_id = interaction.user.id
    try:
        await bot.unload_extension(f"cogs.{cog_name}")
        msg = f"卸載 {cog_name} 成功"
        await interaction.response.send_message(msg)
        bot_log.info_cmd_unload_cog(cog_name, user, user_id)

        if sync:
            await sync_message(interaction, msg)
    except Exception as e:
        bot_log.error_cmd_unload_cog(cog_name, user, user_id, e)
        await interaction.response.send_message(f"卸載 {cog_name} 失敗\n```{e}```")


async def get_bot_guilds_options(interaction: discord.Interaction, current: str):
    guilds = [app_commands.Choice(name="全部伺服器", value="全部伺服器")]
    for guild in bot.guilds:
        guild = f"{guild.name} ({str(guild.id)})"
        guilds.append(app_commands.Choice(name=guild, value=guild))
    return guilds


@add_to_admin_command_list
@bot.tree.command(name="sync_commands", description="同步指令至伺服器")
@check_roleauth
@app_commands.autocomplete(server=get_bot_guilds_options)
async def sync_commands(interaction: discord.Interaction, server: str):
    user = interaction.user.name
    user_id = interaction.user.id

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

    await sync_message(interaction, guild_id=guild_id)


@bot.tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
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


class GracefulExit(SystemExit):
    code = 1


async def main():

    def raise_graceful_exit(*args):
        loop.stop()
        raise GracefulExit()

    loop = asyncio.get_event_loop()

    signal.signal(signal.SIGINT, raise_graceful_exit)
    signal.signal(signal.SIGTERM, raise_graceful_exit)

    try:
        async with bot:
            await bot.start(BOT_TOKEN)
    except asyncio.CancelledError:
        pass
    except GracefulExit:
        pass
    finally:
        # 退出
        await bot.close()
        bot_log.info_stop()


if __name__ == "__main__":
    asyncio.run(main())
