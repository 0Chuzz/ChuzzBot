#!/usr/bin/env python
'''this module contains an implementation of a IRC message parser using
asynchat from the standard library. Should work with ssl, too
'''

import asynchat
import socket, ssl
import re
import logging
from .numevents import numeric_events

class IRCError(Exception):
    pass

class IRCConnection(asynchat.async_chat):
    '''Abstract base for an asinchronous irc connection'''
    def __init__(self, host, is_ssl=False):
        '''constructor of the class IrcClient.

        host is a tuple fed to socket.connect().
        is_ssl bool, use ssl. Default is False
        logger is the logging handler.Default logger prints errors on stderr.
        ''' 
        mysock = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)
        asynchat.async_chat.__init__(self, sock=mysock)
        self._inbuf = bytearray()
        self.is_ssl = is_ssl
        self.set_terminator(b'\r\n')
        self.host = host
        self.log = logging.getLogger('IRC parser')
        self.log.addHandler(logging.StreamHandler())
        self._on_connect, self._on_event = None, None

    def start(self):
        """connect to the host and start event handling."""
        self.connect(self.host)

    def collect_incoming_data(self, data):
        '''asynchat connection handler. Internal.'''
        if not self._on_event:
            raise IRCError("No event handler specified")
        self._inbuf.extend(data)

    def found_terminator(self):
        '''asynchat connection handler. Internal.'''
        self.log.debug('>> ' + self._inbuf)
        self._inbuf.extend(b'\r\n')
        try:
            msg = IRCMessage(str(self._inbuf))
        except IRCError as error:
            self.log.error("Invalid IRC Message")
            self.log.debug(repr(str(error)))
        else:
            self._on_event(msg)
        finally:
            self._inbuf = bytearray()
    
    def handle_connect(self):
        '''asynchat connection handler. Internal. '''
        if self.is_ssl:
            self.del_channel()
            self.set_socket(ssl.wrap_socket(self.socket, 
                suppress_ragged_eofs=False, do_handshake_on_connect=True,
                ssl_version=ssl.PROTOCOL_SSLv23))
        if self._on_connect is not None:
            self.log.debug('firing connection event')
            self._on_connect()

    def send_msg(self, message):
        '''sends a message to the server

        message is a IRCMessage to be sent.
        '''
        try:
            message = str(message)
        except IRCError as error:
            self.log.error(error)
        else:
            self.log.debug('<< ' + message.replace('\r\n', ''))
            self.push(message)

    def bind_events(self, on_connect, on_event):
        """bind event handlers for connection and incoming messages.
        
        on_connect() is called on connection. no arguments.
        on_event(irc_message) is sent on incoming messages, the ony argument is
        the message in question, a IRCMessage object.
        """
        self._on_connect = on_connect
        self._on_event = on_event
        return self.send_msg

class IRCMessage(object):
    """generic irc message class."""
    re_cmd = re.compile(r'''^
    (?: :(?P<source> [^\r\n ]+ ) [ ])?
    (?P<comm> [A-Za-z0-9]+ )
    (?:\ (?P<args> [^\r\n:]+ ))?
    (?:\ ?:(?P<trail> [^\r\n]+ ))?
    \r$''', re.VERBOSE)

    def __init__(self, line=''):
        """class constructor.

        line is the optional string to parse, usually coming from the
        server.
        """
        self.source, self.command = None, None
        self.arguments, self.trail = None, None
        if line:
            self.parse(line)

    def parse(self, line):
        """parse a line to get source, command, args and trail."""
        message = self.re_cmd.match(line)
        if not message:
            raise IRCError(line)
        else:
            message = message.groupdict()
        #prepare arguments for self.event()
        self.source = (message.get('source', ''))
        if self.source:
            self.source = Source(self.source)
        self.command = (numeric_events.get(message['comm'])
                        or message['comm'])
        self.command = self.command.upper()
        self.arguments = (message.get('args') or '').strip()
        if self.arguments:
            self.arguments = self.arguments.split(' ')
        #remove whitespace and empty strings from the arguments list
        self.trail = message.get('trail', '')

    def __str__(self):
        """output the string representaton of the message."""
        #switching from string to bytes
        outp = [self.command]
        outp.extend(self.arguments)
        outp = ' '.join(outp)
        if self.trail:
            outp += b' :' + self.trail
        outp += b'\r\n'
        if not self.re_cmd.match(outp):
            raise IRCError('invalid output')
        return outp

    def __repr__(self):
        return "IRCMessage({0})".format(repr(str(self)))

    def __eq__(self, other):
        return repr(self)==repr(other)

class Source:
    '''a representation of a source of a irc message. can be a server or a
    user, check Source.is_user'''
    re_mask = re.compile('''
            ([^!]+)  #nick
            ! ([^@]*) #user
            @ (.+)   #host
            ''', re.VERBOSE)

    def __init__(self, user):
        """class constructor. usar is the usermask/server."""
        match = self.re_mask.match(user)
        if match:
            self.nick, self.user, self.host =  match.groups()
            self.is_user = True
        else:
            self.server = user.strip()
            self.is_user = False

    def __str__(self):
        if self.is_user:
            return self.nick + '!' + self.user + '@' + self.host
        else:
            return self.server

    def __repr__(self):
        return repr(str(self))

    def __eq__(self, other):
        '''Compare between two irc masks, ignoring the nick'''
        if hasattr(other, 'is_user') and self.is_user and other.is_user:
            return self.user == other.user and self.host == other.host
        else:
            return str(self) == str(other)

