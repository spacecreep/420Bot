from os import name
from discord.ext import commands
from requests.api import get
from Packages.firebase_database.firebase_database import get_json, is_member, set_json
import discord
import random
from settings import *
from riotwatcher import LolWatcher
from datetime import datetime
from Packages.Rocket_league.RLstats420 import rl_update
#this is the file containing all the LoL related commands of the 420 Bot

#variables
message_accueil_lol = """Salut {0} !

Je suis là pour t'aider à configurer ton compte League of Legends afin de l'associer à ton compte discord du serveur 420 gaming !

Tout d'abord, j'aimerais connaître ton nom d'invocateur stp.
Envoie dans ce chat `!summoner <ton nom d'invocateur>`
Par exemple, si ton nom d'invocateur est "Super étron", tu dois entrer `!summoner Super étron`"""

#functions
async def achat(message,bot):
    msg = message.content
    item_str = msg.split(" ",1)[1]
    try:
        item = int(item_str)
    except:
        return await message.author.send(item_str + " n'est pas un numéro valide d'objet de la boutique LoL.")
      
    shop_json = get_json("/LoL/éternels")

    if item < 1 or item > len(shop_json):
        return await message.author.send(str(item) + " ne correspond pas à un numéro d'item du magasin.")
    new_éternel = shop_json[item - 1]

    #collectage des données du membre et détectage de si il a déjà l'éternel
      
    members_json = get_json("Discord Bot/members")

    nb = 0
    for k in range(len(members_json)):
        if members_json[k]["id"] == message.author.id:
            nb = k
            if "éternels" in members_json[k]["lol"].keys():
                for éternel in members_json[k]["lol"]["éternels"]:
                    if éternel["nom"] == new_éternel["nom"]:
                        return await message.author.send("Tu possèdes déjà l'éternel `" + éternel["nom"] + "` !")
      
    #Checkage de si il a les thunasses
    if members_json[nb]["coins"] < new_éternel["prix"]:
        return await message.author.send("Tu n'as pas les thunes pour t'acheter l'éternel `" + new_éternel["nom"] + "` !")
      
    #Envoi du message de confiramtion d'achat
    embed = discord.Embed()
    embed.set_author(name = message.author.name +", tu viens d'acheter l'éternel suivant pour " + str(new_éternel["prix"]) + " pièces",icon_url = "https://cdn.discordapp.com/emojis/843904601354534972.png?v=1")
    embed.add_field(name = new_éternel["nom"],value = new_éternel["description"])
    num_commande = ""
    L = ["a","z","e","r","t","y","u","i","o","p","q","s","d","f","g","h","j","k","l","m","w","x","c","v","b","n","1","2","3","4","5","6","7","8","9","0"]
    for k in range(10):
        num_commande += random.choice(L)
    embed.set_footer(text = "Voici le numéro de ta commande :" + num_commande + "\nSi tu as changé d'avis et que tu souhaites échanger ton éternel ou te faire rembourser, envoie un message à un admin du serveur, ainsi que ton numéro de commande.\nAttention, un éternel ne peut être échangé ou repris que si tu as atteint moins de deux paliers sur celui-ci !")
    await bot.get_channel(boutique_commandes).send(message.author.name + " vient d'acheter l'éternel `" + new_éternel["nom"] + "`. Numéro de commande : " + num_commande)
    await message.author.send(embed = embed)

    #ajoutage de l'éternel
    member_json = get_json("Discord Bot/members/" + str(nb))
    if "éternels" not in member_json["lol"].keys():
        member_json["lol"]["éternels"] = []
    member_json["lol"]["éternels"].append(new_éternel)

    #Retirage des thunasses
    member_json["coins"] -= new_éternel["prix"]

    set_json("Discord Bot/members/" + str(nb),member_json)

async def offre(message,bot):
    return await message.author.send("Désolé, mes développeurs n'ont pas encore prévu que qqn puisse offrir un éternel à qqn ! Patiente un peu")

