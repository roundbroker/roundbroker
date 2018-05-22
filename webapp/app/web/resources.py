# encoding: utf-8

import uuid
from datetime import datetime

import requests
from flask import Flask, request, g, session, redirect, url_for
from flask import render_template_string, current_app, render_template
from app.ext.sqlalchemy import db
from app.ext.github import github
from . import blueprint as web
from app.models import User
from app.models import Hook
from app.models import Pivot

@web.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@web.route('/')
def index():
    if g.user:
        return render_template('web/index_member.html')
    else:
        return render_template('web/index_visitor.html')
# if g.user:
#         t = 'Hello {{ g.user.username }}<br />' \
#             '<a href="{{ url_for("web.pushers") }}">See your pushers</a><br />' \
#             '<a href="{{ url_for("web.logout") }}">Logout</a>'
#     else:
#         t = 'Hello! <a href="{{ url_for("web.login") }}">Login</a>'    

#     return render_template_string(t)

@web.route('/login')
def login():
    return render_template('web/login.html')

@web.route('/login/github')
def login_github():
    if session.get('user_id', None) is None:
        return github.authorize(scope='write:repo_hook,read:repo_hook')
    else:
        return 'Already logged in'

@web.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('web.index'))


@web.route('/pivots/<pivot_uuid>')
def pivot_details(pivot_uuid):
    p1 = Pivot()
    p1.uuid = "helloworld"
    p1.user_id = g.user.id
    p1.name = "Sample pivot 1"
    p1.description = None
    p1.deleted = False
    p1.created_at = datetime.utcnow()
    p1.deleted_at = None
    
    return render_template('web/pivot_details.html', pivot=p1)




@web.route('/pushers')
def pushers():    
    t = 'Your repositories:<br />'
    user_repositories = github.get('/user/repos?visibility=public&affiliation=owner')

    for repository in user_repositories:
        t += "#{} {}".format(repository['id'], repository['full_name'])

        t += '<a href="{{ url_for("web.repository", owner="'+repository['owner']['login']+'", name="'+repository['name']+'") }}">Configure</a><br />'
    
    print(user_repositories[0].keys())
    return render_template_string(t)

@web.route('/r/<owner>/<name>')
def repository(owner, name):

    t = "<h1>Repository {}/{}</h1><br />".format(owner, name)
    t += '<h2>Hooks</h2><br />'
    user = g.user
    hook = Hook.query.filter_by(user_id=user.id, repo_owner=owner, repo_name=name).first()
    if hook is None:
        t += 'No hook found<br />'
        t += '<a href="{{ url_for("web.add_hook", owner="'+owner+'", name="'+name+'") }}">Add a Hook</a><br />'
    else:
        hook_info = github.get('repos/{owner}/{name}/hooks/{hook_id}'.format(
            owner=owner,
            name=name,
            hook_id=hook.github_hook_id))
        
        t += "<h3>Configuration</h3>"
        t += str(hook_info)
        t += "<h3>Received Events</h3>"

        nchan_uri = "{}/{}".format(current_app.config['NCHAN_PUBLISH_ROOT_URL'], hook.subscribe_uuid)        
        response = requests.get(nchan_uri, headers={"Accept": "text/json"}, data=request.data)

        if response.status_code == 200:
            t += '<a href="{{ url_for("web.repository_events", owner="'+owner+'", name="'+name+'") }}">Display Events (in realtime)</a><br />'
            info = response.json()
            t += "<ul>"
            t += "<li>Queued messages: <b>{}</b></li>".format(info['messages'])
            t += "<li>Last requested: <b>{}</b></li>".format(info['requested'])
            t += "<li>Active subscribers: <b>{}</b></li>".format(info['subscribers'])
            t += "<li>Last message ID: <b>{}</b></li>".format(info['last_message_id'])
            t += "</ul>"
        else:
            t += "No event found"
    
    return render_template_string(t)

@web.route('/r/<owner>/<name>/events')
def repository_events(owner, name):

    user = g.user
    hook = Hook.query.filter_by(user_id=user.id, repo_owner=owner, repo_name=name).first()
    
    subscribe_url = "{}/{}".format(current_app.config['NCHAN_SUBSCRIBE_ROOT_URL'], hook.subscribe_uuid)
    
    t = """
    <h1>Repository {owner}/{name}</h1><br />
    <div id="event"></div>
         <script type="text/javascript">

         var eventOutputContainer = document.getElementById("event");
         var evtSrc = new EventSource("{subscribe_url}");

         evtSrc.onmessage = function(e) {{
             console.log(e.data);
             eventOutputContainer.innerHTML = e.lastEventId + "] " + e.data;
         }};

         </script>
    """.format(
        owner=owner,
        name=name,
        subscribe_url=subscribe_url)

    return render_template_string(t)

@web.route('/r/<owner>/<name>/add_hook')
def add_hook(owner, name):
    t = "<h1>Repository {}/{}<h1><br />".format(owner, name)
    t += '<h2>Add a Hook</h2><br />'

    hook_secret_key = "helloworld"
    
    new_hook_data = {
        'name': 'web',
        'config': {
            'url': current_app.config.get('HOOK_ROOT_URL')+"/github",
            'content_type': 'json',
            'secret': hook_secret_key,
        },
        'events': ['*'],
    }

    current_app.logger.error("Creating a hook on repo : {}/{}".format(owner, name))
    hook = github.post('/repos/{owner}/{name}/hooks'.format(owner=owner, name=name), data=new_hook_data)

    repository = github.get('/repos/{owner}/{name}'.format(owner=owner, name=name))

    # create hook in database
    hook = Hook(
        user_id=g.user.id,
        repo_id=repository['id'],
        repo_name=name,
        repo_owner=owner,
        subscribe_uuid=uuid.uuid4().hex,
        github_hook_secret=hook_secret_key,
        github_hook_id=hook['id'])

    db.session.add(hook)
    db.session.commit()
    
    return redirect(url_for('web.repository', owner=owner, name=name))


@web.route('/refresh')
def refresh():
    
    user = g.user
    if user is not None:
        # fetch user details
        user_details = github.get('user')
        print(user_details)
        user.username = user_details.get('login', None)
        user.name = user_details.get('name', None)
        user.email = user_details.get('email', None)
        user.nb_followers = int(user_details.get('followers', 0))
        user.nb_following = int(user_details.get('following', 0))
        user.company = user_details.get('company', None)
        user.avatar_url = user_details.get('avatar_url', None)
        db.session.commit()    
    
    return redirect(url_for('web.index'))
    
@web.route('/oauth-github')
@github.authorized_handler
def authorized(access_token):
    
    next_url = request.args.get('next') or url_for('web.refresh')
    if access_token is None:
        return redirect(next_url)

    user = User.query.filter_by(github_access_token=access_token).first()
    if user is None:
        user = User(access_token)
        db.session.add(user)

    user.github_access_token = access_token    
    db.session.commit()
    session['user_id'] = user.id

    return redirect(next_url)
