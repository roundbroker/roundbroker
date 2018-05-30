# encoding: utf-8

import requests

class NchanChannel(object):

    def __init__(self, nchan_publish_root_url, channel_id):
        self.nchan_publish_root_url = nchan_publish_root_url
        self.channel_id = channel_id
        self.__stats = None

    def create(self):
        print('Create channel {}'.format(self.channel_id))
        nchan_uri = "{}/{}".format(self.nchan_publish_root_url, self.channel_id)
        response = requests.post(nchan_uri, data="")
        print(response.status_code)

    @property
    def nb_queued_messages(self):
        if self.__stats is None:
            self.__refresh_stats(create_channel_if_needed=True)
        return self.__stats['nb_queued_messages']

    @property
    def nb_subscribers(self):
        if self.__stats is None:
            self.__refresh_stats(create_channel_if_needed=True)
        return self.__stats['nb_subscribers']

    def __refresh_stats(self, create_channel_if_needed=False):
        try:
            nchan_uri = "{}/{}".format(self.nchan_publish_root_url, self.channel_id)
            response = requests.get(nchan_uri, headers={"Accept": "text/json"})
            if response.status_code == 200:
                info = response.json()

                self.__stats = dict()
                if 'messages' in info:
                    self.__stats['nb_queued_messages'] = int(info['messages'])
                if 'subscribers' in info:
                    self.__stats['nb_subscribers'] = int(info['subscribers'])

            elif response.status_code == 404 and create_channel_if_needed:
                self.create()
                self.__refresh_stats()

        except Exception as e:
            print(e)


