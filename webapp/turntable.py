#!/usr/bin/env python3
# encoding: utf-8

from app import FlaskServer
server = FlaskServer()
app = server.app

if __name__ == "__main__":
    try:
        server.run()
    finally:
        server.stop()
