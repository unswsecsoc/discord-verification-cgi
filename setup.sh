#!/bin/bash

if [[ ! $PWD =~ "/public_html" ]]; then
   echo "please clone this to a folder inside public_html" 1>&2
   exit 1
fi

WEB_PATH=`echo "$PWD" | sed -e "s/^.*\/public_html/\/web\/$USER/"`
ROOT_URL=`echo "$PWD" | sed -e "s/^.*\/public_html\///"`

cp -r config.sample/ config/
mkdir -p data
openssl rand -base64 32 > .flask_key

chmod 700 config data .flask_key

# generate htaccess
cat << EOF > .htaccess
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteRule ^(.*)$ /~$USER/$ROOT_URL/flask.cgi/\$1
EOF

chmod 644 .htaccess

# install venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# generate flask cgi
cat << EOF > flask.cgi
#!$WEB_PATH/venv/bin/python
from wsgiref.handlers import CGIHandler
from app import app

CGIHandler().run(app)
EOF

chmod 750 flask.cgi
chmod 751 .
