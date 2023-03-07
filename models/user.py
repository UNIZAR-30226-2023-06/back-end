from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    coins = Column(Integer, default=0)
    selected_grid_skin = Column(String, default='default')
    selected_pieces_skin = Column(String, default='default')
    saved_music = Column(String, default='default')
    elo = Column(Integer, default=500)
 