# APITurntable

## Web Application

The web application must be hosted such that it is publicly available.
Developed in Python3, it has few library requirements that must be installed prior to its execution.

    > $ virtualenv venv
    > $ source venv/bin/activate
    (venv) > $ pip install -r requirements.txt
    (venv) > $ ./turntable.py

It accepts the following environment variable to ease its configuration:

| Variable Name | Description | Example |
| ------------- | ----------- | ------- |
| `PUBLIC_DOMAIN` | The domain clients can use to contact the web application | de1b6d5a.ngrok.io |
| `SECRET_KEY`    | A secret key for authentication purposes | fnwbzuUhfleoznihjnJekezuJZIU39n2kj |
| `LISTEN_HOST`   | The listen IP or Hostname the server binds to | 127.0.0.1 |
| `LISTEN_PORT`   | A port number the served binds to | 8000 |
| `DATABASE_URI`  | Full URI of the database | sqlite:// |
| `GITHUB_CLIENT_ID` | Github OAuth Application Client ID | b1424e2f1cd4e9c2eeb9 |
| `GITHUB_CLIENT_SECRET` | Gitub OAuth Application Client Secret | LKjqsdkhqldjsqlkdjkqsjk726BHJB3 |
| `NCHAN_ROOT_URI` | Root URI the nchan server is exposed on | http://127.0.0.1:8081 |

The application leverages Github OAuth for user authentication. It requires a `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` that must be attached to a declared OAuth Github App. One that want to start its own instance of the application must declare a github OAuth app with the following information:
* **Application name**: `turntable` (or any other string)
* **Authorization callback URL**: `http://$PUBLIC_DOMAIN$/ui/oauth-github` (you replaced `$PUBLIC_DOMAIN$` by its value)

Once declared on Github, both the obtained `client id` and `client secret` provided by github must be injected in your instance configuration.
