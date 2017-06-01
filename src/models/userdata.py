from src.common.database import Database
import uuid


class UserData(object):
    def __init__(self, email, first_name, last_name, date_of_birth, profession, _id=None):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.profession = profession
        self._id = uuid.uuid4().hex if _id is None else _id

    def json(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth,
            'profession': self.profession,
            '_id': self._id
        }

    def save_user_data(self):
        Database.insert(collection='user_data', data=self.json())

    @classmethod
    def find_user_data(cls, user_id):
        user_data = Database.find_one(collection='user_data', query={'email': user_id})
        return cls(**user_data) if user_data is not None else None