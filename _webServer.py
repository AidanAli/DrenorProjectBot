from fastapi import FastAPI
from threading import Thread
from configparser import ConfigParser
import uvicorn

config = ConfigParser()
config.read('config.ini')

# Config.ini WebServerSettings
host = config["WebServerSettings"]['host']

app = FastAPI()

@app.get("/")
async def home():
    return {"message": "ArcheRage Events Bot 🟢"}

def run():

    uvicorn.run(app, host=host, port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
