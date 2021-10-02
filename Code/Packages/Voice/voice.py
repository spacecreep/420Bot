#imports
import discord
from discord.ext import commands
from Packages.firebase_database.firebase_database import add_coins, get_json, set_json
import collections
from settings import *

#commands cog
class voice(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_voice_state_update(self,member,before,after):
        if after.channel != None:
            if after.channel.name == "Créer un salon":
                await self.bot.get_guild(763050307818094632).create_voice_channel(name = "Salon de " + member.name,category = discord.utils.get(self.bot.get_guild(763050307818094632).categories, id = 776721073760108544))
                for channel in self.bot.get_guild(763050307818094632).voice_channels:
                    if channel.name == "Salon de " + member.name:
                        await member.move_to(channel)
        if before.channel != None:
            if before.channel.name.startswith("Salon de "):
                if len(before.channel.members) == 0:
                    await before.channel.delete()

def setup(bot):
    bot.add_cog(voice(bot))