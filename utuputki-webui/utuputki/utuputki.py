# -*- coding: utf-8 -*-


import json
import settings

from tornado import web, ioloop
from sockjs.tornado import SockJSRouter, SockJSConnection

from db import db_init
from queue import queue_init
from handlers import login, logout, authenticate, queue, register, unknown
from log import GlobalLog, SessionLog


class UtuputkiSock(SockJSConnection):
    clients = set()

    def __init__(self, session):
        self.authenticated = False
        self.sid = None
        self.uid = None
        self.ip = None
        self.log = None
        super(UtuputkiSock, self).__init__(session)

    def on_open(self, info):
        self.authenticated = False
        self.ip = info.ip
        self.log = SessionLog(global_log, self)
        self.clients.add(self)
        self.log.info("Connection accepted")

    def on_message(self, raw_message):
        # Load packet and parse as JSON
        try:
            message = json.loads(raw_message)
        except ValueError:
            unknown.UnknownHandler(self).handle(None)
            return

        # Handle packet by type
        packet_type = message.get('type', '')
        packet_msg = message.get('message', {})

        # Censor login packets for obvious reasons ...
        if packet_type != 'login':
            self.log.debug("Message: {}.".format(raw_message))
        else:
            self.log.debug("Message: **login**")

        # Find and run callback
        cbs = {
            'auth': authenticate.AuthenticateHandler,
            'login': login.LoginHandler,
            'logout': logout.LogoutHandler,
            'register': register.RegisterHandler,
            'queue': queue.QueueHandler,
            'unknown': unknown.UnknownHandler
        }
        cbs[packet_type if packet_type in cbs else 'unknown'](self, packet_type).handle(packet_msg)

    def on_close(self):
        self.log.info("Connection closed")
        self.clients.remove(self)
        self.uid = None
        self.sid = None
        self.ip = None
        self.log = None
        return super(UtuputkiSock, self).on_close()


if __name__ == '__main__':
    print("Utuputki2 Web UI Daemon starting up ...")

    # Set up configuration vars
    settings.config_init()

    # Set up the global log
    if settings.DEBUG:
        global_log = GlobalLog(None, settings.LOG_LEVEL)
    else:
        global_log = GlobalLog(settings.LOG_FILE, settings.LOG_LEVEL)

    global_log.debug("Server port = {}.".format(settings.PORT))
    global_log.debug("Public path = {}".format(settings.PUBLIC_PATH))

    # Set up the database
    db_init(settings.DATABASE_CONFIG)

    # Set up celery queue
    queue_init()

    # Just log success
    global_log.info("Init OK & server running.")

    # SockJS interface
    router = SockJSRouter(UtuputkiSock, '/sock')

    # Index and static handlers
    handlers = router.urls + [
        (r'/(.*)$', web.StaticFileHandler, {'path': settings.PUBLIC_PATH, 'default_filename': 'index.html'}),
    ]

    conf = {
        'debug': settings.DEBUG,
    }

    # Start up everything
    app = web.Application(handlers, **conf)
    app.listen(settings.PORT)
    ioloop.IOLoop.instance().start()
