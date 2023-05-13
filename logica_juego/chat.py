from models.user import User

class Message:
    def __init__(self, user: User, message: str):
        self.id : int = user.id
        self.username : str = user.username
        self.message: str = message


class Chat:
    def __init__(self):
        self.messages : list[Message] = []

    def add_message(self, user: User, message: str):
        self.messages.append(Message(user, message))

    def get_messages(self):
        return self.messages
    