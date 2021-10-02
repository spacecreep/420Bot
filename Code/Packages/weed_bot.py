from Packages.firebase_database.firebase_database import get_json, set_json
from discord.ext import commands
import discord
from settings import *

class weed_bot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name = "add_list")
    async def add_list(self,ctx):
        await ctx.trigger_typing()

        #if its in the wrong channel
        if ctx.channel.id != channel_bot_settings:
            return await ctx.send("Cette commande n'est pas disponible dans ce salon !")
        
        #get the list name, and the message
        try:
            list_name = ctx.message.content.split(" ",2)[1]
            message_to_add = ctx.message.content.split(" ",2)[2]
        except:
            return await ctx.send("Casse pas les couilles gros fais la commande normalement")

        #check the stupidity of the author
        if list_name == "" or message_to_add == "":
            return await ctx.send("Casse pas les couilles gros fais la commande normalement")
            
        #get the words list
        messages_json = get_json("/Discord Bot/messages")

        #if wrong list name
        if not list_name in messages_json.keys():
            return await ctx.send("Casse pas les couilles gros, ya pas de liste qui s'appelle " + list_name + " ...")
            
        #else, add the word/sentence
        if list_name in ["message_join","message_leave"] and not "{}" in ctx.message.content:
            return await ctx.send("Désolé fréro, mais ton message doit contenir les caractères `{}`")
        messages_json[list_name].append(message_to_add)
        set_json("/Discord Bot/messages",messages_json)
        return await ctx.channel.send("C'est bon fréro, `" + message_to_add + "` a bien été ajouté à la liste `" + list_name + "` !")
    
    @commands.command(name = "show_list")
    async def show_list(self,ctx):
        await ctx.trigger_typing()

        #if its in the wrong channel
        if ctx.channel.id != channel_bot_settings:
            return await ctx.send("Cette commande n'est pas disponible dans ce salon !")
            
        #get the list name, and the message
        try:
            list_name = ctx.message.content.split(" ",1)[1]
        except:
            return await ctx.send("Casse pas les couilles gros fais la commande normalement")
        #check the stupidity of the author
        if list_name == "":
            return await ctx.send("Casse pas les couilles gros fais la commande normalement")
            
        #get the words list
        messages_json = get_json("/Discord Bot/messages")

        #if wrong list name
        if not list_name in messages_json.keys():
            return await ctx.send("Casse pas les couilles gros, ya pas de liste qui s'appelle " + list_name + " ...")
            
        #else, get the words
        embed = discord.Embed(title = "Mots de la liste " + list_name)
        for k in range(len(messages_json[list_name])):
            embed.add_field(name = "Mot n° " + str(k), value = messages_json[list_name][k], inline = True)
        return await ctx.send(embed = embed)
    
    @commands.command(name="remove_list")
    async def remove_list(self,ctx):
        await ctx.trigger_typing()

        #if its in the wrong channel
        if ctx.channel.id != channel_bot_settings:
            return await ctx.send("Cette commande n'est pas disponible dans ce salon !")
        
        #get the list name, and the message
        try:
            list_name = ctx.message.content.split(" ",2)[1]
            message_to_remove = ctx.message.content.split(" ",2)[2]
        except:
            return await ctx.send("Casse pas les couilles gros fais la commande normalement")

        #check the stupidity of the author
        if list_name == "" or message_to_remove == "":
            return await ctx.send("Casse pas les couilles gros fais la commande normalement")
            
        #get the words list
        messages_json = get_json("/Discord Bot/messages")

        #if wrong list name
        if not list_name in messages_json.keys():
            return await ctx.send("Casse pas les couilles gros, ya pas de liste qui s'appelle " + list_name + " ...")
        
            
        #else, get the word index
        index = -1
        for k in range(len(messages_json[list_name])):
            if messages_json[list_name][k] == message_to_remove:
                index = k
        if index < 0: #handle if the word isnt in the list
            return await ctx.send("Désolé fréro, la liste `" + list_name + "` ne contient pas `" + message_to_remove + "`")
        #else, we remove it
        del(messages_json[list_name][index])
        set_json("/Discord Bot/messages",messages_json)
        return await ctx.channel.send("C'est bon fréro, `" + message_to_remove + "` a bien été retiré de la liste `" + list_name + "` !")

def setup(bot):
    bot.add_cog(weed_bot(bot))