#imports
import discord
from discord import activity
from discord.ext import commands, tasks
from discord.ui import view
from Packages.firebase_database.firebase_database import add_coins, get_json, is_member, set_json
import collections, asyncio
from settings import *

#variables
prix_activité = 50
prix_1h = 15
prix_4h = 50
prix_12h = 120
prix_24h = 200
prix_48h = 350
prix_jour = 100
prix_ = [prix_1h,prix_4h,prix_12h,prix_24h,prix_48h]
temps = [1,4,12,24,48]

presentation = """Salut {0} !
Tu souhaites donc changer mon message de statut ? Je suis là pour voir ça avec toi !
Tout d'abord, sache que le message d'activité ou de statut correspond à ce qui est marqué sous mon pseudo dans le serveur discord.
Tu peux mettre n'importe quel message d'activité ! La seule contrainte est que il doit être de la forme 'Joue à ...','Ecoute ...','Regarde ...' ou 'Streame ...'
*Par exemple, tu peux choisir que l'on me voie avec le message d'activité 'en train de jouer à sucer des bites avec Léo' !*

**Cela te coûte {1} pièces pour changer mon message d'activité.**
Celui-ci dure alors jusqu'a ce que qqn d'autre le change à son tour

Néanmoins, tu peux également payer pour protéger ce message et qu'il ne puisse pas petre modifié pendant une certaine durée! Cela évite que tu payes 50 pièces pour voir ton message apparaître seulement 5 secondes...
Voici les prix des protections :
         -> 1h : {2} pièces
         -> 4h : {3} pièces
         -> 12h : {4} pièces
         -> 24h : {5} pièces
         -> 48h : {6} pièces
         -> chaque jour supplémentaire : {7} pièces

Pour changer mon message d'activité, envoie dans cette conversation : `!activité [optionnel: nombre d'heures de protection] [le nouveau message d'activité]`
ATTENTION : Le nouveau message d'activité doit commencer soit par 'Joue à', 'Ecoute', 'Regarde' ou 'Streame'
*Par exemple, tu peux envoyer `!activité Joue à manger son caca` ou encore `!activité 24 Streame un film de boules`*

ATTENTION LE NOMBRE D'HEURES DE PROTECTION DU MESSAGE DOIT ETRE UN NOMBRE ENTIER"""

shop_message = """**Bienvenue dans le magasin !**
*Pour l'instant, il y a peu d'articles à vendre mais ils vont venir au fur et à mesure des semaines à venir !*

Pour seulement 50 pièces tu peux changer mon message d'activité !
*Par exemple, tu peux faire en sorte que je sois 'En train de jouer à manger du caca' ou 'En train de jouer à baiser le chien de Léo'*"""

#buttons
class Shop_button(discord.ui.View):
    def __init__(self,bot):
        super().__init__()
        self.bot = bot
        self.timeout = 70000
        
    @discord.ui.button(label='Changer le message de statut du bot', style=discord.ButtonStyle.green)
    async def change_statut(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.user.send(presentation.format(interaction.user.name,prix_activité,prix_1h,prix_4h,prix_12h,prix_24h,prix_48h,prix_jour))


#commands cog
class Boutique(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @tasks.loop(hours=12)
    async def actualize_shop(self):
        await asyncio.sleep(5)
        messages = await self.bot.get_channel(membre_boutique).history().flatten()
        for message in messages:
            await message.delete()
        await self.bot.get_channel(membre_boutique).send(content = shop_message, view=Shop_button(self.bot))
    
    @commands.command(name = "activité")
    async def activité(self,ctx):
        await ctx.trigger_typing()
        if str(ctx.channel.type) != "private":
            return await ctx.send("Cette commande n'est accessible que en message privé avec le bot.")
        
        #on split le message et on check si il est correct
        message = ctx.message.content.split("!activité ",1)[1]
        L = message.split(" ",1)
        new_msg = ""
        protection = 0
        try:
            protection = int(L[0])
            new_msg = L[1]
        except:
            new_msg = message

        #On check le type de message
        type = ""

        if new_msg.startswith("Ecoute"):
            type = discord.Activity(type=discord.ActivityType.listening, name=new_msg.replace("Ecoute"," "))
        if new_msg.startswith("Streame"):
            type = discord.Streaming(name=new_msg.replace("Streame"," "),url="https://www.youtube.com/watch?v=4PZOtDqGAQU")
        if new_msg.startswith("Joue à"):
            type = discord.Game(name=new_msg.replace("Joue à"," "))
        if new_msg.startswith("Regarde"):
            type = discord.Activity(type=discord.ActivityType.watching, name=new_msg.replace("Regarde"," "))
        
        if type == "":
            return await ctx.send("Le nouveau message d'activité du bot doit commencer par l'un des mots suivants :\n-> Joue à\n-> Ecoute\n-> Streame\n-> Regarde\nSi tu as une question n'hésite pas à demander de l'aide dans le serveur!")

        #on check si le bot a un shield
        settings = get_json("Discord Bot/settings/activity_message")
        now = get_time().timestamp()
        if now < settings["end"]:
            return await ctx.send("Désolé mais " + self.bot.get_user(settings["id"]).name + " a protégé le message d'activité du bot !\nDurée restante : " + str(int(100*(settings["end"]-now)/3600)/100) + "h" )
        
        #on check alors ses sous
        nb = is_member(ctx.author.id)
        if nb < 0: return
        member_json = get_json("Discord Bot/members/" + str(nb))

        #check du prix à payer
        prix = 50
        k = -1
        if protection != 0:
            for l in range(len(prix_)):
                if temps[l] == int(protection):
                    k = l
                    prix += prix_[l]
        if k < 0 and 0 < protection <= 24:
            return await ctx.send("Rentre un nombre d'heures valide stp fréro")
        if protection > 24:
            prix += prix_24h + ((protection - 24)/24) * prix_jour
        
        if member_json["coins"] < prix:
            return await ctx.send("Tu n'as pas assez de sous °3°")

        #si tout est ok
        member_json["coins"] -= prix
        set_json("Discord Bot/members/" + str(nb),member_json)
        settings["id"] = ctx.author.id
        if protection > 0: settings["end"] = now + protection * 3600
        settings["message"] = new_msg
        set_json("Discord Bot/settings/activity_message",settings)

        if new_msg.startswith("Streame"):
            await ctx.send("Tu as choisi de me faire afficher que je streamais qqchose, tu peux donc choisir sur quel lien sont dirigés les gens lorsque ils cliquent sur mon stream sur mon profil !\nEnvoie !url `url_que_tu_veux` !")

        await self.bot.change_presence(activity=type)

        mess = "Merci à toi " + ctx.author.name + " tu viens de dépenser " + str(prix) + " pièces pour mettre le message suivant : `" + new_msg + "`"
        mess2 = ctx.author.name + " viens de dépenser " + str(prix) + " pièces pour me mettre le message d'activité suivant : `" + new_msg + "`"

        if protection>0:
            mess += ", avec un protection de " + str(protection) + " heures !"
            mess2 += ", avec un protection de " + str(protection) + " heures !"

        await self.bot.get_channel(channel_general).send(mess2)
        await ctx.send(mess)

    @commands.command(name = "url")
    async def url(self,ctx):
        await ctx.send("Patiente un peu, mes développeurs travaillent d'arrache pied pour mettre en place cette fonctionnalité !")

            
def setup(bot):
    b = Boutique(bot)
    print("ok")
    b.actualize_shop.start()
    bot.add_cog(b)
    