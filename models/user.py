from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, Integer, String

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
    is_banned = Column(Boolean, default=False)
    profile_picture = Column(String, default='default')
    elo = Column(Integer, default=500)
    profile_picture = Column(String, default='default')
 

class Befriends(Base):
    __tablename__ = 'befriends' 

    request_status = Column(Boolean, default=False)
    user_id = Column(Integer, primary_key=True)
    friend_id = Column(Integer, primary_key=True)

class Has_Board_Skin(Base):
    __tablename__ = 'has_board_skins'

    # user_ id and board_skin_id are the primary keys and foreign keys
    user_id = Column(Integer, primary_key=True)
    board_skin_id = Column(Integer, primary_key=True)

class Has_Pieces_Skin(Base):
    __tablename__ = 'has_piece_skins'

    # user_ id and pieces_skin_id are the primary keys and foreign keys
    user_id = Column(Integer, primary_key=True)
    pieces_skin_id = Column(Integer, primary_key=True)

class Has_Profile_Picture(Base):
    __tablename__ = 'has_profile_pictures'

    # user_ id and profile_picture_id are the primary keys and foreign keys
    user_id = Column(Integer, primary_key=True)
    profile_picture_id = Column(Integer, primary_key=True)

