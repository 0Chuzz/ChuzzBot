#!python3

from core.simplebot import event_for, command_for
from core.chatcommands import ActionError

default_irc_data = {
        'password': '1234pass'
        'authed': []
        }

is_a_query = (lambda x: x.command=='PRIVMSG' 
        and x.arguments[1]==x.self['nick'])

@event_for(is_a_query)
def on_query(self, source, stuff, text):
    if source in self.irc_data['authed']:
        try:
            evalling = str(eval(text))
        except BaseException as e:
            if isinstance(SystemExit, e): raise
            evalling = str(e)
        self.talk(source, evalling)
    else:
        if text == self.irc_data['password']:
            self.irc_data['authed'].append(source)
            self.talk(source, "you're now authed")
        else:
            self.talk(source, "{}, don't know ya".format(source.nick))

@command_for('showauthed')
def do_showauthed(self, chan, source, args):
    outp = 'Users authorized:\n' + '{!s}\n'*len(self.irc_data['authed'])
    outp.format(*self.irc_data['authed'])
    self.talk(chan, outp)
