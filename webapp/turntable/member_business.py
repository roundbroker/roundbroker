# encoding: utf-8
from sqlalchemy.exc import IntegrityError

from turntable.extensions import db
from turntable.models import Pivot
from turntable.models import Producer
from turntable.models import Consumer
from turntable.exceptions import MaxNumberOfPivotReachedException
from turntable.exceptions import MaxNumberOfProducerReachedException
from turntable.exceptions import MaxNumberOfConsumerReachedException
from turntable.exceptions import UnauthorizedException, DuplicateUserException


class MemberBusiness(object):

    def __init__(self, member):
        self.member = member
        if self.member is None:
            raise UnauthorizedException()

    def update_account(self, username=None, password=None):
        """
        Updates the account
        """

        if username is not None:
            self.member.username = username
        if password is not None:
            self.member.set_password(password)

        try:
            db.session.commit()
        except IntegrityError:
            raise DuplicateUserException()

        return self.member

    def create_pivot(self, name, description):
        """
        Creates a pivot on behalf of the current member.
        """

        pivot = Pivot()
        pivot.name = name
        pivot.description = description
        pivot.created_by = self.member.id

        # enforce the max number of pivot per member
        if self.member.can_create_more_pivot():
            db.session.add(pivot)

            # lets create a default producer and consumer
            producer = Producer()
            producer.name = name
            producer.description = description
            producer.url_path = name
            producer.ptype = "generic"
            pivot.producers.append(producer)
            db.session.add(producer)
            
            consumer = Consumer()
            consumer.pivot_id = pivot.id
            consumer.name = name
            consumer.description = description
            consumer.url_path = name
            consumer.ctype = "generic"
            pivot.consumers.append(consumer)
            db.session.add(consumer)
            
            db.session.commit()
        else:
            raise MaxNumberOfPivotReachedException()

        return pivot

    def get_pivot(self, uuid):
        """
        Fetches a pivot with the specified uuid
        on behalf of the current member.
        """

        return Pivot.query.filter_by(
            uuid=uuid, created_by=self.member.id, deleted=False).one()

    def create_generic_producer(self, pivot_uuid, name, description, ptype='generic'):
        """
        Creates a generic producer on behalf
        of the current member.
        """

        pivot = self.get_pivot(uuid=pivot_uuid)

        producer = Producer()
        producer.pivot_id = pivot.id
        producer.name = name
        producer.description = description
        producer.url_path = name
        producer.ptype = ptype

        # enforce the max number of producer per pivot
        if pivot.can_have_more_producer():
            db.session.add(producer)
            db.session.commit()
        else:
            raise MaxNumberOfProducerReachedException()


        return producer

    def create_github_producer(self, pivot_uuid, name, description):
        """
        Creates a github producer on behalf
        of the current member.
        """

        return self.create_generic_producer(
            pivot_uuid=pivot_uuid,
            name=name,
            description=description,
            ptype='github')


    def get_producer(self, producer_uuid):
        """
        Fetches a producer with the specified uuid
        on behalf of the current member.
        """
        return Producer.query.join(Pivot).filter(
            Producer.uuid==producer_uuid,
            Pivot.created_by==self.member.id,
            Pivot.deleted==False).one()

    def get_consumer(self, consumer_uuid):
        """
        Fetches a consumer with the specified uuid
        on behalf of the current member.
        """
        return Consumer.query.join(Pivot).filter(
            Consumer.uuid==consumer_uuid,
            Pivot.created_by==self.member.id,
            Pivot.deleted==False).one()


    def create_generic_consumer(self, pivot_uuid, name, description, ctype='generic'):
        """
        Creates a generic consumer on behalf
        of the current member.
        """

        pivot = self.get_pivot(uuid=pivot_uuid)

        consumer = Consumer()
        consumer.pivot_id = pivot.id
        consumer.name = name
        consumer.description = description
        consumer.url_path = name
        consumer.ctype = ctype

        # enforce the max number of consumer per pivot
        if pivot.can_have_more_consumer():
            db.session.add(consumer)
            db.session.commit()
        else:
            raise MaxNumberOfConsumerReachedException()


        return consumer
