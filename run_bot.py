#!/usr/bin/env python
#vim:fileencoding=utf-8

from core import irc_async, simplebot
import asyncore
import logging


for log in ['IRC parser', 'IRC bot']:
    logging.getLogger(log).setLevel(logging.DEBUG)
a_parser = irc_async.IRCConnection(('irc.unitx.net', 6697), True)
a = simplebot.SimpleBot(a_parser, {})
if __name__ == '__main__':
    a_parser.start()
    try:
        asyncore.loop()
    except BaseException as e:
        from traceback import print_exception
        print_exception(RuntimeError, e, None, limit=15)
