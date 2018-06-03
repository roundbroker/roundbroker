from . import blueprint

from turntable.visitor_business import VisitorBusiness
from turntable.exceptions import BusinessException
from turntable.models import WebCall, WebCallRequestHttp11
from flask import request, g, session, redirect, url_for, current_app
import json

@blueprint.route('/<string:pid>', methods=['GET', 'POST'])
@blueprint.route('/<string:pid>/<path:uri_append>', methods=['GET', 'POST'])
def push(pid, uri_append=None):
    app = current_app
    flask_error_400 = json.dumps({'success':False}), 400

    app.logger.info("Handling new request for pivot=<{}>".format(pid))

    try:
        httpreq = WebCallRequestHttp11.from_request(request)
        VisitorBusiness().publish(pid, WebCall(httpreq))
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

    except BusinessException as e:
        app.logger.info("Error while handling the request for pivot=<{}>: {}".format(pid, e))
        return flask_error_400

    except Exception as e:
        app.logger.info("Error while handling the request for pivot=<{}>: {}".format(pid, e))
        return flask_error_400
