import firebase_admin
from firebase_admin import db





cred_obj = firebase_admin.credentials.Certificate(json)
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':"https://gaming-53505-default-rtdb.europe-west1.firebasedatabase.app/"
	})

#functions
def get_json(reference):
    ref = db.reference(reference)
    json = ref.get()
    return json

def set_json(reference,content):
    ref = db.reference(reference)
    ref.set(content)

def is_member(id):
    ref = db.reference("Discord Bot/members")
    members = ref.get()
    nb = -1
    for k in range(len(members)):
        if members[k]["id"] == id:
            nb = k
    return nb

def add_coins(id,nb):
    check = is_member(id)
    if check<0: return False
    ref = db.reference("Discord Bot/members/" + str(check))
    member = ref.get()
    member["coins"] += nb
    ref.set(member)
    return True

def add_element(reference,content):
    ref = db.reference(reference)
    ref.update(content)
