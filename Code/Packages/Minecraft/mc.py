from Packages.firebase_database.firebase_database import get_json
import discord
from settings import *
from Packages.firebase_database.firebase_database import *

#variables
message_erroné = "Afin de sauvegarder les coordonées de qqchose, écrit ton message de la forme suivante :\n!mc_set x y z nom_endroit\nPar exemple, si tu veux sauvegarder la position de ta maison, tu dois faire :\n!mc_set 0 64 0 ma maison"
message_confirm = "Le point d'intéret `{0}` de coordonées `{1}`a bien été ajouté !"

def mc_set(message):
    if message.channel.id != mc_channel: return
    if not ("»") in message.content: return
    message_content = message.content.split(" » !mc_set")[1]
    try:
      L = message_content.split(" ",4)
      print(L)
      x = L[1]
      y = L[2]
      z = L[3]
      name = L[4]
      test = int(x)
      test = int(y)
      test = int(z)
    except:
      return message_erroné
    json = get_json("/Minecraft/points_interet")
    json[name] = [x,y,z]
    set_json("/Minecraft/points_interet",json)
    return message_confirm.format(name,str(x)+","+str(y)+","+str(z))

def mc_get():
    json = get_json("/Minecraft/points_interet")
    message = ""
    for key in json.keys():
        message += key + " : " + str(json[key][0]) + " , " + str(json[key][1]) + " , " + str(json[key][2]) + "\n"
    return message
