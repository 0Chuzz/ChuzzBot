#!/usr/bin/env python

from mock import Mock
from core import irc_async

class DummyAsync(object, irc_async.IRCClient):
    def connect(self, host):
        self.socket = Mock()
        super(DummyAsync, self).connect(host)
