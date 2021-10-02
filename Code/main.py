#discord imports
from Packages.website.users import check_new_users
from logging import exception
import discord
from discord.ext import commands, tasks
from discord.ui.button import button
import random, pytz, os, asyncio, collections, io
from datetime import datetime
from riotwatcher import LolWatcher

#imports from the other files
from Packages.Puissance4.main import *
from Packages.slot_machine.slot_machine import gain_tirage
from settings import *
from Packages.lol import achat,offre, send_classement_éternels
from Packages.firebase_database.firebase_database import *
from Packages.Minecraft.mc import *
import Packages.website

#discord
bot = commands.Bot(command_prefix = "!",intents = discord.Intents.all())

#startup extensions
startup_extensions = ["Packages.weed_bot","Packages.Accounts.accounts","Packages.lol","Packages.Puissance4.main","Packages.reddit","Packages.slot_machine.slot_machine","Packages.Voice.voice","Packages.Boutique.boutique","Packages.Rocket_league.RLstats420"]

#functions
async def get_classement_arcade(bot):
  #puissance4
  embed = discord.Embed(title="Classement de la machine à sous")

  #NB TIRAGES
  max_L = []
  while len(max_L) < 3:
    members = get_json("Discord Bot/members")
    member = {}
    max = -100000
    for membre in members:
      if "slot_machine" in membre.keys():
        if membre["slot_machine"]["nb_tirages"] > max and membre not in max_L:
          member = membre
          max = membre["slot_machine"]["nb_tirages"]
    if member!= {}:
      max_L.append(member)
  mess = ""
  for _ in max_L:
    mess += bot.get_user(_["id"]).name + ": " + str(_["slot_machine"]["nb_tirages"]) + "\n"
  embed.add_field(name="Nombre de tirages    /",value=mess)

  #SOUS PERDUS
  max_L = []
  while len(max_L) < 3:
    members = get_json("Discord Bot/members")
    member = {}
    max = 100000
    for membre in members:
      if "slot_machine" in membre.keys():
        if membre["slot_machine"]["gain_total"] < max and membre not in max_L:
          member = membre
          max = membre["slot_machine"]["gain_total"]
    if member!= {}:
      max_L.append(member)
  mess = ""
  for _ in max_L:
    mess += bot.get_user(_["id"]).name + ": " + str(_["slot_machine"]["gain_total"]) + "\n"
  embed.add_field(name="Plus gros pigeons    /",value=mess)

  #SOUS GAGNES
  max_L = []
  while len(max_L) < 3:
    members = get_json("Discord Bot/members")
    member = {}
    max = -100000
    for membre in members:
      if "slot_machine" in membre.keys():
        if membre["slot_machine"]["gain_total"] > max and membre not in max_L:
          member = membre
          max = membre["slot_machine"]["gain_total"]
    if member!= {}:
      max_L.append(member)
  mess = ""
  for _ in max_L:
    mess += bot.get_user(_["id"]).name + ": " + str(_["slot_machine"]["gain_total"]) + "\n"
  embed.add_field(name="Plus gros chatteux    ",value=mess)

  #Rapport gain/tirages
  max_L = []
  while len(max_L) < 3:
    members = get_json("Discord Bot/members")
    member = {}
    max = -100000
    for membre in members:
      if "slot_machine" in membre.keys():
        if membre["slot_machine"]["gain_total"]/membre["slot_machine"]["nb_tirages"] > max and membre not in max_L:
          member = membre
          max = membre["slot_machine"]["gain_total"]/membre["slot_machine"]["nb_tirages"]
    if member!= {}:
      max_L.append(member)
  mess = ""
  for _ in max_L:
    mess += bot.get_user(_["id"]).name + ": " + str(_["slot_machine"]["gain_total"]/_["slot_machine"]["nb_tirages"]) + "\n"
  embed.add_field(name="Meilleur rapport gain/tentatives    ",value=mess)

  #Rapport gain/tirages
  max_L = []
  while len(max_L) < 3:
    members = get_json("Discord Bot/members")
    member = {}
    max = 100000
    for membre in members:
      if "slot_machine" in membre.keys():
        if membre["slot_machine"]["gain_total"]/membre["slot_machine"]["nb_tirages"] < max and membre not in max_L:
          member = membre
          max = membre["slot_machine"]["gain_total"]/membre["slot_machine"]["nb_tirages"]
    if member!= {}:
      max_L.append(member)
  mess = ""
  for _ in max_L:
    mess += bot.get_user(_["id"]).name + ": " + str(_["slot_machine"]["gain_total"]/_["slot_machine"]["nb_tirages"]) + "\n"
  embed.add_field(name="Pire rapport gain/tentatives    ",value=mess)

  await bot.get_channel(arcade_classement_channel).send(embed = embed)

  #puissance4
  embed = discord.Embed(title="Classement du Puissance 4")

  #NB PARTIES
  max_L = []
  while len(max_L) < 3:
    members = get_json("Discord Bot/members")
    member = {}
    max = -100000
    for membre in members:
      if "puissance_4" in membre.keys():
        if (membre["puissance_4"]["looses"] + membre["puissance_4"]["wins"]) > max and membre not in max_L:
          member = membre
          max = membre["puissance_4"]["looses"] + membre["puissance_4"]["wins"]
    if member!= {}:
      max_L.append(member)
  mess = ""
  for _ in max_L:
    mess += bot.get_user(_["id"]).name + ": " + str(_["puissance_4"]["looses"] + _["puissance_4"]["wins"]) + "\n"
  embed.add_field(name="Nombre de matchs    /",value=mess)

  #WINRATE
  max_L = []
  while len(max_L) < 3:
    members = get_json("Discord Bot/members")
    member = {}
    max = -1
    for membre in members:
      if "puissance_4" in membre.keys() and (membre["puissance_4"]["looses"] + membre["puissance_4"]["wins"]) != 0:
        if (membre["puissance_4"]["wins"] / (membre["puissance_4"]["looses"] + membre["puissance_4"]["wins"])) > max and membre not in max_L:
          member = membre
          max = membre["puissance_4"]["wins"] / (membre["puissance_4"]["looses"] + membre["puissance_4"]["wins"])
    if member!= {}:
      max_L.append(member)
  mess = ""
  for _ in max_L:
    mess += bot.get_user(_["id"]).name + ": " + str(int(100 * _["puissance_4"]["wins"] / (_["puissance_4"]["looses"] + _["puissance_4"]["wins"]))) + "%\n"
  embed.add_field(name="Meilleur winrate    /",value=mess)

  max_L = []
  while len(max_L) < 3:
    members = get_json("Discord Bot/members")
    member = {}
    max = 420
    for membre in members:
      if "puissance_4" in membre.keys() and (membre["puissance_4"]["looses"] + membre["puissance_4"]["wins"]) != 0:
        if (membre["puissance_4"]["wins"] / (membre["puissance_4"]["looses"] + membre["puissance_4"]["wins"])) < max and membre not in max_L:
          member = membre
          max = membre["puissance_4"]["wins"] / (membre["puissance_4"]["looses"] + membre["puissance_4"]["wins"])
    if member!= {}:
      max_L.append(member)
  mess = ""
  for _ in max_L:
    mess += bot.get_user(_["id"]).name + ": " + str(int(100 * _["puissance_4"]["wins"] / (_["puissance_4"]["looses"] + _["puissance_4"]["wins"]))) + "%\n"
  embed.add_field(name="Pire winrate    ",value=mess)

  await bot.get_channel(arcade_classement_channel).send(embed = embed)


