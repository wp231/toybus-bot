from typing import TYPE_CHECKING
from discord.ext import commands

if TYPE_CHECKING:
    from ..bot import Bot

class CogExtension(commands.Cog):
    def __init__(self, bot: 'Bot'):
        self.bot = bot