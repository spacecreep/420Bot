import firebase_admin
from firebase_admin import db

#setup
json = {
  "type": "service_account",
  "project_id": "gaming-53505",
  "private_key_id": "1b5f310906234f772f50f3baf28b8742bdae2e23",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDfM5SaMeky6jVL\n3KaeELGBdLX7F9LWEwmZsPi8OWrtl1KpZ0tuZ7iF6EgQ8WOmB0Sn89IxGv/pFPw3\ngwIGk2zC03zAY8hfMXUN3FxN3EJIjg1h/5xNXDBbzfXYKCbzm12bMResJF2hxtN0\n26yB8+yf1PJqasjIee7UnPoHrah61XzpMbXIFxUl4huCTvAQIMmTpF3zdl47yjk/\nsWVwWPGx77fZcrGYAB70FsO5lhzhqEqBS9XWFfz4ZYk7dEKFLmG3hZb16PIX1hIF\n7cKLWuuFOnCVjtJ1WF8rXk78Rw7Cn0YyjLCfqocCQ3CuHQX4UNUbi0E6WyJThDBT\nf2tP8pjjAgMBAAECggEABlT53wxeoTy9TLmlwGlln7zzExYWu4Jh81cIUQHcyecd\n4TbQKc50RAtvsyTyvr/WCS23+MyoFeSsHKcKyt6QmoMfA6/Q/C8nzIzdaxgK772X\n6f/Mxb6nxvL0CbEAUEjhqIifM0yUzp7lWmgg+YIB/hOWDPU0KciYjekmIeTU5fPu\nInUIPy2HSabw+LsxN4rPzum+AgCS53Z/5uCOtC4ARSY8X/65k9hRLc2Ot55sVZ/S\nwq9M89K54pUWbgEBd3Jc7nF+BOctgnwmzJ+ZnEipnG0BpyI7Q+mBzSrYU75Xqdjv\n8R501bLiSA23Kxo/2I/V+92uOQ9/CDLBQTOr8GlKAQKBgQD2QwjWg7z/4zODEbPl\nsePjHRBNp3IZVb4GNkR4wlLva0wQTCWaQLGm3Ov0if/ha/fql0dHWouBlwEK6M30\nl+rIznddULYvZDM0WdM/YkyoOWoOBa1H7NK+de3pJxL0E2+MWstysXusKq6TTpFU\neuetDqp83cPtoyaeJn9LwOcI0QKBgQDoBxm9M0D1bap9KqJ7q+SlO/uXtma7o/tS\nrpg30Geng97toj6N9FjK9y0NCoclwK7HjhXKatd3H+G12xlhCA4ev2nrqAH1zhCf\nqJQlbz3rWlMSrjCFuMYNgQbGFQ5nGw42ea7MHng4gorWblTe7V848e+uSKLelwEP\npe7kZOgzcwKBgQD0A8p/HPyrJcuGJYV3pcRk6AiembwChKaNazp/2jXpzQ0K3Rkp\nds9Rw3j+z7s/+AcpagsUFhFEMIe08qgZpGrd3VADpBVSclwWlKcxGEtTKcj/6fog\n2fadCSfcLn6mYZfXoKQVmu4r1AM2LdTtu/dS0MR4hBo/n7mFXiomuxdy8QKBgCGI\n5S9zOPA/6WQtxU4aifFXugUzV6XHDYvlsBphBJoxdQbjbCcYKb0r/FbmLqJGNvyg\njIW0629MLFMcV46um1vWTnjAz4e3QK/SrZa7fTeG1nrcsiahjf5lp5T5dhtwzZ0R\n+TGHNdj1BRv41ktiA2E3lmyaEvAY4w5f7ScVbnoBAoGADtW0VMesfHCuHqYTqXBT\nvuV9AZJTs+Yfb1zJNeA9jTjqYFfLhfnC1c2M5jAzQ2xnu1QU5hGU/EGI1vQqQTWg\nE3AQ4OBOnJTgaer2IlBr00DP9D9olHo8noc6cyIqgPPItw0qjQJcYBFh1zOsaHmg\nf2lYIbig0tXB0qS5ZxjCf28=\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-34vau@gaming-53505.iam.gserviceaccount.com",
  "client_id": "114203187689619090171",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-34vau%40gaming-53505.iam.gserviceaccount.com"
}


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