@bot.event
async def on_member_join(member):
  join_msg = get_json("/Discord Bot/messages/message_join")
  message = random.choice(join_msg)
  await bot.get_channel(channel_general).send(message.format(member.mention))

@bot.event
async def on_member_remove(member):
  join_msg = get_json("/Discord Bot/messages/message_leave")
  message = random.choice(join_msg)
  await bot.get_channel(channel_general).send(message.format(member.name))

@bot.event
async def on_ready():
  puissance4_list = []
  print("Bot is logged in as {0.user}".format(bot))

@bot.event
async def on_message(message):
  msg = message.content
  #if the message is in the minecraft channel, and the player wants to save sthg
  if "!mc_set" in message.content:
    return await message.channel.send(mc_set(message))
  if "!mc_get" in message.content and message.channel.id == mc_channel:
    return await message.channel.send(mc_get())

  #The bot doesnt reacts to its own messages
  if message.author == bot.user:
    return
  #check if a command has been entered
  await bot.process_commands(message)

  #react if one word is in the weed words
  weed_words_json = get_json("/Discord Bot/messages/weed_words")
  caca = False
  if not message.content.startswith("!"):
    for k in range(len(weed_words_json)):
      if weed_words_json[k] in message.content and not caca:
        ref = db.reference("/Discord Bot/messages/weed_response")
        weed_response_json = ref.get()
        reponse = random.choice(weed_response_json)
        await message.channel.send(reponse)
        caca = True

  #Get the actual time
  datetime_Paris = datetime.now(time_paris)
  current_time = datetime_Paris.strftime("%H:%M")

  #si on demande de l'aide
  if "<@!864962061439467570>" in msg:
    if "aled" in msg:
      await message.author.send("Tu as demandé de l'aide ? Attends un peu, mes développeurs sont en train de setup les messages d'aides (liste des commandes .. etc). \nMerci de patienter un peu !")
    else:
      ref = db.reference("/Discord Bot/messages/mention_response")
      response_json = ref.get()
      await message.channel.send(random.choice(response_json))

  #réagis si il est 4h20
  if msg == "420 !" or msg == "420!" and current_time == "04:20":
    for role in message.author.roles:
      if role.id == fortwenirole: return
    await message.author.add_roles(bot.get_guild(763050307818094632).get_role(fortwenirole))
    await message.channel.send("420 ! Bienvenue dans le groupe d'élite que sont les {0.mention} !".format(bot.get_guild(763050307818094632).get_role(fortwenirole)))
  
  #si on veut que le bot envoie un message
  if msg.startswith("?420"):
    if message.channel.id != channel_bot_settings:
      return await message.channel.send("Cette commande n'est disponible que dans le salon {0.mention}".format(bot.get_channel(channel_bot_settings)))
    try:
      await bot.get_channel(int(msg.split(" ",2)[1])).send(msg.split(" ",2)[2])
    except:
      await message.channel.send("Envoie un message de la forme :\n`!420 numéro_salon contenu_message`")

  #a une faible proba d'envoyer un message cho
  a = random.choice([k for k in range(100)])
  if a == 0 and not msg.startswith("!"):
    messages_cho = get_json("/Discord Bot/messages/message_cho")
    await message.channel.send(random.choice(messages_cho))
  
  if message.channel == bot.get_channel(lol_accueil) or message.channel == bot.get_channel(rl_accueil_channel):
    await message.delete()

  
  if message.channel == bot.get_channel(lol_boutique):
    await message.delete()
    if msg.startswith("achat "):
      await achat(message,bot)
    
    elif msg.startswith("offre "):
      await offre(message,bot)

