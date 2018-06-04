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


## Start the server stack

A Docker compose stack is available and allows to quickly start all the required services (database, nchan, webapp, etc.).

You could start the stack by executing the following commands.

    docker-compose build
    docker-compose run turntable /usr/local/bin/flask db upgrade
    docker-compose up

The `docker-compose.yaml` file could also be used to deploy the server side in Docker Swarm stack:

    docker deploy -c docker-compose.yaml turntable


## Start the official client

This Git repository contains a client, written in Go. This client is designed to read one (and only one) consumer queue, hence you need to run as many clients as you have pivot URLs.

To start the client on the `48a6a147c5474f7e89229072eb02473c` queue, you can execute the following commands:

    docker build -t turnt -f client/Dockerfile client
    export PIVOT_URL=http://localhost/sub/48a6a147c5474f7e89229072eb02473c
    docker run --rm -it --net="host" -e SERVER_ADDRESS=$PIVOT_URL turnt

One could easily develop its own client to retrieve data from the APITurntable servers.


## URLs

  - Web UI : http://localhost/ui
  - Push base URL : http://localhost/pivot/
  - Consumer base URL : http://localhost/sub/
