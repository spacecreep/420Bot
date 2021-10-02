#imports
import discord
from discord.ext import commands
from Packages.firebase_database.firebase_database import add_coins, get_json, set_json
from PIL import Image
import io
import random
import collections
from settings import *

#variables
message_combat_puissance_4 = """**Salut {0.mention} et {1.mention} !**

**Vous allez vous affronter au jeu de puissance 4. voici les règles :**
-> Le hasard a décidé que ça serait {2.mention} qui allait commencer à jouer.
-> {3} a les jetons rouges et {4} a les jaunes.
-> Vous jouez chacun votre tour, le premier qui aligne 4 jetons gagne.
-> Vous placez des jetons en cliquant sur les boutons situés sous l'image lorsque c'est votre tour (cliquer sur le bouton lorsque ce n'est pas votre tour est sans effet sur le jeu).
-> Le gagnant repart avec {5} pièces.
-> Si vous souhaitez abandonner, tapez `!surrender`
-> Le salon se supprime automatiquement après 1h d'inactivité, auquel cas chacun regagne sa mise.
-> Si jamais un joueur met plus de 30mn à jouer, l'autre peut faire !report, auquel cas il est immédiatement déclaré gagnant et remporte la mise !

Pour que le jeu soit plus plaisant à jouer, je vous conseille de cliquer sur le `...`en haut à droite du salon, et de cliquer sur `ouvrir en pleine fenêtre`

Le jeu va désormais commencer ! Que le meilleur gagne !

SI JAMAIS UN BUG SE PRESENTE, FAITES LA COMMANDE `!bug` ET VOUS REGAGNEZ VOS PIECES !
"""
puissance4_list = []

#functions and buttons
async def puissance_4_jouer(column,interaction,self):
	#on check si la personne est dans un jeu de puissance 4
	for combat in puissance4_list:
		if interaction.user.id in combat[1] or combat[2]:
			if interaction.channel.id == combat[7]: #c'est le bon channel
				if combat[combat[5]][0] == interaction.user.id: #si c'est bien à lui de jouer
					if combat[6]: return #on vérifie juste par précaution que le jeu n'est pas déjà fini
					thread = self.bot.get_channel(puissance4_channel).get_thread(combat[7])
					win = combat[0].add_token(column,interaction.user.id)
					self.stop() #plus personne ne pourra interagir avec le bouton
					if win: #le joueur a mis un jeton qui l'a fait gagner
						combat[6] = True
						nb_win = 1
						nb_loose = 2
						if combat[2][0] == interaction.user.id:
							nb_win = 2
							nb_loose = 1
						member_json = get_json("Discord Bot/members/" + str(combat[nb_win][1]))
						member_json2 = get_json("Discord Bot/members/" + str(combat[nb_loose][1]))
						member_json["coins"]+=2*combat[3]
						member_json["puissance_4"]["wins"] += 1
						member_json["puissance_4"]["gain total"] += combat[3]
						member_json2["puissance_4"]["looses"] += 1
						member_json2["puissance_4"]["gain total"] -= combat[3]
						set_json("Discord Bot/members/" + str(combat[nb_win][1]),member_json)
						set_json("Discord Bot/members/" + str(combat[nb_loose][1]),member_json2)
						with io.BytesIO() as image_binary:
							combat[0].get_grid().save(image_binary,'PNG')
							image_binary.seek(0)
							await thread.send(file = discord.File(fp = image_binary, filename='image.png'))
						await interaction.response.send_message(interaction.user.name + " a gagné !!!\nTu remportes ta mise, ainsi que celle de ton adversaire, soit un total de " + str(2*combat[3]) + " pièces !!!\nFaites !close pour fermer le salon !")
					else:#le jeu continue normalement

						with io.BytesIO() as image_binary:
							combat[0].get_grid().save(image_binary,'PNG')
							image_binary.seek(0)
							await thread.send(file = discord.File(fp = image_binary, filename='image.png'))
					
						if combat[5] == 1:
							combat[5] = 2
						else:
							combat[5] = 1
					
						a_qui_de_jouer = self.bot.get_user(combat[combat[5]][0])
						
						await thread.send("C'est à " + a_qui_de_jouer.name + " de jouer",view = Puissance_4_Buttons(self.bot))

				else:
					await interaction.response.send_message("ce n'est pas à toi de jouer !",ephemeral = True)

