#import--------------------
import os
import secrets

#Tokens-------------------
SECRET_KEY = os.urandom(32)
WTF_CSRF_SECRET_KEY=secrets.token_bytes(32)
WTF_CSRF_CHECK_DEFAULT=False

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

#Server init--------------
#SERVER_NAME = '127.0.0.1:5000'

# Enable debug mode.
DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Connect to the database
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:admin@127.0.0.1:5432/fyuur'
