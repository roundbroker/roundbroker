from . import blueprint

from flask import request, g, session, redirect, url_for
import json

@blueprint.route('/<string:pid>', methods=['GET', 'POST'])
@blueprint.route('/<string:pid>/<path:extra_path>', methods=['GET', 'POST'])
def push(pid, uri_append=None):

    posted_data = {
        'method': request.method,
        'uri_append': uri_append,
        'headers': { k: v for k, v in request.headers.items() },
        'body': request.get_data(as_text=True),
        'cookies': request.cookies,
        'source_ip': request.remote_addr,
        'source_url': request.url,
    }

    print(posted_data)
