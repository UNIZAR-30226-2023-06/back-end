import os
from dotenv import load_dotenv

KEYS = ["PGUSER", "PGPASSWD", "PGPORT", "PGHOST", "PGDB", "JWT_SECRET"]

load_dotenv()

config = {key: os.getenv(key) for key in KEYS}

JWT_SECRET = config['JWT_SECRET']

postgresql = {

    'pguser' : config['PGUSER'],
    'pgpasswd' : config['PGPASSWD'],
    'pgport' : config['PGPORT'],
    'pghost' : config['PGHOST'],
    'pgdb' : config['PGDB']
}
