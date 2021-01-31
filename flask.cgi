#!/web/secsoc/discord/venv/bin/python

#!/usr/bin/python
from wsgiref.handlers import CGIHandler
from app import app

CGIHandler().run(app)
