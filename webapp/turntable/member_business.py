# encoding: utf-8

from turntable.extensions import db
from turntable.models import Pivot
from turntable.models import Producer

class MemberBusiness(object):

    def __init__(self, member):
        self.member = member

    def create_pivot(self, name, description):
        """
        Creates a pivot on behalf of the current member.
        """

        pivot = Pivot()
        pivot.name = name
        pivot.description = description
        pivot.created_by = self.member.id
        
        db.session.add(pivot)
        db.session.commit()

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

        db.session.add(producer)
        db.session.commit()
        
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
