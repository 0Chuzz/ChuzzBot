#!/usr/bin/env python
# vim:fileencoding=utf-8

from .simplebot import event_for, command_for, CommandError, Pluggable

DEFAULT_IRC_DATA = {
        'command_str' : '§',
        'more_limit' : (1, 6)
        }

class CommandEvent(Pluggable):
    plug_name = "commands"

    def start(self):
        self.commands = dict(
                more=self.comm_more,
                nomore=self.comm_nomore,
                help=self.comm_help)

    def evt_check(self, message):
        if message.command == "PRIVMSG":
            return self.evt_call

    def evt_call(self, message):
        cs = self.data['command_str']
        text = message.trail
        
        who = message.source
        where = message.arguments[0]
        if where == self.data['nick']:
            where = message.source.nick

        if text.startswith(cs):
            call_args = text[len(cs):].split()
            try:
                self.commands[call_args.pop(0)](who, where, call_args)
            except Exception as e:
                self.do.say(where, 
                  "EXCEPTION: {0.__class__.__name__}: {0!s}".format(e))


    def register(self, name, func):
        self.commands[name] = func

    def comm_more(self, who, where, args):
        '''<qty>'''
        try:
            lines = int(args[0])
        except (ValueError, IndexError):
            lines = 4
        lines_min, lines_max = self.data['more_limit']
        if not lines_min <= lines <= lines_max:
            raise CommandError('argument cannot be accepted')
        if not self.do.say_more(where, lines):
            self.do.say(where, 'no more')

    def comm_nomore(self, who, where, args):
        if self.do.say_nomore(where):
            self.do.say(where, 'cleared buffer')
        else:
            raise CommandError('empty buffer')

    def comm_help(self, who, where, args):
        func_help = ["{0}: {1}".format(k, v.__doc__ or "no doc") 
                for k,v in self.commands.iteritems()]
        self.do.say(where, func_help)


@command_for('plugins')
def do_plugins(bot,  who, where, args):
    bot.do.say(where, 'plugins loaded:')
    bot.do.say(where, ', '.join(bot.plugins.keys()))
        

