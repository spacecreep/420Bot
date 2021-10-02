from Packages.firebase_database.firebase_database import add_element, get_json, set_json
from discord.ext import commands
import discord
from datetime import datetime
from settings import *

class accounts(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command(name = "register")
    async def register(self,ctx):
        answer = ""
        await ctx.trigger_typing()
        members = get_json("/Discord Bot/members")
        for membre in members:
            if membre["id"] == ctx.author.id:
                return await ctx.send("Tu possèdes déjà un compte membre ! Va dans le salon <#846625724948676658> !")
        if "<@!" in ctx.message.content and ">" in ctx.message.content: #The player mentionned someone
            message_list = ctx.message.content.split(" ",1)
            message_id_str = message_list[1].replace("<@!","").replace(">","")

            try:
                member_id = int(message_id_str)
            except:
                return await ctx.send("Le format de la commande n'est pas valide.\nfais `!aled register` pour plus d'informations ")
            
            for k in range(len(members)):
                if members[k]["id"] == member_id:
                    nb = k
                    if members[k]["nb invites"] == 5:
                        return await ctx.send("<@!" + str(member_id) + "> a déjà parrainé 5 personnes, et ne peut plus en parrainer à nouveau !")
            
            guy_json = get_json("/Discord Bot/members/" + str(nb))
            guy_json["coins"] += 700
            guy_json["nb invites"] += 1
            if "invites_id" in guy_json:
                guy_json["invites id"].append(ctx.author.id)
            else:
                guy_json["invites id"] = [ctx.author.id]
            set_json("/Discord Bot/members/" + str(nb),guy_json)
            answer += "<@!" + str(member_id) + "> te parraine ! Il gagne 700 pièces, ainsi que un boost sur ses récompenses journalières !"
            
        nb_members = len(members)
        add_element("/Discord Bot/members",{
            str(nb_members) : {"coins" : 100, "id" : ctx.author.id, "name" : ctx.author.name,"multiplier" : 1,"nb invites":0}
        })
        await ctx.author.add_roles(self.bot.get_guild(763050307818094632).get_role(846624730118750219))
        answer += "\nTon compte a bien été créé ! Va dans le salon <#846625724948676658> !"
        return await ctx.send(answer)
    
    @commands.command(name = "banque")
    async def banque(self,ctx):
        await ctx.trigger_typing()
        members = get_json("/Discord Bot/members")
        for membre in members:
            if membre["id"] == ctx.author.id:
                member = ctx.author
                embed = discord.Embed()
                embed.set_author(name = member.name,icon_url = str(member.avatar.url))
                embed.add_field(name = "Montant de pièces possédées :", value = int(membre["coins"]))
                return await ctx.send(embed = embed)
        return await ctx.send("Tu n'as pas encore de compte membre !\nAfin de te créer un compte membre, tu as juste à faire `!register` !\nDe plus, si jamais tu souhaites être parrainé par un membre existant, tu peux le mentionner juste après ton `!register`. Cette personne gagnera des pièces , ainsi que pleins d'autres trucs cools !\nPar exemple, si jamais tu as envie que <@!266207977487335425> gagne des pièces grâce à ton inscription, tu dois taper `!register <@!266207977487335425>` !")

    @commands.command(name = "day")
    async def day(self,ctx):
        await ctx.trigger_typing()

        #check if the persons has an account
        members = get_json("/Discord Bot/members")

        for k in range(len(members)):
            if members[k]["id"] == ctx.author.id:

                member_json = get_json("/Discord Bot/members/" + str(k))

                now = datetime.now(time_paris)
                timestamp = datetime.timestamp(now) + 3600

                if not "!day" in member_json.keys():
                    member_json["!day"] = timestamp
                    a = 0
                    if "nb invites" in member_json.keys():
                        a = member_json["nb invites"]
                    m = member_json["multiplier"]
                    gain = 20
                    member_json["coins"] += int(gain * m * (1.2 ** a))
                    set_json("/Discord Bot/members/" + str(k),member_json)
                    if a == 0 and m == 1:
                        return await ctx.send("Ta récompense journalière : "+str(gain)+" pièces !")
                    if a != 0 and m == 1:
                        return await ctx.send("Ta récompense journalière : "+str(gain)+" pièces !\nPuisque tu parraines " + str(a) + " personne(s), tu gagnes " + str(int(gain * (1.2 ** a)) - gain) + " pièces supplémentaires !!!")
                    return await ctx.send("Ta récompense journalière : "+str(gain)+" pièces !\nPuisque tu parraines " + str(a) + " personne(s), tu gagnes " + str(int(gain * (1.2 ** a))) + " pièces !!!\nOr, tu as un multiplicateur de gain de " + str(m) + ", ce qui fait que tu gagnes " + str(int(gain * m * (1.2 ** a)) - gain) + " pièces supplémentaires !!!!!")
            
                pipi = member_json["!day"]
                last_update = datetime.fromtimestamp(pipi).strftime("%w")
                date_now = now.strftime("%w")

                if date_now != last_update :
                    member_json["!day"] = timestamp
                    a = member_json["nb invites"]
                    m = member_json["multiplier"]
                    gain = 20
                    member_json["coins"] += int(gain * m * (1.2 ** a))
                    set_json("/Discord Bot/members/" + str(k),member_json)
                    if a == 0 and m == 1:
                        return await ctx.send("Ta récompense journalière : "+str(gain)+" pièces !")
                    if a != 0 and m == 1:
                        return await ctx.send("Ta récompense journalière : "+str(gain)+" pièces !\nPuisque tu parraines " + str(a) + " personne(s), tu gagnes " + str(int(gain * (1.2 ** a)) - gain) + " pièces supplémentaires !!!")
                    return await ctx.send("Ta récompense journalière : "+str(gain)+" pièces !\nPuisque tu parraines " + str(a) + " personne(s), tu gagnes " + str(int(gain * (1.2 ** a))) + " pièces !!!\nOr, tu as un multiplicateur de gain de " + str(m) + ", ce qui fait que tu gagnes " + str(int(gain * m * (1.2 ** a)) - gain) + " pièces supplémentaires !!!!!")
            
                if timestamp - member_json["!day"] > 86400:
                    member_json["!day"] = timestamp
                    a = member_json["nb invites"]
                    m = member_json["multiplier"]
                    gain = 20
                    member_json["coins"] += int(gain * m * (1.2 ** a))
                    set_json("/Discord Bot/members/" + str(k),member_json)
                    if a == 0 and m == 1:
                        return await ctx.send("Ta récompense journalière : "+str(gain)+" pièces !")
                    if a != 0 and m == 1:
                        return await ctx.send("Ta récompense journalière : "+str(gain)+" pièces !\nPuisque tu parraines " + str(a) + " personne(s), tu gagnes " + str(int(gain * (1.2 ** a)) - gain) + " pièces supplémentaires !!!")
                    return await ctx.send("Ta récompense journalière : "+str(gain)+" pièces !\nPuisque tu parraines " + str(a) + " personne(s), tu gagnes " + str(int(gain * (1.2 ** a))) + " pièces !!!\nOr, tu as un multiplicateur de gain de " + str(m) + ", ce qui fait que tu gagnes " + str(int(gain * m * (1.2 ** a)) - gain) + " pièces supplémentaires !!!!!")
            
                return await ctx.send("Tu as déjà collecté ta récompense journalière ! Reviens demain pour une autre récompense !!!")

        return await ctx.send("Tu n'as pas encore de compte membre !\nAfin de te créer un compte membre, tu as juste à faire `!register` !\nDe plus, si jamais tu souhaites être parrainé par un membre existant, tu peux le mentionner juste après ton `!register`. Cette personne gagnera des pièces , ainsi que pleins d'autres trucs cools !\nPar exemple, si jamais tu as envie que <@!266207977487335425> gagne des pièces grâce à ton inscription, tu dois taper `!register <@!266207977487335425>` !")

def setup(bot):
    bot.add_cog(accounts(bot))