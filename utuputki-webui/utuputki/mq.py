# -*- coding: utf-8 -*-

import pika
import settings
import json

class MessageQueue(object):
    def __init__(self, io_loop, log):
        self.log = log
        self.io_loop = io_loop
        self.connected = False
        self.connection = None
        self.channel = None
        self.message_count = 0
        self.event_listeners = set([])

    def connect(self):
        self.connection = pika.adapters.TornadoConnection(
            pika.URLParameters(settings.AMQP_URL),
            on_open_callback=self.on_connected
        )
        self.connection.add_on_close_callback(self.on_closed)

    def on_connected(self, connection):
        self.log.info("MQ: Connected to AMQP server")
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        self.log.info('MQ: Channel {} open.'.format(channel))
        self.channel = channel

    def on_closed(self, connection):
        self.log.info('MQ: Connection closed')

    def notify(self, packet):
        event_json = json.dumps(packet)
        for listener in self.event_listeners:
            listener.write_message(event_json)
            self.log.info('MQ: Notify {}'.format(repr(listener)))

    def add_event_listener(self, listener):
        self.event_listeners.add(listener)
        self.log.info('MQ: listener {} added'.format(repr(listener)))

    def del_event_listener(self, listener):
        try:
            self.event_listeners.remove(listener)
            self.log.info('MQ: listener {} removed'.format(repr(listener)))
        except KeyError:
            pass