class BUG(discord.ui.View):
	def __init__(self,bot):
		super().__init__()
		self.bot = bot
	
	@discord.ui.button(label="Je suis d'accord",style=discord.ButtonStyle.danger)
	async def BUG_(self, button: discord.ui.button, interaction: discord.Interaction):
		for combat in puissance4_list:
			nb = 0
			if interaction.user.id in combat[1]:
				nb = 1
			if interaction.user.id in combat[2]:
				nb = 2
			if nb>0:
				if combat[7] != interaction.channel_id: return #Ce n'est pas la bonne personne
				if combat[nb][2]: return await interaction.response.send_message("C'est pas à toi de cliquer dessus!",ephemeral=True)
				add_coins(combat[1][0],combat[3])
				add_coins(combat[2][0],combat[3])
				combat[6] = True
				await interaction.response.send_message("Vos pièces vous ont été rendues !\nNous sommes sincèrement désolés pour la gène occasionée, le jeu de puissance 4 n'est pas encore parfait et présente quelques bugs.\nVous pouvez maintenant faire !close pour fermer cette partie !")
				self.stop()

class Puissance_4_Buttons(discord.ui.View):
	def __init__(self,bot):
		super().__init__()
		self.bot = bot
		self.timeout = 70000

	@discord.ui.button(label='1', style=discord.ButtonStyle.green)
	async def button_1(self, button: discord.ui.Button, interaction: discord.Interaction):
		await puissance_4_jouer(1,interaction,self)

		# This one is similar to the confirmation button except sets the inner value to `False`
	@discord.ui.button(label='2', style=discord.ButtonStyle.grey)
	async def button_2(self, button: discord.ui.Button, interaction: discord.Interaction):
		await puissance_4_jouer(2,interaction,self)
	
	@discord.ui.button(label='3', style=discord.ButtonStyle.green)
	async def button_3(self, button: discord.ui.Button, interaction: discord.Interaction):
		await puissance_4_jouer(3,interaction,self)

		# This one is similar to the confirmation button except sets the inner value to `False`
	@discord.ui.button(label='4', style=discord.ButtonStyle.grey)
	async def button_4(self, button: discord.ui.Button, interaction: discord.Interaction):
		await puissance_4_jouer(4,interaction,self)
	
	@discord.ui.button(label='5', style=discord.ButtonStyle.green)
	async def button_5(self, button: discord.ui.Button, interaction: discord.Interaction):
		await puissance_4_jouer(5,interaction,self)

		# This one is similar to the confirmation button except sets the inner value to `False`
	@discord.ui.button(label='6', style=discord.ButtonStyle.grey)
	async def button_6(self, button: discord.ui.Button, interaction: discord.Interaction):
		await puissance_4_jouer(6,interaction,self)
	
	@discord.ui.button(label='7', style=discord.ButtonStyle.green)
	async def button_7(self, button: discord.ui.Button, interaction: discord.Interaction):
		await puissance_4_jouer(7,interaction,self)

		# This one is similar to the confirmation button except sets the inner value to `False`
	@discord.ui.button(label='8', style=discord.ButtonStyle.grey)
	async def button_8(self, button: discord.ui.Button, interaction: discord.Interaction):
		await puissance_4_jouer(8,interaction,self)


#game
class puissance4:
	def __init__(self,player1,player2):
		self.player1 = player1
		self.player2 = player2
		self.lines = [[0,0,0,0,0,0,0,0] for k in range(6)]
		self.image_empty = Image.open('Packages/Puissance4/empty.png')
		self.image_p1 = Image.open("Packages/Puissance4/red.png")
		self.image_p2 = Image.open("Packages/Puissance4/yellow.png")
	def get_grid(self):
		new_image = Image.new('RGB',(8*self.image_empty.size[0], 6*self.image_empty.size[1]), (250,250,250))
		for k in range(6):
			for l in range(8):
				if self.lines[k][l] == 0:
					new_image.paste(self.image_empty,(self.image_empty.size[0] * l,self.image_empty.size[0] * k))
				elif self.lines[k][l] == 1:
					new_image.paste(self.image_p1,(self.image_empty.size[0] * l,self.image_empty.size[0] * k))
				elif self.lines[k][l] == 2:
					new_image.paste(self.image_p2,(self.image_empty.size[0] * l,self.image_empty.size[0] * k))
		return new_image

	def add_token(self,column,player):
		#caca
		if column > 8 or column < 1: return "Colonne invalide"
		if player != self.player1 and player != self.player2: return("Ce joueur ne joue pas !")
		#who is playing?
		if player == self.player1:
			var = 1
		else:
			var = 2
		#Check if the column chosen is full
		if self.lines[0][column - 1] !=  0:
			return("Cette colonne est pleine !")
		#Add the token to the correct column
		line = 6
		for k in range(len(self.lines)):
			if self.lines[k][column - 1] == 0:
				line = 6 - k
		self.lines[6 - line][column - 1] = var
		#After the person played, we need to check if it completes a row of 4 tokens
		return self.check_win([column - 1,6 - line])

	def check_win(self,coord):
		# Check horizontal locations for win
		for c in range(5):
			for r in range(6):
				if self.lines[r][c] == self.lines[r][c+1] == self.lines[r][c+2] == self.lines[r][c+3] != 0:
					return True

		# Check vertical locations for win
		for c in range(8):
			for r in range(6-3):
				if self.lines[r][c] == self.lines[r+1][c] == self.lines[r+2][c] == self.lines[r+3][c] != 0:
					return True

		# Check positively sloped diaganols
		for c in range(8-3):
			for r in range(6-3):
				if self.lines[r][c] == self.lines[r+1][c+1] == self.lines[r+2][c+2] == self.lines[r+3][c+3] != 0:
					return True

		# Check negatively sloped diaganols
		for c in range(8-3):
			for r in range(3, 6):
				if self.lines[r][c] == self.lines[r-1][c+1] == self.lines[r-2][c+2] == self.lines[r-3][c+3] != 0:
					return True
		return False

