# encoding: utf-8

import requests

class NchanException(Exception):
    pass


class NchanChannel(object):

    def __init__(self, nchan_publish_root_url, channel_id):
        self.nchan_publish_root_url = nchan_publish_root_url
        self.channel_id = channel_id
        self.__stats = {
            'nb_queued_messages': None,
            'nb_subscribers': None,
        }

    def create(self):
        print('Create channel {}'.format(self.channel_id))

        response = requests.post(self.__build_channel_uri(), data="")
        print(response.status_code)

    def publish(self, data):
        try:
            print("Publishing data on <{}>".format(self.channel_id))
            response = requests.post(self.__build_channel_uri(), headers={"Accept": "text/json"}, data=data)

            print("Response:")
            print(response.status_code)
            print(response.json())

        except requests.exceptions.ConnectionError as e:
            raise NchanException("Unable to connect to the NChan server: {}".format(e))

    @property
    def nb_queued_messages(self):
        if self.__stats['nb_queued_messages'] is None:
            self.__refresh_stats(create_channel_if_needed=True)
        return self.__stats['nb_queued_messages']

    @property
    def nb_subscribers(self):
        if self.__stats['nb_subscribers'] is None:
            self.__refresh_stats(create_channel_if_needed=True)
        return self.__stats['nb_subscribers']

    def __refresh_stats(self, create_channel_if_needed=False):
        try:
            response = requests.get(self.__build_channel_uri(), headers={"Accept": "text/json"})
            if response.status_code == 200:
                info = response.json()

                if 'messages' in info:
                    self.__stats['nb_queued_messages'] = int(info['messages'])
                if 'subscribers' in info:
                    self.__stats['nb_subscribers'] = int(info['subscribers'])

            elif response.status_code == 404 and create_channel_if_needed:
                self.create()
                self.__refresh_stats()

        except requests.exceptions.ConnectionError as e:
            raise NchanException("Unable to connect to the NChan server: {}".format(e))

    def __build_channel_uri(self):
        return "{}/{}".format(self.nchan_publish_root_url, self.channel_id)
