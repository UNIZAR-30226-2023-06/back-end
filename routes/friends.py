import jwt

from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from local_settings import  JWT_SECRET

from routes.auth import oauth2_scheme
from routes.auth import session

from models.user import User, Befriends

router = APIRouter()


#route for sending a friend request
@router.post("/send_friend_request", tags=["friends"])
def send_friend_request(friend_id: int, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the friend_id exists in the database
        if session.query(User).filter(User.id == friend_id).first() is None:
            raise HTTPException(status_code=404, detail="User not found")
        #search whether the friend request already exists
        elif session.query(Befriends).filter(Befriends.user_id == user_id, Befriends.friend_id == friend_id).first() is not None:
            raise HTTPException(status_code=409, detail="Friend request already exists")
        #search whether the friend request already exists
        elif session.query(Befriends).filter(Befriends.friend_id == user_id, Befriends.friend_id == friend_id).first() is not None:
            raise HTTPException(status_code=409, detail="Friend request already exists")
        else:
            #add the friend request to the database
            session.add(Befriends(request_status=False, user_id=user_id, friend_id=friend_id))
            session.commit()
            return {"detail": "Friend request sent"}
        
#route for accepting a friend request
@router.post("/accept_friend_request", tags=["friends"])
def accept_friend_request(requester_id: int, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the requester_id exists in the database and whether the friend request exists
        if session.query(User).filter(User.id == requester_id).first() is None:
            raise HTTPException(status_code=404, detail="User not found")
        elif session.query(Befriends).filter(Befriends.user_id == requester_id, Befriends.friend_id == user_id).first() is None:
            raise HTTPException(status_code=404, detail="Friend request not found")
        else:
            #update the friend request in the database
            session.query(Befriends).filter(Befriends.user_id == requester_id, Befriends.friend_id == user_id).update({Befriends.request_status: True})
            session.commit()
            return {"detail": "Friend request accepted"}
        
#route for rejecting a friend request
@router.post("/reject_friend_request", tags=["friends"])
def reject_friend_request(requester_id: int, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the requester_id exists in the database and whether the friend request exists
        if session.query(User).filter(User.id == requester_id).first() is None:
            raise HTTPException(status_code=404, detail="User not found")
        elif session.query(Befriends).filter(Befriends.user_id == requester_id, Befriends.friend_id == user_id).first() is None:
            raise HTTPException(status_code=404, detail="Friend request not found")
        else:
            #delete the friend request from the database
            session.query(Befriends).filter(Befriends.user_id == requester_id, Befriends.friend_id == user_id).delete()
            session.commit()
            return {"detail": "Friend request rejected"}
        
#route for getting all friend requests
@router.put("/get_friend_requests", tags=["friends"])
def get_friend_requests(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #get all friend requests from the database
        friend_requests = session.query(Befriends).filter(Befriends.friend_id == user_id, Befriends.request_status == False).all()
        #gets the username of all the users who sent the friend requests
        friend_request_usernames = [session.query(User).filter(User.id == friend_request.user_id).first().username for friend_request in friend_requests]
        #create a list of dictionaries with the friend requests
        friend_requests_list = []
        for friend_request in friend_requests:
            friend_requests_list.append({"requester_id": friend_request.user_id, "requester_name": friend_request_usernames[friend_requests.index(friend_request)]})
        number_of_friend_requests = len(friend_requests_list)
        return {"friend_requests": friend_requests_list, "number_of_requests": number_of_friend_requests, "detail": "Friend requests retrieved"}
    
#route for getting all friends
@router.put("/get_friends", tags=["friends"])
def get_friends(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #get all friends from the database (the friend can be either the user who has sent the friend request or the user who has received the friend request)
        friends = session.query(Befriends).filter(Befriends.user_id == user_id, Befriends.request_status == True).all()
        friends.extend(session.query(Befriends).filter(Befriends.friend_id == user_id, Befriends.request_status == True).all())

        #gets the username of all the users who are friends
        friend_usernames = [session.query(User).filter(User.id == friend.friend_id).first().username for friend in friends if friend.friend_id != user_id]
        friend_usernames.extend([session.query(User).filter(User.id == friend.user_id).first().username for friend in friends if friend.user_id != user_id])
        #create a list of dictionaries with the friends
        friends_list = []
        for friend in friends:
            if(friend.friend_id == user_id):
                friends_list.append({"friend_id": friend.user_id, "friend_name": friend_usernames[friends.index(friend)]})
            else:
                friends_list.append({"friend_id": friend.friend_id, "friend_name": friend_usernames[friends.index(friend)]})
        return {"friends": friends_list, "detail": "Friend list retrieved successfully"}
    
#route for deleting a friend
@router.post("/delete_friend", tags=["friends"])
def delete_friend(friend_id: int, token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    else:
        #decode the token
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        #get the user id from the token
        user_id = decoded_token['id']
        #search whether the friend_id exists in the database
        if session.query(User).filter(User.id == friend_id).first() is None:
            raise HTTPException(status_code=404, detail="User not found")
        else:
            #delete the friend request from the database (both ways)
            session.query(Befriends).filter(Befriends.user_id == user_id, Befriends.friend_id == friend_id).delete()
            session.query(Befriends).filter(Befriends.user_id == friend_id, Befriends.friend_id == user_id).delete()
            session.commit()
            return {"detail": "Friend deleted"}
        

