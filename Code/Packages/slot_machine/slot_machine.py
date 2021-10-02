from Packages.firebase_database.firebase_database import get_json, set_json
import random
import collections
import discord
from discord.ext import commands
from discord.ext.commands import bot
from settings import *
import time

def gain_tirage(L):
    M = [random.choice(L) for k in range(5)]
    caca = collections.Counter(M).most_common(1)
    chiffre = caca[0][0]
    nb = caca[0][1]

    if 6 in M: return 0,M

    if nb == 5:
        if chiffre == 1: return 5000,M
        if chiffre == 2: return 2000,M
        return 1000,M
    if nb == 4:
        if chiffre == 1: return 700,M
        if chiffre == 2: return 600,M
        if chiffre == 3: return 500,M
        if chiffre == 4: return 300,M
        return 200,M
    if nb == 3:
        if chiffre == 1: return 200,M
        if chiffre == 2: return 150,M
        if chiffre == 3: return 100,M
        if chiffre == 4: return 75,M
        return 50,M
    return 0,M

class slot_machine(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.players = []
        self.delay = 1
    
    @commands.command(name = "r")
    async def r(self,ctx):
        now = time.time()
        a = False
        for _ in self.players:
            if _[0] == ctx.author.id:
                if now - _[1] - self.delay < 0:
                    return await ctx.reply("Tu dois encore attendre " + str(int(-(now - _[1] - self.delay )*10)/10) + " secondes avant de pouvoir jouer à nouveau !")
                else:
                    _[1] = now
                    a = True
        if not a: self.players.append([ctx.author.id,now])

        prix = 20
        if ctx.channel.id != slot_machine_channel: return
        await ctx.trigger_typing()

        #On check si le mec a les thunes
        members_json = get_json("Discord Bot/members")

        nb = -1
        for k in range(len(members_json)):
            if members_json[k]["id"] == ctx.author.id:
                nb = k
        
        if nb == -1:
            return await ctx.send("Tu n'as pas encore de compte membre !\nAfin de te créer un compte membre, tu as juste à faire `!register` !\nDe plus, si jamais tu souhaites être parrainé par un membre existant, tu peux le mentionner juste après ton `!register`. Cette personne gagnera des pièces , ainsi que pleins d'autres trucs cools !\nPar exemple, si jamais tu as envie que <@!266207977487335425> gagne des pièces grâce à ton inscription, tu dois taper `!register <@!266207977487335425>` !")
        
        member_json = get_json("Discord Bot/members/" + str(nb))

        if member_json["coins"] < prix:
            return await ctx.send("T'as pas assez de thunes UwU")
        
        #on check le gain
        taxe = -prix
        member_json["coins"] += taxe
        L = [1,2,3,4,5,6]
        gain,slots = gain_tirage(L)
        print(slots)
        if 6 in slots:
            message = "Oh non, tu as perdu ta mise car guireg apparaît dans ton résultat !"
        elif gain + taxe < 0:
            message = "Oh non, tu as perdu ta mise !\nRetente ta chance °3°"
        else:
            message = "Tu remportes " + str(gain) + " pièces !!!"
        
        #on envoie le message
        emojis = ["<:weed:843904601354534972>","<:modesperme:845140692401127484>","<:mecbranche:845151114445062165>","<:high:862038168529928223>","<:highguy:843914797850296322>","<:guireglepd:865327742383161355>"]
        
        if gain >= 500:
            await self.bot.get_channel(channel_general).send(ctx.author.name + " viens tout juste de gagner " + str(gain) + " pièces à la {0.mention} !!!".format(self.bot.get_channel(slot_machine)))
        
        mess=""
        for k in slots:
            mess += emojis[k-1]
        mess += "\n" + message
        await ctx.send(mess)
        
        #update les pièces du joueur
        member_json["coins"] += gain
        if not "slot_machine" in member_json.keys():
            member_json["slot_machine"] = {"nb_tirages":1,"gain_total":gain}
        member_json["slot_machine"]["nb_tirages"] += 1
        member_json["slot_machine"]["gain_total"] += gain + taxe
        
        set_json("Discord Bot/members/" + str(nb),member_json)
        

def setup(bot):
    bot.add_cog(slot_machine(bot))