#commands cog
class p4(commands.Cog):
	def __init__(self,bot):
		self.bot = bot
	
	@commands.command(name = "fight")
	async def fight(self,ctx):
		if ctx.channel.id == puissance4_channel:
			#si jamais il n'a pas mentionné son opposant
			if "<@!" and ">" not in ctx.message.content:
				return await ctx.send("Ton message doit être de la forme `!fight @ton_opposant mise`")
			L = ctx.message.content.split(" ",2)
			try:
				opponent_id = int(L[1].replace("<@!","").replace(">",""))
			except: return await ctx.send("Ton message doit être de la forme `!fight @ton_opposant mise`")

			#check de la mise
			try:
				mise = int(L[2])
			except: return await ctx.send("Ton message doit être de la forme `!fight @ton_opposant mise`")

			#mise positive?
			if mise <= 0: return await ctx.send("Tu casses les couilles la gros, rentre une mise positive")

			#check de si la personne désignée est un membre
			members_json = get_json("Discord Bot/members")

			nb_1 = -1
			nb_2 = -1
			for k in range(len(members_json)):
				if members_json[k]["id"] == opponent_id:
					nb_2 = k
				if members_json[k]["id"] == ctx.author.id:
					nb_1 = k
			
			if nb_1<0: return await ctx.send("Crée toi un compte de membre pour pouvoir jouer !")
			if nb_2<0: return await ctx.send("La personne que tu souhaites affronter n'a pas créé de compte membre !")

			#on import les deux json
			member_1_json = get_json("Discord Bot/members/" + str(nb_1))
			member_2_json = get_json("Discord Bot/members/" + str(nb_2))

			#on check si ils ont les thunasses ou pas
			if mise > member_1_json["coins"]: return await ctx.send("Tu n'as pas assez d'argent pour pouvoir en miser autant !")
			if mise > member_2_json["coins"]: return await ctx.send("La personne que tu souahaites affronter n'a pas suffisamment d'argent !")

			#check de si le gars est pas déjà dans une game
			for combat in puissance4_list:
				if ctx.author.id in combat[1] or combat[2]:
					return await ctx.send("T'as déjà un match en cours fréro !")
			
			#on update leurs nb de games jouées
			if not "puissance_4" in member_1_json.keys():
				member_1_json["puissance_4"] = {"wins":0,"looses":0,"gain total":0}
			if not "puissance_4" in member_2_json.keys():
				member_2_json["puissance_4"] = {"wins":0,"looses":0,"gain total":0}
			
			set_json("Discord Bot/members/" + str(nb_1),member_1_json)
			set_json("Discord Bot/members/" + str(nb_2),member_2_json)

			#ils ont les thunes, on lance le jeu
			game = puissance4(ctx.author.id,opponent_id)
			puissance4_list.append([game,[ctx.author.id,nb_1,False],[opponent_id,nb_2,False],mise,False,random.choice([1,2]),False])

			message = await ctx.send("{0.mention}, ya ".format(self.bot.get_user(opponent_id)) + "{0.mention} qui te défie au puissance 4 pour **".format(ctx.author) + str(mise) + " pièces **!!! Réagis à ce message pour accepter ou décliner l'invitation !")
			await message.add_reaction("✔️")
			await message.add_reaction("❌")
			return
			
		return await ctx.send("Cette commande ne sert à rien dans ce channel !")

	@commands.command(name = "report")
	async def report(self,ctx):
  		await ctx.send("Désolé mais mes développeurs n'ont pas encore setup le système des signalements ! À la place, je t'invite à prendre un screen du channel et de l'envoyer à un admin afin qu'il applique la punition !")

	@commands.command(name = "close")
	async def close(self,ctx):
		for combat in puissance4_list:
			if (ctx.author.id in combat[1] or combat[2]) and combat[6]==True:
				puissance4_list.remove(combat)
				messages = await self.bot.get_channel(puissance4_channel).history().flatten()
				for message in messages:
					if str(combat[1][0]) and str(combat[2][0]) in message.content:
						await message.delete()
				await self.bot.get_channel(puissance4_channel).get_thread(combat[7]).delete()
	
	@commands.command(name = "bug")
	async def bug(self,ctx):
		for combat in puissance4_list:
			nb = 0
			if combat[1][0] == ctx.author.id:
				nb = 1
			if combat[2][0] == ctx.author.id:
				nb = 2
			if nb>0:
				if ctx.channel.id != combat[7]: return
				if combat[6]: return await ctx.send("La partie est déjà finie !") #on évite que des joueurs puissent déclarer un bug à la fin de la game et donc toucher plus de sous
				combat[nb][2] = True
				await ctx.send(ctx.author.name + " déclare qu'il y a un bug dans le jeu, est-tu d'accord avec lui ?",view = BUG(self.bot))

	@commands.Cog.listener()
	async def on_reaction_add(self,reaction,user):
		if reaction.emoji in ["✔️","❌"]: #peut être pour un combat?
			if reaction.message.channel.id == puissance4_channel and reaction.message.author == self.bot.user: #ya de très fortes chances pour que ce soit pour un combat
				if "pièces **!!! Réagis à ce message pour accepter ou décliner l'invitation !" in reaction.message.content:#combat de puissance 4
					if reaction.message.content.startswith("<@" + str(user.id) + ">"): #c'est la bonne personne qui a réagi
						#now we get the id of the one who sent the !fight message
						L = reaction.message.content.split(" ",5)
						id = int(L[2].replace("<@","").replace(">",""))

						#we check if the match has already started
						for combat in puissance4_list:
							if combat[1][0] == id and combat[2][0] == user.id:
								if not combat[4]: #we have to start a match
									if reaction.emoji == "❌":
										puissance4_list.remove(combat)
										return await reaction.message.channel.send("{0.mention} a refusé le combat proposé par {1.mention} !!!".format(user,self.bot.get_user(id)))
						
						#check de si le gars est pas déjà dans une game
						for combat in puissance4_list:
							if user.id in combat[1] or combat[2] and combat[4]==True:
								return await reaction.message.channel.send("T'as déjà un match en cours fréro !")
						
						#on prend les données des membres et on retire les thunes
						json_1 = get_json("Discord Bot/members/" + str(combat[1][1]))
						json_2 = get_json("Discord Bot/members/" + str(combat[2][1]))

						if json_1["coins"] < combat[3]: return await reaction.message.send("Ah merde, on dirait bien que " + self.bot.get_user(id).name + " n'a plus assez de thunes pour pouvoir miser " + str(combat[3]) + " pièces !")
						if json_2["coins"] < combat[3]: return await reaction.message.send("Ah merde, on dirait bien que " + user.name + " n'a plus assez de thunes pour pouvoir miser " + str(combat[3]) + " pièces !")

						json_1["coins"] -= combat[3]
						json_2["coins"] -= combat[3]

						set_json("Discord Bot/members/" + str(combat[1][1]),json_1)
						set_json("Discord Bot/members/" + str(combat[2][1]),json_2)

						message = await reaction.message.channel.send("{0.mention} et {1.mention} vont s'affronter au puissance 4 !!! Il y a une mise de ".format(user,self.bot.get_user(id)) + str(combat[3]) + " pièces en jeu !")
						thread = await message.create_thread(name = user.name + " VS " + self.bot.get_user(id).name,
						auto_archive_duration = 60)
						combat.append(thread.id)
						combat[4] = True
						


						celui_qui_commence = user
						celui_qui_commence_pas = self.bot.get_user(id)
						if combat[5] == 1:
							celui_qui_commence = self.bot.get_user(id)
							celui_qui_commence_pas = user

						await thread.send(message_combat_puissance_4.format(user,self.bot.get_user(id),celui_qui_commence,celui_qui_commence.name,celui_qui_commence_pas.name,combat[3]))
						
						with io.BytesIO() as image_binary:
							combat[0].get_grid().save(image_binary,'PNG')
							image_binary.seek(0)
							await thread.send(file = discord.File(fp = image_binary, filename='image.png'))
						
						await thread.send("C'est à " + celui_qui_commence.name + " de jouer",view = Puissance_4_Buttons(self.bot))
						print(combat)

def setup(bot):
	bot.add_cog(p4(bot))