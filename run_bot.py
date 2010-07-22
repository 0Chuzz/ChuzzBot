#!/usr/bin/env python
#vim:fileencoding=utf-8

from core import irc_async, simplebot
import asyncore
import logging

try:
    from config import IRC_DATA
except ImportError:
    print "Missing config.py, run"
    print "$ echo \"IRC_DATA = {}\" > config.py"
    print "to get a quick fix."
    exit()

for log in ['IRC parser', 'IRC bot']:
    logging.getLogger(log).setLevel(logging.DEBUG)
a_parser = irc_async.IRCConnection(('irc.unitx.net', 6697), True)
a = simplebot.SimpleBot(a_parser, IRC_DATA, ('plugins.develbot',))
if __name__ == '__main__':
    a_parser.start()
    try:
        asyncore.loop()
    except BaseException as e:
        from traceback import print_exception
        print_exception(RuntimeError, e, None, limit=15)
