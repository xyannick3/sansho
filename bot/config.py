import os
import json

from dotenv import load_dotenv
load_dotenv("environment.env")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

def load_settings():
    with open("bot/settings.json","r") as f:
        return json.load(f)
SETTINGS = load_settings()
MODERATOR_ROLE = SETTINGS["moderator_role"]
LOG_CHANNEL = SETTINGS["log_channel"]
SHAME_ROLE = SETTINGS["shame_role"]
MEGASHAME_ROLE = SETTINGS["megashame_role"]
MUTE_ROLE = SETTINGS["mute_role"]
MEMBER_ROLE = SETTINGS["member_role"]
PRESENTATION_ROLE = SETTINGS["presentation_role"]
