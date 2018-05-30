# encoding: utf-8

import uuid
from hashlib import md5
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app

from turntable.extensions import db
from turntable.nchan import NchanChannel

class Pivot(db.Model):

    __tablename__ = 'pivot'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(32), nullable=False, default=str(uuid.uuid4()))
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=True)
    deleted = db.Column(db.Boolean(), default=False, nullable=False)
    created_by = db.Column(db.Integer(), db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime(), default=datetime.utcnow(), nullable=False)
    deleted_at = db.Column(db.DateTime(), nullable=True)
    producers = db.relationship('Producer', lazy='dynamic', backref='pivot')
    consumers = db.relationship('Consumer', lazy='dynamic', backref='pivot')

    @property
    def nb_producers(self):
        return len(list(self.producers))

    @property
    def nb_consumers(self):
        return len(list(self.consumers))

    @property
    def channel_id(self):
        return uuid.UUID(self.uuid).hex

    @property
    def channel(self):
        publish_root_url = current_app.config['NCHAN_PUBLISH_ROOT_URL']
        return NchanChannel(
            nchan_publish_root_url=publish_root_url,
            channel_id=self.channel_id)


class Consumer(db.Model):

    __tablename__ = 'consumer'

    id = db.Column(db.Integer, primary_key=True)
    pivot_id = db.Column(db.Integer(), db.ForeignKey('pivot.id'))
    uuid = db.Column(db.String(32), nullable=False, default=str(uuid.uuid4()))
    url_path = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=True)

    @property
    def url(self):
        return 'apipivots.io/ci/{}'.format(self.url_path)

class Producer(db.Model):

    __tablename__ = 'producer'

    id = db.Column(db.Integer, primary_key=True)
    pivot_id = db.Column(db.Integer(), db.ForeignKey('pivot.id'))
    uuid = db.Column(db.String(32), nullable=False, default=str(uuid.uuid4()))
    url_path = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=True)
    ptype = db.Column(db.String(), nullable=False)

    def is_github(self):
        return self.ptype == 'github'

    @property
    def url(self):
        return 'apipivots.io/pi/{}'.format(self.url_path)

    @property
    def github_secret(self):
        return 'my-super-secret'

class Hook(db.Model):

    __tablename__ = 'hook'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer())
    repo_id = db.Column(db.Integer())
    repo_name = db.Column(db.String())
    repo_owner = db.Column(db.String())
    subscribe_uuid = db.Column(db.String())
    github_hook_secret = db.Column(db.String())
    github_hook_id = db.Column(db.Integer())

    def __init__(self, user_id, repo_id, repo_name, repo_owner, subscribe_uuid, github_hook_secret, github_hook_id):
        self.user_id = user_id
        self.repo_id = repo_id
        self.repo_name = repo_name
        self.repo_owner = repo_owner
        self.subscribe_uuid = subscribe_uuid
        self.github_hook_secret = github_hook_secret
        self.github_hook_id = github_hook_id


class User(db.Model):

    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, index=True)
    name = db.Column(db.String())
    email = db.Column(db.String(), unique=True, index=True)

    password_hash = db.Column(db.String(128))
    avatar_url = db.Column(db.String())
    github_nb_followers = db.Column(db.Integer())
    github_nb_following = db.Column(db.Integer())
    github_access_token = db.Column(db.String(200))
    pivots = db.relationship('Pivot', lazy='dynamic')

    def __init__(self, username=None, email=None, github_access_token=None):
        self.username = username
        self.email = email
        self.github_access_token = github_access_token

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def avatar_url(self, size):
        """
        The URL of the avatar for the given image size
        """
        try:
            size = int(size)
        except Exception:
            raise ValueError('Invalid size')

        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=retro&s={}&r=pg'.format(digest, size)
