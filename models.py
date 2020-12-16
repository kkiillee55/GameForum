from modules import db,application
from datetime import datetime, timedelta
import jwt

class User(db.Model):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True)
    first_name=db.Column(db.String(50),nullable=False)
    last_name=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(120),nullable=False,unique=True)
    password=db.Column(db.String(200),nullable=False)
    status=db.Column(db.String(10),nullable=False,default='PENDING')
    is_admin=db.Column(db.Boolean,nullable=False,default=True)
    date_created=db.Column(db.DateTime,nullable=False,default=datetime.utcnow())
    address=db.Column(db.String(100),nullable=False,default='Earth')
    posts=db.relationship('Post',backref='author',lazy=True,cascade="all,delete-orphan")
    comments=db.relationship('Comment',backref='author',lazy=True,cascade="all,delete-orphan")
    following_games=db.relationship(
        'Game',
        secondary='user_game'
    )

    def generate_token(self,expire_min=30):
        return jwt.encode(
            {'user_id': self.id, 'first_name': self.first_name, 'last_name': self.last_name, 'email': self.email,'exp':datetime.utcnow()+timedelta(minutes=expire_min)},
            application.config['SECRET_KEY']
        ).decode('utf-8')

    @staticmethod
    def verify_token(token):
        try:
            data=jwt.decode(token,application.config['SECRET_KEY'])
            return data
        except jwt.ExpiredSignatureError:
            return None


    def __repr__(self):
        return f'{self.first_name} {self.last_name}, {self.email}'

class UserGameJunction(db.Model):
    __tablename__='user_game'
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),primary_key=True)
    game_id=db.Column(db.Integer,db.ForeignKey('game.id'),primary_key=True)

class Game(db.Model):
    __tablename__='game'
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(50),nullable=False,unique=True)
    release_date=db.Column(db.DateTime,nullable=False)
    posts=db.relationship('Post',backref='game',lazy=True,cascade="all,delete-orphan")
    followers=db.relationship(
        'User',
        secondary='user_game'
    )

    platforms=db.relationship(
        'Platform',
        secondary='game_platform'
    )

    def __repr__(self):
        return f'{self.title}-{self.release_date}'

class GamePlatformJunction(db.Model):
    __tablename__='game_platform'
    game_id=db.Column(db.Integer,db.ForeignKey('game.id'),primary_key=True)
    platform_id=db.Column(db.Integer,db.ForeignKey('platform.id'),primary_key=True)

class Platform(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False,unique=True)
    games=db.relationship(
        'Game',
        secondary='game_platform'
    )
    def __repr__(self):
        return self.name

class Post(db.Model):
    __tablename__='post'
    id=db.Column(db.Integer,primary_key=True)
    date_posted=db.Column(db.DateTime,nullable=False,default=datetime.utcnow())
    title=db.Column(db.String(100),nullable=False)
    content=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    game_id=db.Column(db.Integer,db.ForeignKey('game.id'),nullable=False)
    comments=db.relationship('Comment',backref='post',lazy=True,cascade="all,delete-orphan")
    def __repr__(self):
        return f'{self.title}, {self.author.first_name+" "+self.author.last_name}'


class Comment(db.Model):
    __tablename__='comment'
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    post_id=db.Column(db.Integer,db.ForeignKey('post.id'),nullable=False)
    comment_uuid=db.Column(db.String(100),nullable=False)
    comment_parent_uuid=db.Column(db.String(100),nullable=False)
    def __repr__(self):
        return f'{self.author.first_name+" "+self.author.last_name}, {self.post.title}, {self.comment_uuid}, {self.comment_parent_uuid}'


'''
class Comment:
    id
    user_id
    post_id
    comment_id
    comment_parent_id

'''




