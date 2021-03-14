import json


with open('config/discord.json') as cfg_file:
  discord_cfg = json.loads(cfg_file.read())
with open('config/app.json') as cfg_file:
  app_cfg = json.loads(cfg_file.read())

DISCORD_CLIENT_ID = discord_cfg['client_id']
DISCORD_CLIENT_SECRET = discord_cfg['client_secret']
DISCORD_ROLES = discord_cfg["roles"]
DISCORD_BOT_TOKEN = discord_cfg["bot_token"]
DISCORD_GUILD = discord_cfg["guild"]


APP_BASE_URL = app_cfg['base_url']
APP_SERVER_NAME = app_cfg['server_name']
APP_CONTACT_EMAIL = app_cfg['contact_email']