@bot.command()
async def load(ctx):
    if ctx.message.content == "!load Activité":
      await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.streaming,name = messageActivité))
      return
    """Loads an extension."""
    extension_name = ctx.message.content.split("!load ",1)[1]
    try:
        bot.load_extension(extension_name)
    except exception as e:
        await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        return
    await ctx.send("{} loaded.".format(extension_name))

@bot.command()
async def unload(ctx):
    """Unloads an extension."""
    extension_name = ctx.message.content.split("!unload ",1)[1]
    try:
      bot.unload_extension(extension_name)
    except exception as e:
      return ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
    await ctx.send("{} unloaded.".format(extension_name))

#cadeaux aléatoires
class Claim_Gift_10(discord.ui.View):
  def __init__(self):
        super().__init__()
        self.timeout = 70000

  @discord.ui.button(label='Récupérer les 10 pièces !', style=discord.ButtonStyle.blurple)
  async def claim_gift_10(self, button: discord.ui.Button, interaction: discord.Interaction):
    #on récupère les thunes
    if add_coins(interaction.user.id,10) == False: 
      await interaction.response.send_message(content="Tu dois te créer un compte de membre afin de pouvoir encaisser cet argent !", ephemeral=True)
      return
    button.label = str(interaction.user.name + " a déjà collecté ce cadeau !")
    await interaction.response.edit_message(view=self)

    # Make sure to update the message with our updated selves
    
    self.stop()

