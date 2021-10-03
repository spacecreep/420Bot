from selenium.webdriver.chrome.options import Options 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Packages.firebase_database.firebase_database import get_json, is_member, set_json
import discord
from datetime import datetime
from discord.ext import commands
from settings import *
#variables
mess_accueil = """Salut {} !
Je suis là pour t'aider à lier ton compte Rocket League à ton compte discord !

Envoie dans ce salon `!vroom <ton_pseudo_rocket_league>`!
Par exemple, si tu ton pseudo est 'Gros chibre du 44', tu dois envoyer `!vroom Gros chibre du 44`"""

#functions
def infosJoueurRL(joueur):
    stats = {}

    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless") # On va lancer le navigateur Chrome en headless, i.e. sans interface graphique
    driver = webdriver.Chrome(options=chrome_options)

    driver.get("https://rocketleague.tracker.network/rocket-league/profile/epic/"+joueur+"/overview") #connexion au site
    wait = WebDriverWait(driver, 10)
    print("started")
    #nb_vict
    nb_vict = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid__sidebar-left > aside > div.overview.card.bordered.header-bordered.responsive > div > div:nth-child(1) > div > div.numbers > span.value")))
    nb_vict_fr=""
    for char in nb_vict.text:
        if char!=',':
            nb_vict_fr=nb_vict_fr+char
    
    stats["nb_vict"] = int(nb_vict_fr)
    print("nb_vict")
    #nb_goals
    nb_buts = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid__sidebar-left > aside > div.overview.card.bordered.header-bordered.responsive > div > div:nth-child(3) > div > div.numbers > span.value")))
    nb_buts_fr= ""
    for char in nb_buts.text:
        if char!=',':
            nb_buts_fr=nb_buts_fr+char
    stats["nb_buts"] = int(nb_buts_fr)
    print("nb_buts")
    #MVP
    nb_mvp = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid__sidebar-left > aside > div.overview.card.bordered.header-bordered.responsive > div > div:nth-child(7) > div > div.numbers > span.value")))
    nb_mvp_fr= ""
    for char in nb_mvp.text:
        if char!=',':
            nb_mvp_fr=nb_mvp_fr+char
    stats["nb_mvp"] = int(nb_mvp_fr)
    print("nb_mvp")
    #Saves
    nb_saves = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#app > div.trn-wrapper > div.trn-container > div > main > div.content.no-card-margin > div.site-container.trn-grid.trn-grid--vertical.trn-grid--small > div.trn-grid__sidebar-left > aside > div.overview.card.bordered.header-bordered.responsive > div > div:nth-child(6) > div > div.numbers > span.value")))
    nb_saves_fr= ""
    for char in nb_saves.text:
        if char!=',':
            nb_saves_fr=nb_saves_fr+char
    stats["nb_saves"] = int(nb_saves_fr)
    print("nb_saves")
    return stats

async def rl_update(bot,member,ctx):
    print("Le joueur a fait la commande")
    progress = infosJoueurRL(member["rl"]["stats"]["pseudo"])
    progress["pseudo"] = member["rl"]["stats"]["pseudo"]
    
    old_stats = member["rl"]["stats"]

    if "nb_vict" not in old_stats.keys():
        print("Ok fréro, à partir de maintenant je vais tenir comptes de tes parties de Rocket League !")
        member["rl"]["stats"] = progress
        set_json("Discord Bot/members/" + str(is_member(member["id"])),member)
        return

    nb_win = progress["nb_vict"] - old_stats["nb_vict"]
    nb_buts = progress["nb_buts"] - old_stats["nb_buts"]

    if nb_win == nb_buts == 0:
        print("ok")
        return await ctx.send("Tu n'as pas marqué de buts ni gagné de parties depuis la dernière fois !")
    
    gain = nb_win * 5 + nb_buts
    await ctx.send("Bravo, tu as gagné {} parties depuis la dernière fois et marqué {} buts! Tu gagnes donc un total de {} pièces!".format(nb_win,nb_buts,gain))

    member["rl"]["stats"] = progress
    member["coins"] += gain
    set_json("Discord Bot/members/" + str(is_member(member["id"])),member)


