# encoding: utf-8

from sqlalchemy.exc import IntegrityError

from turntable.extensions import db
from turntable.models import User, Producer
from turntable.nchan import NchanChannel, NchanException
from turntable.exceptions import InvalidProducerException, NchanCommunicationError

from sqlalchemy.orm import exc

class VisitorBusiness(object):

    def __init__(self):
        pass

    def create_user(self, username, email, password):
        """
        Creates a user with the specified info.

        :raises turntable.exceptions.DuplicateUserException: if equivalent user already exists
        """

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)

        try:
            db.session.commit()
        except IntegrityError:
            raise exceptions.DuplicateUserException()

        return user

    def login_user(self, email, password):
        """
        Returns the user that matches both the provided
        email and password
        """

        user = User.query.filter_by(email=email).scalar()
        if user is None or not user.check_password(password):
            raise ValueError('User not found')

        return user

    def publish(self, pid, data):
        try:
            p = Producer.query.filter(Producer.url_path == pid).one()
            p.pivot.channel.publish(data)
        except exc.NoResultFound as e:
            raise InvalidProducerException("Producer <{}> is not defined in our database".format(pid))
        except NchanException as e:
            raise NchanCommunicationError("Unable to communicate with Nchan for producer id=<{}>: {}".format(pid, e))
