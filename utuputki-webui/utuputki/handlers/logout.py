# -*- coding: utf-8 -*-

from handlers.handlerbase import HandlerBase
from db import db_session, Session


class LogoutHandler(HandlerBase):
    def handle(self, packet_msg):
        # Remove session
        s = db_session()
        s.query(Session).filter_by(key=self.sock.sid).delete()
        s.commit()
        s.close()

        # Dump out log
        print("{} Logged out '{}'".format(self.sock.ip, self.sock.sid))

        # Deauthenticate & clear session ID
        self.sock.authenticated = False
        self.sock.sid = None