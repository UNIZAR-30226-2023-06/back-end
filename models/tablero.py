from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


# ! AÚN FALTA PROBARLAS Y VER SI FUNCIONAN

class Tablero(Base):
    __tablename__ = 'tableros'
    id = Column(Integer, primary_key=True, autoincrement=True)
    board_distribution = Column(String)

class Board_Skins(Base):
    __tablename__ = 'board_skins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    image = Column(String)
    description = Column(String)

class Pieces_Skins(Base):
    __tablename__ = 'pieces_skins'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    image = Column(String)
    description = Column(String)


# ! #######################################################################