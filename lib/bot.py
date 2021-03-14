import requests
import config
import sys

BASE_URL = 'https://discord.com/api'

session = requests.Session()
session.headers.update({'authorization': f'Bot {config.DISCORD_BOT_TOKEN}'})


def add_roles(user_id, roles):
  url = f'{BASE_URL}/guilds/{config.DISCORD_GUILD}/members/{user_id}/roles'
  for role in roles:
    resp = session.put(f'{url}/{role}')
    if resp.status_code != 204:
      print("api error:", resp.text, file=sys.stdout)
      raise Exception
