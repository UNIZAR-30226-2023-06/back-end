from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy_utils import database_exists
from local_settings import postgresql as settings

def get_engine(user, passwd, host, port, db):
    url = f"postgresql://{user}:{passwd}@{host}:{port}/{db}"
    engine = create_engine(url, pool_size=50, echo=False)
    return engine

def get_engine_from_settings():
    keys = ['pguser', 'pgpasswd', 'pghost', 'pgport', 'pgdb']
    if not all(key in keys for key in settings.keys()):
        raise Exception('Bad configuration file')

    return get_engine(settings['pguser'],
                      settings['pgpasswd'],
                      settings['pghost'],
                      settings['pgport'],
                      settings['pgdb'])

def get_session():
    engine = get_engine_from_settings()
    session = sessionmaker(bind=engine)
    return session()



# from sqlalchemy.orm import sessionmaker

# engine = get_engine_from_settings()
# Session = sessionmaker(bind=engine)
# session = Session()

# if __name__ == '__main__':
#     # Query all users
#     users = session.query(User).all()
#     #prints all the info the query returns
#     for user in users:
#         print(user.id, user.username, user.email, user.password)

#     # Query a user by id
#     user = session.query(User).filter_by(id=1).first()

#     # Query users by email
#     users = session.query(User).filter_by(email='user@example.com').all()

#     # Query users by username and password
#     users = session.query(User).filter_by(username='user', password='password').all()
    