def get_classement_éternel(éternel,nb):
    members = get_json("Discord Bot/members")
    members_needed = []
    for member in members:
        if "lol" in member.keys():
            if "éternels" in member["lol"].keys():
                for éternel_ in member["lol"]["éternels"]:
                    if éternel_["nom"] == éternel:
                        members_needed.append(member)

    L = []
    #now, we have all the members that have purchased this éternel
    while len(members_needed) > 0 and len(L) < nb:
        max = -1
        best = {}
        for member in members_needed:
            for éternel_ in member["lol"]["éternels"]:
                if éternel_["nom"] == éternel:
                    if éternel_["count"] > max:
                        best = member
                        max = éternel_["count"]
        L.append([best["id"],max])
        members_needed.remove(best)
    
    return L

async def send_classement_éternels(bot):
    éternels = get_json("LoL/éternels")
    embed = discord.Embed(title = "Voici le classement des meilleurs joueurs dans chaque éternel !")
    for éternel in éternels:
        L = get_classement_éternel(éternel["nom"],3)
        if L != []:
            mess = ""
            for k in L:
                print(k)
                mess += bot.get_user(k[0]).name + ": " + str(int(k[1])) + "\n"
            embed.add_field(name = "**" + éternel["nom"] + "**",value = mess,inline=True)
    embed.set_footer(text = "Dernière mise à jour à " + str(get_time()))
    await bot.get_channel(lol_classement_channel).send(embed = embed)
        


