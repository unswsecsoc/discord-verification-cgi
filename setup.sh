#!/bin/bash

cp -r config.sample/ config/
mkdir data
openssl rand -base64 32 > .flask_key

chmod 700 config data .flask_key