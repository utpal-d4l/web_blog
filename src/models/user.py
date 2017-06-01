from src.common.database import Database
import uuid
from flask import session


class User(object):

    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            'email': self.email,
            'password': self.password,
            '_id': self._id
        }

    def save_user(self):
        Database.insert(collection='users', data=self.json())

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one('users', {'email': email})
        return cls(**data) if data is not None else None

    @staticmethod
    def register(email, password):
        user = User.get_by_email(email)
        if user is None:
            user = User(email, password)
            user.save_user()
            return True
        else:
            return False

    @staticmethod
    def login(user_email):
        session['email'] = user_email

    @staticmethod
    def logout():
        session['email'] = None