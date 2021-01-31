import json

BASE_URL = 'https://cgi.cse.unsw.edu.au/~secsoc/discord'
EMAIL_MANUAL_CC = 'execs@unswsecurity.com'

with open('config/discord.json') as cfg_file:
  discord_cfg = json.loads(cfg_file.read())

DISCORD_CLIENT_ID = discord_cfg['client_id']
DISCORD_CLIENT_SECRET = discord_cfg['client_secret']
DISCORD_ROLES = discord_cfg["roles"]
DISCORD_BOT_TOKEN = discord_cfg["bot_token"]
DISCORD_GUILD = discord_cfg["guild"]