#main class
class LoL(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.watcher = LolWatcher(RiotKey)
    
    @commands.command(name="update")
    async def update(self,ctx):
        if ctx.channel.id == lol_bot_channel:
            await ctx.trigger_typing()

            #get the member
            members = get_json("/Discord Bot/members")
            nb = -1
            for k in range(len(members)):
                if members[k]["id"] == ctx.author.id:
                    nb = k
            
            #if the member isnt referenced yet
            if nb < 0:
                return await ctx.send("Tu n'as pas encore de compte membre !\nAfin de te créer un compte membre, tu as juste à faire `!register` !\nDe plus, si jamais tu souhaites être parrainé par un membre existant, tu peux le mentionner juste après ton `!register`. Cette personne gagnera des pièces , ainsi que pleins d'autres trucs cools !\nPar exemple, si jamais tu as envie que <@!266207977487335425> gagne des pièces grâce à ton inscription, tu dois taper `!register <@!266207977487335425>` !")
            
            #else, we get the member json to operate on it
            member_json = get_json("/Discord Bot/members/" + str(nb))

            #then, we need to check if the person already verified its account
            if "lol" not in member_json.keys():
                return await ctx.send("Tu n'as pas associé de compte lol à ton compte membre, ou alors tu n'as pas achevé la démarche pour l'associer ! Va dans le salon {0.mention} pour plus d'infos !".format(self.bot.get_channel(lol_accueil)))
            if member_json["lol"]["player_data"]["need_verif"]:
                return await ctx.send("Tu n'as pas associé de compte lol à ton compte membre, ou alors tu n'as pas achevé la démarche pour l'associer !")
            
            last_update = member_json["lol"]["player_data"]["last_timestamp"]
            lol_id = member_json["lol"]["player_data"]["puuid"]

            #now, we collect data of the member account
            me = self.watcher.summoner.by_puuid(riotApiRegion,lol_id)
            me["need_verif"] = False
            me["last_timestamp"] = last_update
            me["verif_id"] = member_json["lol"]["player_data"]["verif_id"]

            #on check ensuite si il a eu des games récentes
            now = datetime.now(time_paris)
            timestamp = datetime.timestamp(now)

            matches = self.watcher.match.matchlist_by_account(riotApiRegion,me["accountId"])
            new_matches = []

            for match in matches["matches"]:
                if int(match["timestamp"]/1000) > last_update:
                    new_matches.append(match)
                    continue
                break
            print(new_matches)
            if len(new_matches) == 0:
                return await ctx.channel.send("Pas de games récentes trouvées ! Dernière game : " + str(datetime.fromtimestamp(int(last_update) + 7200)))
            
            too_long = False
            if len(new_matches)>10:
                too_long = True

            embed = discord.Embed()
            mess = ""
            embed.set_author(name = me["name"],icon_url = "https://storage.googleapis.com/discord-bot-da81e.appspot.com/LoL/playericons/" + str(me["profileIconId"]) + ".png")
            embed.set_footer(text = "Depuis le " + str(datetime.fromtimestamp(int(last_update) + 3600)))

            gain = 0
            id = -1
            kills = 0
            deaths = 0
            win = False
            mess = ""
            nb_heures = 0
            nb_kills = 0
            nb_assists = 0
            nb_wards = 0
            nb_morts = 0
            nb_multikills = 0
            nb_tourelles = 0
            nb_monstres_jgl = 0
            nb_penta = 0
            nb_firstblood = 0
            nb_cs = 0
            nb_damage_dealt = 0
            nb_cc = 0
            nb_thunes = 0
            nb_heal = 0
            nb_damage_received = 0

            last_game = last_update

            for match in new_matches:
                detail = self.watcher.match.by_id(riotApiRegion,match["gameId"])
                if match["timestamp"] / 1000 > last_game:
                    last_game = int(match["timestamp"]/1000)
                
                for participant in detail["participantIdentities"]:
                    if participant["player"]["summonerName"] == me["name"]:
                        id = participant["participantId"]

                data = detail["participants"][id - 1]
                win = data["stats"]["win"]
                kills = data["stats"]["kills"]
                assists = data["stats"]["assists"]
                nb_assists += assists
                deaths = data["stats"]["deaths"]
                #pour les éternels
                nb_heures += detail["gameDuration"] / 3600
                nb_kills += kills
                nb_wards += data["stats"]["visionScore"]
                nb_morts += deaths
                nb_multikills += data["stats"]["doubleKills"]
                nb_tourelles += data["stats"]["turretKills"]
                if "neutralMinionsKilledEnemyJungle" in data["stats"].keys():
                    nb_monstres_jgl += data["stats"]["neutralMinionsKilledEnemyJungle"]
                nb_penta += data["stats"]["pentaKills"]
                if "firstBloodKill" in data["stats"].keys():
                    if data["stats"]["firstBloodKill"]:
                        nb_firstblood += 1
                nb_cs += data["stats"]["totalMinionsKilled"] + data["stats"]["neutralMinionsKilled"]
                nb_damage_dealt += data["stats"]["totalDamageDealtToChampions"]
                nb_cc += data["stats"]["timeCCingOthers"]
                nb_thunes += data["stats"]["goldEarned"]
                nb_heal += data["stats"]["totalHeal"]
                nb_damage_received += data["stats"]["totalDamageTaken"]
                if detail["queueId"] == 450:#Aram
                    gain += 5
                    if win:
                        gain += 5
                        mess += "Tu as gagné une aram (+10),et tu y as fait "+str(kills) + " kills (+"+str(kills)+")\n"
                    else:
                        mess += "Tu as perdu une aram (+5),et tu y as fait "+str(kills) + " kills (+"+str(kills)+")\n"
                    gain += kills
                elif detail["queueId"] == 440:#FLEX
                    if not win: 
                        gain += 20
                        mess += "Tu as perdu une flex (+20),et tu y as fait "+str(deaths) + " morts (+"+str(deaths)+")\n"
                    else:
                        mess += "Tu as gagné une flex (+0),et tu y as fait "+str(deaths) + " morts (+"+str(deaths)+")\n"
                    gain += deaths
                elif detail["queueId"] == 420:#RANKED
                    if win:
                        gain += 20
                        mess += "Tu as gagné une ranked solo/duo (+20)\n"
                    else:
                        mess += "Tu as perdu une ranked solo/duo (+5)\n"
                        gain += 5
                elif detail["queueId"] == 400:#normale
                    if win:
                        gain += 10
                        mess += "Tu as gagné une normale game (+10)\n"
                    else:
                        gain += 2
                        mess += "Tu as perdu une normale game (+2)\n"
                else: #temporaire
                    if win:
                        gain += 10
                        mess += "Tu as gagné une partie en mode temporaire (+10)\n"
                    else:
                        gain += 5
                        mess += "Tu as perdu une partie en mode temporaire (+5) \n"

            me["last_timestamp"] = last_game

            message = ""

            if "éternels" in member_json["lol"].keys():
                for éternel in member_json["lol"]["éternels"]:
                    value = 0

                    #palier
                    palier = 0
                    for k in range(len(éternel["paliers"])):
                        if éternel["count"] >= éternel["paliers"][k]:
                            palier = k+1
                    if éternel["nom"] == "Temps de jeu":
                        value = int(nb_heures*100)/100
                        ancien = int(éternel["count"]*100)/100
                        éternel["count"]=ancien + value
                    if éternel["nom"] == "Nombre d'assistances":
                        value = nb_assists
                        éternel["count"] += value
                    if éternel["nom"] == "Nombre de kills":
                        value = nb_kills
                        éternel["count"]+=nb_kills
                    if éternel["nom"] == "Score de vision":
                        value = nb_wards
                        éternel["count"]+=nb_wards
                    if éternel["nom"] == "Nombre de morts":
                        value = nb_morts
                        éternel["count"]+=nb_morts
                    if éternel["nom"] == "Nombre de kills multiples":
                        value = nb_multikills
                        éternel["count"]+=nb_multikills
                    if éternel["nom"] == "Nombre de tourelles détruites":
                        value = nb_tourelles
                        éternel["count"]+=nb_tourelles
                    if éternel["nom"] == "Monstres tués dans la jungle ennemie":
                        value = nb_monstres_jgl
                        éternel["count"]+=nb_monstres_jgl
                    if éternel["nom"] == "Nombre de pentakills":
                        value = nb_penta
                        éternel["count"]+=nb_penta
                    if éternel["nom"] == "Nombre de premiers sang":
                        value = nb_firstblood
                        éternel["count"]+=nb_firstblood
                    if éternel["nom"] == "Nombre de sbires tués":
                        value = nb_cs
                        éternel["count"]+=nb_cs
                    if éternel["nom"] == "Dégâts infligés aux champions":
                        value = nb_damage_dealt
                        éternel["count"]+=nb_damage_dealt
                    if éternel["nom"] == "Temps de contrôles de foules subis":
                        value = nb_cc
                        éternel["count"]+=nb_cc
                    if éternel["nom"] == "Quantité d'argent gagné":
                        value = nb_thunes
                        éternel["count"]+=nb_thunes
                    if éternel["nom"] == "Nombre de PV soignés":
                        value = nb_heal
                        éternel["count"]+=nb_heal
                    if éternel["nom"] == "Dégâts subis":
                        value = nb_damage_received
                        éternel["count"]+=nb_damage_received
                    
                    new_palier = 0
                    for k in range(len(éternel["paliers"])):
                        if éternel["count"] >= éternel["paliers"][k]:
                            new_palier = k+1
                    message += éternel["nom"] + " : + "+str(value) +"\n"

                    if new_palier != palier:
                        gain += éternel["rewards"][new_palier - 1]
                        message += "Tu viens de passer le palier " + str(new_palier) + " ! Tu remportes " + str(éternel["rewards"][new_palier - 1]) + " pièces !!!\n"
            
            if too_long:
                embed.add_field(name = "Bravo frérot, tu as gagné " + str(gain) + " pièces avec tes games de lol!", value = "T'en a fait plus de 10 depuis la dernière fois, la flemme de tout te détailler", inline = False)
            else:
                embed.add_field(name = "Bravo frérot, tu as gagné " + str(gain) + " pièces avec tes games de lol!", value = mess, inline = False)
            if message != "":
                embed.add_field(name = "Tu as également gagné des points d'éternels :",value = message)
            member_json["coins"] += gain
            member_json["lol"]["player_data"] = me

            set_json("/Discord Bot/members/" + str(nb),member_json)

            await ctx.send(embed = embed)
        
        if ctx.channel.id == rl_bot_channel:
            await ctx.trigger_typing()

            nb = is_member(ctx.author.id)
            if nb<0: return

            member = get_json("Discord Bot/members/"+str(nb))
            if "rl" not in member.keys(): return await ctx.send("Tu n'as pas de compte Rocket League lié à ton compte membre ! Va dans le salon {0.mention} pour plus d'infos !".format(self.bot.get_channel(rl_accueil_channel)) )
            if member["rl"]["need_verif"]: return await ctx.send("Ton compte RL n'est pas encore vérifié! Si tu as du mal à l'associer à ton compte membre, n'hésite pas à demander de l'aide à un admin !!!")

            await rl_update(self.bot,member,ctx)
        

        return await ctx.send("Cette commande n'est dispo que dans les salons {0.mention} et {1.mention}".format(self.bot.get_channel(rl_bot_channel),self.bot.get_channel(lol_bot_channel)))
    
    @commands.command(name = "lol")
    async def lol(self,ctx):
        members_json = get_json("/Discord Bot/members")
        for membre in members_json:
            if membre["id"] == ctx.author.id:
                if "lol" in membre.keys():
                    if membre["lol"]["player_data"]["need_verif"] == False:
                        return await ctx.author.send("Ton compte discord est déjà associé à un compte LoL ! DM un admin si tu souhaites changer le compte associé à ton compte discord !")
                if ctx.channel.id == lol_accueil:
                    return await ctx.author.send(message_accueil_lol.format(ctx.author.name))
        await ctx.send("Cette commande n'est disponible que dans le salon {0.mention}".format(self.bot.get_channel(lol_accueil)))
    
    @commands.command(name = "summoner")
    async def summoner(self,ctx):
        await ctx.trigger_typing()

        if str(ctx.channel.type) != "private":
            return await ctx.send("Cette commande n'est accessible que en message privé avec le bot. Tape `!lol` pour ouvrir un channel privé.")
        
        summoner_name = ctx.message.content.split(" ",1)[1]

        members_json = get_json("/Discord Bot/members")
        for k in range(len(members_json)):
            if members_json[k]["id"] == ctx.author.id:
                nb = k
        
        member_json = get_json("/Discord Bot/members/" + str(nb))

        if "lol" in member_json.keys():
            if member_json["lol"]["player_data"]["need_verif"] == False:
                return await ctx.send("Ton compte discord est déjà associé à un compte LoL ! DM un admin si tu souhaites changer le compte associé à ton compte discord !")
        
        try:
            me = self.watcher.summoner.by_name(riotApiRegion, summoner_name)
        except:
            await ctx.send("Il n'existe pas de compte sur le serveur EUW ayant pour pseudo " + summoner_name + "... Si ton compte n'est pas sur le serveur EUW, contacte un admin du serveur, sinon vérifie que tu as bien tapé ton nom d'invocateur .")
            return
        
        embed = discord.Embed(title = "Est-ce bien ton compte ?" ,colour = discord.Colour.purple())
        embed.set_author(name = me["name"] + ", LvL "+ str(me["summonerLevel"]), icon_url = "https://storage.googleapis.com/discord-bot-da81e.appspot.com/LoL/playericons/" + str(me["profileIconId"]) + ".png")
        me["need_verif"] = True
        icon_id = random.choice([k for k in range(5)])
        me["verif_id"] = icon_id

        now = datetime.now(time_paris)
        timestamp = datetime.timestamp(now)

        me["last_timestamp"] = timestamp
        member_json["lol"] ={}
        member_json["lol"]["player_data"] = me
        set_json("/Discord Bot/members/" + str(nb),member_json)

        embed.set_thumbnail(url = "https://storage.googleapis.com/discord-bot-da81e.appspot.com/LoL/playericons/" + str(icon_id) + ".png")
        embed.add_field(name = "\n \nSi c'est le compte, voilà ce que tu dois faire pour finir la vérification :", value = "Tu dois aller sur ton compte League of legends, et mettre l'icône d'invocateur qui est en haut à droite de ce message.\nUne fois que tu l'as fait, reviens dans cette conversation et tape `!verif` . ",inline = False)
        embed.add_field(name = "Si ce n'est pas le bon, refait juste la commande précédente avec le bon nom",value = "Si tu rencontres un problème, n'hésite pas à dm un admin :)")

        await ctx.send(embed = embed)

    @commands.command(name = "verif")
    async def verif(self,ctx):
        await ctx.trigger_typing()
        if str(ctx.channel.type) != "private":
            await ctx.send("Cette commande n'est accessible que en message privé avec le bot. Tape `!lol` pour ouvrir un channel privé.")
            return

        members_json = get_json("/Discord Bot/members")
        for k in range(len(members_json)):
            if members_json[k]["id"] == ctx.author.id:
                nb = k
        
        member_json = get_json("/Discord Bot/members/" + str(nb))
        
        if member_json["lol"]["player_data"]["need_verif"] == False:
            return await ctx.send("Ton compte discord est déjà associé à un compte LoL ! DM un admin si tu souhaites changer le compte associé à ton compte discord !")
        try:
            summonername = member_json["lol"]["player_data"]["name"]
            me = self.watcher.summoner.by_name(riotApiRegion, summonername)
        except:
            return await ctx.send("Vous devez d'abord faire `!summoner <votre nom d'invocateur>`")
        if not member_json["lol"]["player_data"]["need_verif"]:
            return await ctx.send("Ton compte est déja vérifié ! va donc souper sur la faille au lieu de faire de la merde :)")
        if me["profileIconId"] == member_json["lol"]["player_data"]["verif_id"]:
            member_json["lol"]["player_data"]["need_verif"] = False
            set_json("/Discord Bot/members/" + str(nb),member_json)
            await ctx.send("C'est bon fréro ton compte League of Legends est vérifié ! \nBon soupage sur la faille !")
        else:
            embed = discord.Embed(title = "Tu n'as pas équipé le bon icône !")
            embed.set_thumbnail(url = "https://storage.googleapis.com/discord-bot-da81e.appspot.com/LoL/playericons/" + str(me["profileIconId"]) + ".png")
            embed.add_field(name = "Tu dois mettre cet icône, puis retaper `!verif` dans le chat", value = "Si jamais tu rencontres un quelconque problème, n'hésite pas à dm un admin du serveur !")
            await ctx.send(embed = embed)
    
    @commands.command(name = "éternels")
    async def éternels(self,ctx):
    
        members_json = get_json("Discord Bot/members")
        nb = -1
        for k in range(len(members_json)):
            if members_json[k]["id"] == ctx.author.id:
                nb = k
        
        if nb == -1:
            return await ctx.send("Tu n'as pas encore de compte membre !\nAfin de te créer un compte membre, tu as juste à faire `!register` !\nDe plus, si jamais tu souhaites être parrainé par un membre existant, tu peux le mentionner juste après ton `!register`. Cette personne gagnera des pièces , ainsi que pleins d'autres trucs cools !\nPar exemple, si jamais tu as envie que <@!266207977487335425> gagne des pièces grâce à ton inscription, tu dois taper `!register <@!266207977487335425>` !")
        
        member_json = get_json("Discord Bot/members/" + str(nb))

        if not "éternels" in member_json["lol"].keys():
            return await ctx.send("Tu n'as pas d'éternels ! Va dans {0.mention} pour en acheter !".format(self.bot.get_channel(lol_boutique)))
        if len(member_json["lol"]["éternels"]) == 0:
            return await ctx.send("Tu n'as pas d'éternels ! Va dans {0.mention} pour en acheter !".format(self.bot.get_channel(lol_boutique)))
        embed = discord.Embed()
        embed.set_author(name = "Voici tes éternels " + ctx.author.name + " :",icon_url=str(ctx.author.avatar.url))
        for éternel in member_json["lol"]["éternels"]:
            palier = 0
            for k in range(len(éternel["paliers"])):
                if éternel["count"] >= éternel["paliers"][k]:
                    palier = k + 1
            try:
                embed.add_field(name = éternel["nom"] + " : "+ str(éternel["count"]), value = "Tu est au palier n°" + str(palier) + ".\nProchain palier : " + str(éternel["paliers"][palier]) +", récompense : " + str(éternel["rewards"][palier]) + " pièces .")
            except:
                embed.add_field(name = éternel["nom"] + " : "+ str(éternel["count"]), value = "Tu as terminé cet éternel et obtenu sa médaille ! Fais `/médaille` pour consulter tes médailles !")
        await ctx.send(embed = embed)

    @commands.command(name = "classement")
    async def classement_éternel(self,ctx):
        nb = is_member(ctx.author.id)
        if nb < 0: return await ctx.send("Tu dois te créer un compte membre afin d'accéder à cette fonctionnalité !")
        
        #get the eternel name
        name = ctx.message.content.split("!classement ",1)[1]
        
        mess = ""

        #eternel exists?
        for éternels in get_json("LoL/éternels"):
            if éternels["nom"] == name:
                L = get_classement_éternel(name,10)
                
                mess = "**Classement de l'éternel '" + name + "'**:\n"
                for i in range(len(L)):
                    mess += "#"+str(i+1)+ " "+self.bot.get_user(L[i][0]).name + ": " + str(L[i][1]) + "\n"
        
        member = get_json("Discord Bot/members/"+str(nb))
        try:
            for éternel in member["lol"]["éternels"]:
                if éternel["nom"] == name:
                    mess += "Toi: " + str(éternel["count"])
        except:
            mess+= "Tu ne possèdes pas cet éternel !"
        
        await ctx.send(mess)

def setup(bot):
    bot.add_cog(LoL(bot))