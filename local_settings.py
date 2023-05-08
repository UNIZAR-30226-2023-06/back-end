import os

JWT_SECRET = os.getenv('JWT_SECRET')

postgresql = {
    'pguser': os.getenv('PGUSER'),
    'pgpasswd': os.getenv('PGPASSWD'),
    'pgport': os.getenv('PGPORT'),
    'pghost': os.getenv('PGHOST'),
    'pgdb': os.getenv('PGDB')
}
