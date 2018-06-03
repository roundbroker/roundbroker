# APITurntable

## Web Application

The web application must be hosted such that it is publicly available.
Developed in Python3, it has few library requirements that must be installed prior to its execution.

    > $ cd webapp
    > $ python3 -m venv venv
    > $ source venv/bin/activate
    (venv) > $ pip3 install -r requirements.txt
    (venv) > $ FLASK_APP=turntable flask db upgrade
    (venv) > $ FLASK_APP=turntable FLASK_DEBUG="true" flask run --port 4242

It accepts the following environment variable to ease its configuration:

| Variable Name | Description | Example |
| ------------- | ----------- | ------- |
| `PUBLIC_DOMAIN` | The domain clients can use to contact the web application | de1b6d5a.ngrok.io |
| `SECRET_KEY`    | A secret key for authentication purposes | fnwbzuUhfleoznihjnJekezuJZIU39n2kj |
| `DATABASE_URI`  | Full URI of the database | sqlite:// |
| `GITHUB_CLIENT_ID` | Github OAuth Application Client ID | b1424e2f1cd4e9c2eeb9 |
| `GITHUB_CLIENT_SECRET` | Gitub OAuth Application Client Secret | LKjqsdkhqldjsqlkdjkqsjk726BHJB3 |
| `NCHAN_ROOT_URI` | Root URI the nchan server is exposed on | http://127.0.0.1:8081 |

The application leverages Github OAuth for user authentication. It requires a `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` that must be attached to a declared OAuth Github App. One that want to start its own instance of the application must declare a github OAuth app with the following information:
* **Application name**: `turntable` (or any other string)
* **Authorization callback URL**: `http://$PUBLIC_DOMAIN$/ui/oauth-github` (you replaced `$PUBLIC_DOMAIN$` by its value)

Once declared on Github, both the obtained `client id` and `client secret` provided by github must be injected in your instance configuration.


## Docker compose stack

A Docker compose stack is available and could be used as follow:

    docker-compose build
    docker-compose run turntable /usr/local/bin/flask db upgrade
    docker-compose up

And you could deploy this app in a Docker Swarm stack:

    docker deploy -c docker-compose.yaml turntable


## URLs

  - Web UI : http://localhost:4242/ui
  - Push base URL : http://localhost:4242/pivot/
  - Consumer base URL : http://localhost:4242/sub/
