from src.common.database import Database
import uuid
import datetime


class Blog(object):

    def __init__(self, user_id, title, description, date_created=datetime.datetime.now(), _id=None):
        self.user_id = user_id
        self.title = title
        self.description = description
        self.date_created = date_created
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_blog(self):
        Database.insert(collection='blogs', data=self.json())

    def json(self):
        return {
            'user_id': self.user_id,
            'title': self.title,
            'description': self.description,
            'date_created': self.date_created,
            '_id': self._id
        }

    @classmethod
    def find_blog(cls, _id):
        blog_data = Database.find_one(collection='blogs', query={'_id': _id})
        return cls(**blog_data) if blog_data is not None else None

    @classmethod
    def find_blogs(cls, user_id):
        blogs = Database.find(collection='blogs', query={'user_id': user_id})
        return [cls(**blog) for blog in blogs]

    @staticmethod
    def count_blogs(user_id):
        blogs = Blog.find_blogs(user_id)
        count = 0
        for blog in blogs:
            count = count+1
        return count
