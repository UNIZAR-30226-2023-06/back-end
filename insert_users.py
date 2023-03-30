
import random

from models.tablero import Board_Skins, Pieces_Skins
from models.user import Befriends, User

from werkzeug.security import generate_password_hash

from db import get_engine_from_settings
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

engine = get_engine_from_settings()
Session = sessionmaker(bind=engine)
session = Session()

def insertUsers(num):
    for i in range(num):
        user_id = random.randint(1000, 9999)
        while session.query(User).filter_by(id=user_id).first() is not None:
            user_id = random.randint(1000, 9999)
        username = "user"+str(i)
        email = username + "@gmail.com"
        if session.query(User).filter_by(email=email).first() is not None:
            print("Email already exists: " + email)
            continue

        password = "1234"
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(id=user_id, username=username, email=email, password=hashed_password)
        session.add(new_user)
        session.commit()
        print("User created: " + username + "email: " + email + "password: "  + password)

def insertBoardSkins(num):
    for i in range(num):
        skin_id = i
        while session.query(Board_Skins).filter_by(id=skin_id).first() is not None:
            skin_id += 1
        skin_name = "skin"+str(i)
        skin_image = "skin"+str(i)+".png"
        skin_description = "skin"+str(i)+" description"
        price = random.randint(50, 200)
        new_skin = Board_Skins(id=skin_id, name=skin_name, image=skin_image, description=skin_description, price=price)
        session.add(new_skin)
        session.commit()
        print("Skin created: " + skin_name + "image: " + skin_image + "description: "  + skin_description)

def insertPiecesSkins(num):
    for i in range(num):
        skin_id = i
        while session.query(Pieces_Skins).filter_by(id=skin_id).first() is not None:
            skin_id += 1
        skin_name = "skin"+str(i)
        skin_image = "skin"+str(i)+".png"
        skin_description = "skin"+str(i)+" description"
        price = random.randint(50, 200)
        new_skin = Pieces_Skins(id=skin_id, name=skin_name, image=skin_image, description=skin_description, price=price)
        session.add(new_skin)
        session.commit()
        print("Skin created: " + skin_name + "image: " + skin_image + "description: "  + skin_description)

def insertFriends():
    user1 = session.query(User).filter_by(email="user1@gmail.com").first()
    user2 = session.query(User).filter_by(email="user2@gmail.com").first()
    user3 = session.query(User).filter_by(email="user3@gmail.com").first()
    user4 = session.query(User).filter_by(email="user4@gmail.com").first()
    user5 = session.query(User).filter_by(email="user5@gmail.com").first()
    new_Friendship = Befriends(request_status=True, user_id=user1.id, friend_id=user2.id)
    session.add(new_Friendship)
    new_Friendship = Befriends(request_status=True, user_id=user2.id, friend_id=user3.id)
    session.add(new_Friendship)
    new_Friendship = Befriends(request_status=True, user_id=user3.id, friend_id=user4.id)
    session.add(new_Friendship)
    new_Friendship = Befriends(request_status=True, user_id=user4.id, friend_id=user5.id)
    session.add(new_Friendship)
    new_Friendship = Befriends(request_status=True, user_id=user5.id, friend_id=user1.id)
    session.add(new_Friendship)
    new_Friendship = Befriends(request_status=True, user_id=user1.id, friend_id=user3.id)
    session.add(new_Friendship)
    new_Friendship = Befriends(request_status=True, user_id=user2.id, friend_id=user4.id)
    session.commit()


def poblarTodo():
    insertUsers(10)
    insertBoardSkins(5)

    # Reiniciar la secuencia de autoincremento
    session.execute(text("ALTER SEQUENCE public.board_skins_id_seq RESTART WITH 5;"))

    insertPiecesSkins(5)
    #alter table pieces_skins AUTO_INCREMENT = 5;
    session.execute(text("ALTER SEQUENCE public.piece_skins_id_seq RESTART WITH 5;"))
    insertFriends()

if __name__ == "__main__":
    poblarTodo()