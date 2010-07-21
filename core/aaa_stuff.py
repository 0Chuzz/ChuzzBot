#!/usr/bin/python

from .simplebot import event_for, command_for
from .chatcommands import CommandError, parse_command

DEFAULT_IRC_DATA = {
        'password': '1234pass5',
        'authed': []
        }

def only_if_authed(self, source):
    if source not in self.irc_data['authed']:
        raise CommandError('No authorisation')

is_a_query = (lambda x: x.command=='PRIVMSG' 
        and x.arguments[0]==x.bot['nick'])

@event_for(is_a_query)
def on_query(self, source, stuff, text):
    if text == self.irc_data['password']:
        self.irc_data['authed'].append(source)
        self.say(source, "you're now authed")
    elif source in self.irc_data['authed']:
        parse_command(self, source, source.nick, text)
    else:
        self.say(source, "{0}, don't know ya".format(source.nick))

@command_for('showauthed')
def do_showauthed(self, chan, source, args):
    outp = ['Users authorized:' ]
    outp += self.irc_data['authed']
    self.say(chan, outp)

