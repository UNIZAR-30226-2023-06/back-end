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
    profile_picture = Column(String, default='default')
 

# ! AÚN FALTA PROBARLAS Y VER SI FUNCIONAN

class Befriends(Base):
    __tablename__ = 'befriends'

    request_status = Column(String)
    user_id = Column(Integer, primary_key=True)
    friend_id = Column(Integer, primary_key=True)

class Has_Board_Skin(Base):
    __tablename__ = 'has_board_skin'

    # user_ id and board_skin_id are the primary keys and foreign keys
    user_id = Column(Integer, primary_key=True)
    board_skin_id = Column(Integer, primary_key=True)

class Has_Pieces_Skin(Base):
    __tablename__ = 'has_pieces_skin'

    # user_ id and pieces_skin_id are the primary keys and foreign keys
    user_id = Column(Integer, primary_key=True)
    pieces_skin_id = Column(Integer, primary_key=True)

# ! #######################################################################