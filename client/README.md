# Installation
## Bare installation
Bare installation needs `go` installed on the host

```bash
go install ./...
```


## Docker installation
Docker installation needs `docker` installed on the host
```bash
make build
```

# Running the client
## Env variable used in this CLI command
- RB_VERBOSE (bool): define the verbosity leve of the application
- RB_SERVER_ADDRESS (string): address of the main roundbroker server
- RB_DESTINATION_SERVICE_URL (string): address of the service to send request to (ex: mattermost, bell, etc.)
- RB_CONSUMER_UUID="secret_code_to_consume"
- RB_TLS_INSECURE=true

for bare installation, just run `rb collect` command to launch the client.
it connects to the `SERVER_ADDRESS` URL and retrieve requests in SSE mode.


## Run with bare installation

```bash
export RB_SERVER_ADDRESS=https://roundbroker.io/c
export RB_CONSUMER_UUID="secret_code_to_consume"
export RB_DESTINATION_SERVICE_URL=http://mattermost.entreprise.com/hooks/123456789
export RB_TLS_INSECURE=true
rb
```

## Run with docker installation

```bash
docker run \
    --rm -it \
    -e RB_SERVER_ADDRESS=https://roundbroker.io/c \
    -e RB_DESTINATION_SERVICE_URL=http://mattermost.entreprise.com/hooks/123456789 \
    -e RB_CONSUMER_UUID="secret_code_to_consume" \
    -e RB_TLS_INSECURE=true \
    rb
```