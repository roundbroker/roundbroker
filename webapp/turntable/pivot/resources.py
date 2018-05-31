from . import blueprint

from turntable.visitor_business import VisitorBusiness
from turntable.exceptions import BusinessException

from flask import request, g, session, redirect, url_for, current_app
import json

@blueprint.route('/<string:pid>', methods=['GET', 'POST'])
@blueprint.route('/<string:pid>/<path:uri_append>', methods=['GET', 'POST'])
def push(pid, uri_append=None):
    app = current_app
    flask_error_400 = json.dumps({'success':False}), 400

    app.logger.info("Handling new request for pivot=<{}>".format(pid))

    try:
        posted_data = {
            'method': request.method,
            'uri_append': uri_append,
            'headers': { k: v for k, v in request.headers.items() },
            'body': request.get_data(as_text=True),
            'cookies': request.cookies,
            'source_ip': request.remote_addr,
            'source_url': request.url,
        }

        VisitorBusiness().publish(pid, posted_data)

        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

    except BusinessException as e:
        app.logger.info("Error while handling the request for pivot=<{}>: {}".format(pid, e))
        return flask_error_400

    except Exception as e:
        app.logger.info("Error while handling the request for pivot=<{}>: {}".format(pid, e))
        return flask_error_400
