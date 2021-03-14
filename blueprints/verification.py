import os
import json
import uuid
import re
import config
from functools import reduce
from email.utils import parseaddr
from flask import Blueprint, render_template, redirect, url_for, request
from flask_dance.contrib.discord import discord
from lib.bot import add_roles
from lib.email import send_email

RE_SNOWFLAKE = re.compile(r'[0-9]{16,}')
RE_ZID = re.compile(r'z[0-9]{7}')
RE_PHONE = re.compile(r'04[0-9]{8}')

VALID_SUFFIXES = ['@education.nsw.gov.au', '.edu.au', '@unswalumni.com']

EMAIL_TEMPLATE_AUTO = """Hello {name},

You have requested verification on the {server_name} Discord server. Please follow
the link below in order to gain access to the community.

{verification_url}

If there are any issues, feel free to contact us at {contact_email}.
"""


EMAIL_TEMPLATE_NOAUTO = """Hello {name},

You have requested verification on the {server_name} Discord server. Since you
provided us with a private email and phone number, we will aim to verify you
as soon as possible.

If there are any issues, feel free to contact us at {contact_email}.
"""

BOOL_CONVERT = {
  '0': False,
  '1': True
}

verification_blueprint = Blueprint('verification', __name__)

def check_user_verified(user_id):
  # check if user already exists
  if os.path.exists(f'data/{user_id}'):
    # check if user is already verified
    with open(f'data/{user_id}') as f:
      try:
        return json.loads(f.read()).get('verified', False)
      except:
        return False
  
  return False

# returns a processed form object
def validate_form(form):
  name = form.get('name', '')
  unsw = form.get('unsw', '')
  arc = form.get('arc', '')
  zid = form.get('zid', '')
  email = form.get('email', '')
  phone = form.get('phone', '')

  if not name:
    return False
  
  if unsw not in BOOL_CONVERT:
    return False
  unsw = BOOL_CONVERT[unsw]

  if unsw:
    if arc not in BOOL_CONVERT:
      return False
    arc = BOOL_CONVERT[arc]
    if not re.match(RE_ZID, zid):
      return False

    return {
      'automated': True,
      'type': 'unsw',
      'name': name,
      'unsw': True,
      'arc': arc,
      'zid': zid,
      'email': f'{zid}@ad.unsw.edu.au'
    }

  email = email.lower()
  if parseaddr(email) == ('', ''):
    return False

  automated = reduce(lambda cur, suffix: email.endswith(suffix) or cur, VALID_SUFFIXES, False)
  
  if automated:
    return {
      'automated': True,
      'type': 'assoc',
      'name': name,
      'unsw': False,
      'email': email
    }

  if not re.match(RE_PHONE, phone):
    return False

  return {
    'automated': False,
    'type': 'assoc',
    'name': name,
    'unsw': False,
    'arc': False,
    'email': email,
    'phone': phone
  }


@verification_blueprint.route('/', methods=['GET'])
def get_verification_form():
  if not discord.authorized:
    return redirect(url_for('discord.login'))

  user = discord.get('/api/users/@me').json()
  if check_user_verified(user['id']):
    return 'You are already verified, please contact us if you want to change your details.'

  return render_template('verification.html', server_name=config.APP_SERVER_NAME)

@verification_blueprint.route('/', methods=['POST'])
def post_verification_form():
  if not discord.authorized:
    return redirect(url_for('discord.login'))
  
  user = discord.get('/api/users/@me').json()
  if check_user_verified(user['id']):
    return 'You are already verified, please contact us if you want to change your details.'

  data = validate_form(request.form)
  code = str(uuid.uuid4())

  # TODO: validation
  with open(f'data/{user["id"]}', 'w') as f:
    f.write(json.dumps({
      **data,
      'verified': False,
      'code': code,
      'discord_id': user['id'],
      'discord_name': f'{user["username"]}#{user["discriminator"]}'
    }))
  
  if data['automated']:
    send_email(data['email'], f'{config.APP_SERVER_NAME} Discord Verification', EMAIL_TEMPLATE_AUTO.format(
      name=data['name'],
      server_name=config.APP_SERVER_NAME,
      contact_email=config.APP_CONTACT_EMAIL,
      verification_url=f'{config.APP_BASE_URL}/verification/link/{user["id"]}/{code}'
    ))
  else:
    send_email(data['email'], f'Manual {config.APP_SERVER_NAME} Discord Verification', EMAIL_TEMPLATE_NOAUTO.format(
      name=data['name'],
      server_name=config.APP_SERVER_NAME,
      contact_email=config.APP_CONTACT_EMAIL,
    ), config.APP_CONTACT_EMAIL)

  return 'Please check your email for an activation link.'

@verification_blueprint.route('/link/<discord_id>/<code>', methods=['GET'])
def get_link(discord_id, code):
  # check that discord id is a numeric string
  if not re.match(RE_SNOWFLAKE, discord_id):
    return 'Record Not Found'

  # open file and check if valid
  try:
    with open(f'data/{discord_id}') as f:
      data = json.loads(f.read())
      verified = data.get('verified', False)
      automated = data.get('automated', False)
      m_type = data.get('type', '')
  except:
    return 'Record Not Found'
  
  if data.get('code', '') != code:
    return 'Record Not Found'

  if not automated:
    return 'Please contact us at {config.APP_CONTACT_EMAIL} in order to verify.'

  if verified:
    return 'You are already verified, please contact us if you want to change your details.'

  add_roles(discord_id, config.DISCORD_ROLES[m_type])

  with open(f'data/{discord_id}', 'w') as f:
    f.write(json.dumps({ **data, 'verified': True }))
  
  return 'You have been successfully verified, welcome aboard!'
