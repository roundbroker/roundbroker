# encoding: utf-8

import uuid
from datetime import datetime
from hashlib import md5
import json
from json import JSONEncoder
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.dialects.postgresql import JSON

from flask import current_app
from turntable.extensions import db
from turntable.nchan import NchanChannel
from turntable.settings import Config
from werkzeug.security import check_password_hash, generate_password_hash


class BaseModelMixin(object):
    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(db.DateTime(), default=db.func.now(), nullable=False)
    updated_at = db.Column(db.DateTime(), default=db.func.now(), onupdate=db.func.now())

class NchanChannelModelMixin(object):
    uuid = db.Column(db.String(36), nullable=False)
    name = db.Column(db.String(), nullable=False)
    description = db.Column(db.String(), nullable=True)
    deleted = db.Column(db.Boolean(), default=False, nullable=False)
    deleted_at = db.Column(db.DateTime(), nullable=True)

    @property
    def channel_id(self):
        return uuid.UUID(self.uuid).hex

    @property
    def channel(self):
        publish_root_url = current_app.config['NCHAN_PUBLISH_ROOT_URL']
        return NchanChannel(
            nchan_publish_root_url=publish_root_url,
            channel_id=self.channel_id)


class Pivot(db.Model, BaseModelMixin, NchanChannelModelMixin):

    __tablename__ = 'pivot'

    producers = db.relationship('Producer', lazy='dynamic', backref='pivot')
    consumers = db.relationship('Consumer', lazy='dynamic', backref='pivot')
    created_by = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __init__(self):
        self.uuid = str(uuid.uuid4())

    def can_have_more_producer(self):
        """
        This method returns False if the pivot has reached
        the maximum number of producer it is allowed to
        """

        return self.nb_producers < 5

    def can_have_more_consumer(self):
        """
        This method returns False if the pivot has reached
        the maximum number of consumer it is allowed to
        """

        return self.nb_consumers < 5

    @property
    def nb_producers(self):
        return db.session.query(Producer).filter_by(pivot_id=self.id).count()

    @property
    def nb_consumers(self):
        return db.session.query(Consumer).filter_by(pivot_id=self.id).count()

    def get_last_webcalls(self):
        return WebCall.query.filter_by(published_on=self.uuid).order_by(WebCall.published_at.desc()).limit(10).all()

class Consumer(db.Model, BaseModelMixin, NchanChannelModelMixin):

    __tablename__ = 'consumer'

    pivot_id = db.Column(db.Integer(), db.ForeignKey('pivot.id'))
    url_path = db.Column(db.String(), nullable=False)
    ctype = db.Column(db.String(), nullable=False)

    def __init__(self):
        self.uuid = str(uuid.uuid4())

    @property
    def url(self):
        return '{}/ci/{}'.format(Config.PUBLIC_DOMAIN, self.url_path)


class Producer(db.Model, BaseModelMixin, NchanChannelModelMixin):

    __tablename__ = 'producer'

    pivot_id = db.Column(db.Integer(), db.ForeignKey('pivot.id'))
    url_path = db.Column(db.String(), nullable=False)
    ptype = db.Column(db.String(), nullable=False)

    def __init__(self):
        self.uuid = str(uuid.uuid4())

    def is_github(self):
        return self.ptype == 'github'

    @property
    def url(self):
        return '{}/pivot/{}'.format(Config.PUBLIC_DOMAIN, self.url_path)

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


class User(db.Model, BaseModelMixin):

    __tablename__ = 'user'

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

    @property
    def nb_pivots(self):
        """
        Returns the number of pivot the user manages
        """

        return db.session.query(Pivot).filter_by(created_by=self.id, deleted=False).count()

    def can_create_more_pivot(self):
        """
        This method returns False if the user has reached
        the maximum number of pivot he is allowed to
        """

        return self.nb_pivots < 5

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


class WebCallRequest(object):

    def __init__(self, protocol):
        self.protocol = protocol

class WebCallRequestHttp11(WebCallRequest):

    def __init__(self, method, headers, cookies, body, source_ip, source_url, extra_path=None, args=None):
        super(WebCallRequestHttp11, self).__init__(protocol='http 1.1')

        self.method = method
        self.headers = headers
        self.cookies = cookies
        self.body = body
        self.source_ip = source_ip
        self.source_url = source_url
        self.extra_path = extra_path
        self.args = args

    def to_dict(self):
        return {
            'method': self.method,
            'headers': self.headers,
            'cookies': self.cookies,
            'body': self.body,
            'source_ip': self.source_ip,
            'source_url': self.source_url,
            'extra_path': self.extra_path,
            'args': self.args,
        }


class CustomJsonEncoder(JSONEncoder):
    def default(self, o):
        return str(o)


class WebCall(db.Model, BaseModelMixin):

    __tablename__ = 'webcall'
    
    uuid = db.Column(db.String(36), nullable=False)
    published_at = db.Column(db.DateTime(), nullable=True)
    published_on = db.Column(db.String(36), nullable=True)
    request = db.Column(JSON)
    
    def __init__(self, webcall_request):
        self.uuid = str(uuid.uuid4())
        self.request = webcall_request.to_dict()
        self.published_on = None
        self.published_at = None
        

    def to_dict(self):
        return {
            'received_at': self.created_at,
            'published_on': self.published_on,
            'published_at': self.published_at,
            'request': self.request
        }

    def to_json(self):
        return json.dumps(
            self.to_dict(),
            cls=CustomJsonEncoder, sort_keys=True)
