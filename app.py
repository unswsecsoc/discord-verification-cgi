from flask import Flask
from flask_dance.contrib.discord import make_discord_blueprint
import config
from blueprints.verification import verification_blueprint


app = Flask(__name__)
app.secret_key = 'lol'

discord_blueprint = make_discord_blueprint(
  client_id=config.DISCORD_CLIENT_ID,
  client_secret=config.DISCORD_CLIENT_SECRET,
  scope='identify',
  redirect_to='verification.get_verification_form'
)

app.register_blueprint(discord_blueprint, url_prefix='/oauth')
app.register_blueprint(verification_blueprint, url_prefix='/verification')