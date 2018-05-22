#!/usr/bin/env python3
# encoding: utf-8


import sseclient
# import json
# import pprint
# import requests
# import urllib3
    
def run():
    url='http://127.0.0.1:8081/sub/07eec00d0c4748539b39f138947ad152'


    # http = urllib3.PoolManager()
    # response = http.request('GET', url, preload_content=False)
    
    #response = requests.get(url, stream=True)
    messages = sseclient.SSEClient(url)
    for message in messages:
        print(message)
    # print("Starting...")
    # for event in client.events():
    #     pprint.pprint(json.loads(event.data))
    # print("Finishing...")

if __name__ == "__main__":
    run()
