#!/usr/bin/python

from .simplebot import event_for, command_for
from .chatcommands import CommandError, Pluggable

DEFAULT_IRC_DATA = {
        'password': '1234pass5',
        'authed': []
        }



@command_for('showauthed')
def do_showauthed(self, who, where, args):
    self.plugins['auth'].check_authed(who)
    outp = ['Users authorized:' ]
    outp += self.data['authed']
    self.do.say(where, outp)


class Auth(Pluggable):
    plug_name = 'auth'
    def evt_check(self, message):
        if self.is_query(message):
            return self.evt_query
    
    def is_query(self, message):
        return (message.command=='PRIVMSG' 
                and message.arguments[0]==self.data['nick'])

    def check_authed(self, source):
        if source not in self.data['authed']:
            raise CommandError('No authorization')

    def evt_query(self, message):
        source = message.source
        if message.trail == self.data['password']:
            self.data['authed'].append(source)
            self.do.say(source, "you're now authed")
        else:
            self.do.say(source, "{0}, don't know ya".format(source.nick))

