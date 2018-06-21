FROM golang:1.9-alpine as builder

ENV path /go/src/github.com/roundbroker/roundbroker/client

RUN mkdir -p ${path} && \
    apk update && apk add git
COPY . ${path}

RUN cd ${path} && \
    go get -v ./... && \
    go install ./...

FROM alpine:3.7

RUN apk add --no-cache ca-certificates
COPY --from=builder /go/bin/rb /rb

CMD ["/rb", "collect"]