class Claim_Gift_25(discord.ui.View):
  def __init__(self):
        super().__init__()
        self.timeout = 70000

  @discord.ui.button(label='Récupérer les 25 pièces !', style=discord.ButtonStyle.blurple)
  async def claim_gift_25(self, button: discord.ui.Button, interaction: discord.Interaction):
    #on récupère les thunes
    if add_coins(interaction.user.id,25) == 0: 
      await interaction.response.send_message(content="Tu dois te créer un compte de membre afin de pouvoir encaisser cet argent !", ephemeral=True)
      return
    button.label = str(interaction.user.name + " a déjà collecté ce cadeau !")
    await interaction.response.edit_message(view=self)

    # Make sure to update the message with our updated selves
    
    self.stop()

class Claim_Gift_50(discord.ui.View):
  def __init__(self):
        super().__init__()
        self.timeout = 70000

  @discord.ui.button(label='Récupérer les 50 pièces !', style=discord.ButtonStyle.blurple)
  async def claim_gift_50(self, button: discord.ui.Button, interaction: discord.Interaction):
    #on récupère les thunes
    if add_coins(interaction.user.id,50) == 0: 
      await interaction.response.send_message(content="Tu dois te créer un compte de membre afin de pouvoir encaisser cet argent !", ephemeral=True)
      return
    button.label = str(interaction.user.name + " a déjà collecté ce cadeau !")
    await interaction.response.edit_message(view=self)

    # Make sure to update the message with our updated selves
    
    self.stop()

class Claim_Gift_100(discord.ui.View):
  def __init__(self):
        super().__init__()
        self.timeout = 70000

  @discord.ui.button(label='Récupérer les 100 pièces !', style=discord.ButtonStyle.blurple)
  async def claim_gift_100(self, button: discord.ui.Button, interaction: discord.Interaction):
    #on récupère les thunes
    if add_coins(interaction.user.id,100) == 0: 
      await interaction.response.send_message(content="Tu dois te créer un compte de membre afin de pouvoir encaisser cet argent !", ephemeral=True)
      return
    button.label = str(interaction.user.name + " a déjà collecté ce cadeau !")
    await interaction.response.edit_message(view=self)

    # Make sure to update the message with our updated selves
    
    self.stop()

@bot.command(name = "test")
async def test(ctx):
  if ctx.author.name != "Romain": return
  await bot.get_channel(channel_general).send("Le premier à cliquer sur ce bouton remporte 10 pièces !!!",view = Claim_Gift_10())

######################################################


@tasks.loop(seconds = 30) # repeat after every 5 mn
async def DeleteOldMessages():
  await asyncio.sleep(5)
  await bot.wait_until_ready()
  messages = await bot.get_channel(slot_machine_channel).history().flatten()
  for message in messages:
    origine = message.created_at
    now = datetime.now(time_paris)
    timestamp = datetime.timestamp(now)
    origin = datetime.timestamp(origine)
    if timestamp - origin > 60:
      if not message.content.startswith("**Bienvenue dans la salle des machines à sous du salon d'arcade !**"):
        await message.delete()
        print("Je viens de supprimer le message suivant :" + message.content)

