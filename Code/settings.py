import pytz
from datetime import datetime
import random
################################ SETTINGS ###############################################

RiotKey = "RGAPI-a65424c1-2e67-44b0-97f5-0179453c3f5e"
riotApiRegion = 'euw1'
TOKEN = 'ODY0OTYyMDYxNDM5NDY3NTcw.YO9EsQ.0yeuuUzh0b7eXhY3cuab9JzFtkU'


#The list of the keys that needs name (with the {} symbol)
keys_that_needs_name = ["join_msg","leave_msg"]

#Channel variables
channel_general = 859045090956410911
channel_bot_settings = 843101125971935243
membres_accueil = 846625724948676658
slot_machine_channel = 862040208789602364
lol_accueil = 859206809712853072
lol_boutique = 859208596448739328
boutique_commandes = 861354474239688704
mc_channel = 855507328571670548
puissance4_channel = 872057042901295124
calcul_mental_channel = 872064250242273290
rl_accueil_channel = 871018297771057172
lol_bot_channel = 880769698634006608
lol_classement_channel = 882391956662140938
arcade_classement_channel = 883126302700355594
membre_boutique = 858862463026331648
rl_bot_channel = 880770159520940063

#role variables
member_role = 846624730118750219
fortwenirole = 842882705402363915

#user variables
romain = 266207977487335425

#timezone
timeZone = "Europe/Paris"
time_paris = pytz.timezone(timeZone)

#message d'activité
messageActivité = "manger son caca"

#functions
def get_time():
    datetime_Paris = datetime.now(time_paris)
    return datetime.now(time_paris)

def get_random_code():
    L = ["a","z","e","r","t","y","u","i","o","p","q","s","d","f","g","h","j","k","l","m","w","x","c","v","b","n","1","2","3","4","5","6","7","8","9","0"]
    num_commande = ""
    for k in range(10):
        num_commande += random.choice(L)
    return num_commande

