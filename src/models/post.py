from src.common.database import Database
import uuid
import datetime


class Post(object):

    def __init__(self, blog_id, title, content, author, date_created=datetime.datetime.now(), _id=None):
        self.blog_id = blog_id
        self.title = title
        self.content = content
        self.author = author
        self.date_created = date_created
        self._id = uuid.uuid4().hex if _id is None else _id

    def save_post(self):
        Database.insert(collection='posts', data=self.json())

    def json(self):
        return {
            'blog_id': self.blog_id,
            'title': self.title,
            'content': self.content,
            'author': self.author,
            'date_created': self.date_created,
            '_id': self._id
        }

    @classmethod
    def find_post(cls, _id):
        post_data = Database.find_one(collection='posts', query={'_id': _id})
        return cls(**post_data) if post_data is not None else None

    @classmethod
    def find_posts(cls, blog_id):
        posts = Database.find(collection='posts', query={'blog_id': blog_id})
        return [cls(**post) for post in posts]

    @classmethod
    def find_post_author(cls, author):
        posts = Database.find(collection='posts', query={'author': author})
        return [cls(**post) for post in posts]

    @staticmethod
    def count_posts(user_id):
        posts = Post.find_post_author(user_id)
        count = 0
        for post in posts:
            count = count + 1
        return count