#commands
class rl_tracker(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command(name = "rl")
    async def rl(self,ctx):
        #if its the wrong channel
        if ctx.channel.id != rl_accueil_channel: await ctx.send("Cette commande n'est disponible que dans le salon {0.mention}".format(self.bot.get_channel(rl_accueil_channel)))
        #if the user already registered
        nb = is_member(ctx.author.id)
        if nb < 0: return
        member_json = get_json("Discord Bot/members/" + str(nb))
        if "rl" in member_json.keys():
            if "need_verif" == False:
                return await ctx.author.send("Ton compte est déjà vérifié ! Va drifter sur les pelouses de RL !!!")
        return await ctx.author.send("Envoie !vroom 'ton pseudo rl' dans cette conversation pour associer ce compte RL à ton compte membre !")

    @commands.command(name = "vroom")
    async def vroom (self,ctx):
        pseudo = ctx.message.content.split("!vroom ",1)[1]

        #if the user already registered
        nb = is_member(ctx.author.id)
        if nb < 0: return
        member_json = get_json("Discord Bot/members/" + str(nb))
        if "rl" in member_json.keys():
            if "need_verif" == False:
                return await ctx.send("Ton compte est déjà vérifié ! Va drifter sur les pelouses de RL !!!")

        code = get_random_code()
        member_json["rl"] = {"need_verif":True,"verif_code":code,"éternels":[],"stats":{"pseudo":pseudo}}
        set_json("Discord Bot/members/" + str(nb),member_json)
        return await ctx.send("Tu dois demander en ami `Ragondindu36` dans rocket league \nUne fois que c'est fait, envoie !verif_rl dans ce salon !")

    @commands.command(name = "verif_rl")
    async def verif_rl(self,ctx):
        #if the user already registered
        nb = is_member(ctx.author.id)
        if nb < 0: return
        member_json = get_json("Discord Bot/members/" + str(nb))
        if "rl" in member_json.keys():
            if "need_verif" == False:
                return await ctx.send("Ton compte est déjà vérifié ! Va drifter sur les pelouses de RL !!!")
        await self.bot.get_channel(channel_bot_settings).send("{0.mention} il y a ".format(self.bot.get_user(366579740976480257)) + ctx.author.name + ", dont le pseudo RL est " + member_json["rl"]["stats"]["pseudo"] + " qui t'as demandé en ami dans RL !! Fais !verif_rl_modo 'Le pseudo du gars dans RL' une fois qu'il t'as envoyé sa demande d'ami")
        await ctx.send("Supernickel ! Patiente un peu le temps que je vérifie que tu as bien fait la demande d'ami (ça peut prendre 24h max)")

    @commands.command(name= "verif_rl_modo")
    async def verif_rl_modo(self,ctx):
        if ctx.author.id != 366579740976480257: return
        members = get_json("Discord Bot/members")
        pseudo = ctx.message.content.split("!verif_rl_modo ",1)[1]
        for membre in members:
            if "rl" in membre.keys():
                if "pseudo" in membre["rl"]["stats"].keys():
                    if membre["rl"]["stats"]["pseudo"] == pseudo:
                        membre["rl"]["need_verif"] = False
                        set_json("Discord Bot/members/" + str(is_member(membre["id"])),membre)
                        await self.bot.get_user(membre["id"]).send("Ton compte RL est vérifié !!! Va donc drifter sur les terrains de Rocket League !!")
                        return
        return await ctx.send("Ya pas de joueur du serveur qui a le pseudo suivant: '" + pseudo + "' ! Vérifie l'orthographe ou alors vois direct avec le joueur si ya pas une couille")


def setup(bot):
    bot.add_cog(rl_tracker(bot))