@tasks.loop(seconds = 600) # repeat after every 1h
async def DeleteOldMessagesP4():
  await asyncio.sleep(5)
  await bot.wait_until_ready()
  messages = await bot.get_channel(puissance4_channel).history().flatten()
  for message in messages:
    origine = message.created_at
    now = datetime.now(time_paris)
    timestamp = datetime.timestamp(now)
    origin = datetime.timestamp(origine)
    if timestamp - origin > 300:
      if "vont s'affronter au puissance 4 !!!" not in message.content:
        if not message.content.startswith("**Bienvenue dans la salle de jeu dédiée au Puissance 4 !**"):
          if not "Réagis à ce message pour accepter ou décliner l'invitation !" in message.content and not "vont s'affronter au puissance 4 !!! Il y a une mise de" in message.content:
            await message.delete()
            print("Je viens de supprimer le message suivant :" + message.content)

@tasks.loop(seconds = 60) # repeat after every 60s
async def DeleteOldMessagesLolClassement():
  datetime_Paris = datetime.now(time_paris)
  current_time = datetime_Paris.strftime("%H:%M")
  if current_time != "00:00": return
  await asyncio.sleep(5)
  await bot.wait_until_ready()
  messages = await bot.get_channel(lol_classement_channel).history().flatten()
  for message in messages:
    await message.delete()
  await send_classement_éternels(bot)

@tasks.loop(seconds = 60) # repeat after every 60s
async def DeleteOldMessagesArcadeClassement():
  datetime_Paris = datetime.now(time_paris)
  current_time = datetime_Paris.strftime("%H:%M")
  if current_time != "00:00": return
  await bot.wait_until_ready()
  await asyncio.sleep(5)
  messages = await bot.get_channel(arcade_classement_channel).history().flatten()
  for message in messages:
    await message.delete()
  print("ok")
  await get_classement_arcade(bot)
      

@tasks.loop(hours = 4)
async def CreateBackup():
  print("je viens de créer un backup")
  ref = db.reference("/")
  now = datetime.now(time_paris)
  date_time = now.strftime("%m-%d-%Y, %H-%M-%S")
  with open("backup/" + date_time + ".json","w", encoding = "utf-8") as file:
    json.dump(ref.get(),file)

@tasks.loop(minutes = 10)
async def generate_gift():
  await bot.wait_until_ready()
  a =random.randint(0,1500)
  if a < 980: return
  if a == 1000:
    await bot.get_channel(channel_general).send("Le premier à cliquer sur ce bouton remporte 100 pièces !!!",view = Claim_Gift_100())
  if 980 <= a <= 990:
    await bot.get_channel(channel_general).send("Le premier à cliquer sur ce bouton remporte 10 pièces !!!",view = Claim_Gift_10())
  if 990 < a <= 996:
    await bot.get_channel(channel_general).send("Le premier à cliquer sur ce bouton remporte 25 pièces !!!",view = Claim_Gift_25())
  if 996 < a < 1000:
    await bot.get_channel(channel_general).send("Le premier à cliquer sur ce bouton remporte 50 pièces !!!",view = Claim_Gift_50())

@tasks.loop(seconds=10)
async def send_mails():
  await bot.wait_until_ready()
  print("checking new users...")
  check_new_users()



#Run the bot
if __name__ == "__main__":
    for extension in startup_extensions:
      bot.load_extension(extension)

    DeleteOldMessages.start()
    DeleteOldMessagesP4.start()
    CreateBackup.start()
    generate_gift.start()
    DeleteOldMessagesLolClassement.start()
    DeleteOldMessagesArcadeClassement.start()
    send_mails.start()

    bot.run(TOKEN)