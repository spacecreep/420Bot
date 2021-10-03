from settings import get_time
import smtplib
from email.message import EmailMessage
from Packages.firebase_database.firebase_database import get_json,set_json,is_member
from datetime import datetime

smtp = smtplib.SMTP_SSL('smtp.hostinger.com', 465)
smtp.login('contact@420gaming.fr', 'Iksniprak12')
from_addr = "contact@420gaming.fr"

msg = """Merci d'avoir créé ton compte {0} !
Pour pouvoir l'utiliser, tu dois tout d'abord vérifier ton compte en cliquant sur le lien ci-dessous, et en entrant ton code d'activation : {1}
https://www.420gaming.fr/Vérification.html"""

def send_mail(to_addr,name,code):
    message = EmailMessage()
    message.set_content(msg.format(name,code))
    message["Subject"] = "Création de ton compte 420gaming"
    message["From"] = from_addr
    message["To"] = to_addr
    smtp.send_message(message)

def check_new_users():
    users = get_json("420gaming/users")
    for key in users.keys():
        if users[key]["need_verif"] and not users[key]["email_sent"]:
            user = get_json("420gaming/users/" + key)
            send_mail(user["email"],user["prénom"],user["verif_number"])
            user["email_sent"] = True
            set_json("420gaming/users/"+key,user)

