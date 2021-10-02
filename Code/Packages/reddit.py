import praw
import discord
from discord.ext import commands
import random

class reddit(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.client = praw.Reddit(client_id = "pNOO5WjykvCtXIU1u_wcMw",
					client_secret = "u61q1tdueU0tZBvRAe6TDtvrZTIXEQ", 
					user_agent = "420gaming")

    @commands.command(name = "meme")
    async def meme(self,ctx):
        await ctx.trigger_typing()
        subreddit = self.client.subreddit("memes")
        top = subreddit.hot(limit = 100)
        L = []
        for meme in top:
            L.append(meme)
        meme = random.choice(L)
        embed = discord.Embed()
        embed.set_author(name = meme.title,icon_url = str(self.client.redditor(meme.author).icon_img))
        embed.set_image(url = meme.url)

        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(reddit(bot))