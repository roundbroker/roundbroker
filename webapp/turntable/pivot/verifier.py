# encoding: utf-8

import json
import hmac
import hashlib
import requests

@hook.route('/github', methods=['POST', 'GET'])
def new_github_event():

    flask_error_400 = json.dumps({'success':False}), 400
    
    if request.json is None:
        current_app.logger.error('New event received with an invalid Content-Type')
        return 'Content-Type must be application/json and the request body must contain valid JSON', 400

    data = request.json
    print(data)

    # a valid request MUST have a github Signature header
    signature = request.headers.get('X-Hub-Signature', None)
    if signature is None:
        return flask_error_400

    print("Request is signed")

    # extract repository from request
    repo_id = int(data['repository'].get('id', 0))
    if repo_id == 0:
        return flask_error_400

    print("Fetched repository id")

    # check we know this hook
    hook = Hook.query.filter_by(repo_id=repo_id).first()
    if hook is None:
        return flask_error_400

    print("Found a configured hook")

    # check the signature of the hook
    sig = hmac.new(hook.github_hook_secret.encode('utf8'), digestmod=hashlib.sha1)
    sig.update(request.data)

    if sig.hexdigest() != signature.split('=')[1]:
        return flask_error_400

    print("Signature is valid")

    # publish the hook data
    nchan_uri = "{}/{}".format(current_app.config['NCHAN_PUBLISH_ROOT_URL'], hook.subscribe_uuid)
    print("Publishing hook data on '{}'".format(nchan_uri))
    response = requests.post(nchan_uri, headers={"Accept": "text/json"}, data=request.data)
    print("Response:")
    print(response.status_code)
    print(response.json())
    
    
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

