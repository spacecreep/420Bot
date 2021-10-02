from flask import Flask
from threading import Thread

app = Flask('weed_bot')

@app.route('/')
def main():
    return "Hello. I am alive!"

def run():
  app.run("0.0.0.0")

def keep_alive():
    t = Thread(target=run)
    t.start()