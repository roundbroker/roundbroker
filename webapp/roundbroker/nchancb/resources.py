# encoding: utf-8

from flask import request, current_app
from . import blueprint
from roundbroker.visitor_business import VisitorBusiness


@blueprint.route('/channel_id', methods=['GET'])
def get_channel_id():

    # extracting consumer UUID from headers
    consumer_uuid = None
    if 'X-Consumer-Uuid' in request.headers.keys():
        consumer_uuid = str(request.headers['X-Consumer-Uuid'])

    # resolving channel id based on consumer uuid
    current_app.logger.info('Resolving channel ID for consummer uuid={}.'.format(consumer_uuid))
    channel_id = VisitorBusiness().get_channel_id(consumer_uuid)
    current_app.logger.error('Found channel_id = {}'.format(channel_id))

    # configure nchan X-Accel-Redirect headers
    nchan_headers = {
        'X-Accel-Redirect': '/internal/{}'.format(channel_id),
        'X-Accel-Buffering': 'no'
    }

    return "", 200, nchan_headers

