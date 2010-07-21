#!/usr/bin/env python

import logging
import imp
import weakref
from .irc_async import  Source, IRCMessage


class CommandError(Exception): 
    pass


class Stuffer(object):
    pass


class Pluggable(object):
    plug_name = None
    def __init__(self, do, plugins, irc_data):
        self.do = do
        self.plugins = plugins
        self.data = irc_data

    def start(self):
        pass

    def evt_check(self, message):
        return self.evt_call

    def evt_call(self,message):
        pass

    def on_error(self, errmsg):
        pass


def event_for(*params):
    def event_factor(func):
        class OnTheFlyEvent(Pluggable):
            plug_name = func.__name__
            def evt_check(self, message):
                if message.command in params:
                    return self.evt_call
                else:
                    return None
            
            def evt_call(self, message):
                func(self, message)

        return OnTheFlyEvent
    return event_factor


def command_for(command_name):
    def command_factor(func):
        class OnTheFlyComm(Pluggable):
            plug_name = func.__name__

            def start(self):
                myattr = getattr(self, "comm_" + command_name)
                self.plugins["commands"].register(command_name, myattr)

            def _dummy_comm(self, *args):
                return func(self, *args)

        setattr(OnTheFlyComm, 'comm_' + command_name, OnTheFlyComm._dummy_comm)
        return OnTheFlyComm
    return command_factor


class ChatOutput(object):
    def __init__(self, raw_out):
        self.raw_message = raw_out
        self.output_buff = {}

    def raw(self, *args):
        args = list(args)
        message = IRCMessage()
        message.command = args.pop(0)
        message.trail = args.pop()
        message.arguments = args
        self.raw_message(message)

    def raw_trail(self, *args, **kwargs):
        trail = kwargs.get('trail')
        args = list(args)
        args.append(trail)
        self.raw(*args)

    def __getattr__(self, attr_name):
        def generic(*attr):
            self.raw(attr_name.upper(), *attr)
        return generic

    def nick(self, new_nick):
        self.raw_trail('NICK', new_nick)
    
    def join(self, chan):
        self.raw_trail('JOIN', chan)

    def say(self, dest, text):
        if isinstance(dest, Source):
            dest = dest.nick
        if hasattr(text, "splitlines"):
            text = text.splitlines()
        if not dest in self.output_buff:
            self.output_buff[dest] = []
        self.output_buff[dest].extend(text)
        self.say_more(dest)

    def say_more(self, chan, howmuch=1):
        if chan not in self.output_buff:
            return False
        for message in self.output_buff[chan][:howmuch]:
            self.privmsg(chan, str(message))
        del self.output_buff[chan][:howmuch]
        if not self.output_buff[chan]:
            del self.output_buff[chan]
            return False
        else:
            self.privmsg(chan, 'still more...')
            return True
    
    def say_nomore(self, chan):
        return self.output_buff.pop(chan, [])


class SimpleBot(object):
    DEFAULT_MODULES = ( 'core.basic', 'core.chatcommands',#) 
            'core.aaa_stuff',)# 'core.privileged_commands')

    def __init__(self, irc_parser, irc_data, modules=tuple()):
        self._irc_parser = irc_parser
        self.send_msg = self._irc_parser.bind_events(
                    self.on_connect, self.event
                    )
        self.irc_data = irc_data
        self._modules = {}
        self.plugins = {}#weakref.WeakValueDictionary()
        self._output = ChatOutput(self.send_msg)
        self.log = logging.getLogger('IRC bot')
        self.log.addHandler(logging.StreamHandler())

        modules += self.DEFAULT_MODULES
        for module in modules:
            self.load_ext_module(module)

    def __getattr__(self, attr_name):
        return getattr(self._irc_parser, attr_name)

    def on_connect(self):
        self.log.debug("start fired. starting {0!s}".format(dict(self.plugins)))
        for pname, plugin in self.plugins.iteritems():
            self.log.debug('starting '+pname)
            plugin.start()

    def load_ext_module(self, module_name):
        self.log.debug("loading " + module_name)
        if module_name in self._modules:
            self.log.warning(module_name + 'already loaded')
            return
        try:
            #recursively load packag, [])s
            mdle = Stuffer() 
            mdle.__path__ = ''
            mdle.__name__ = ''
            for package in module_name.split('.'):
                found_mdle = imp.find_module(package, 
                        mdle.__path__ or None)
                mdle = imp.load_module(
                        mdle.__name__ or mdle.__name__ + '.' + package,
                        *found_mdle
                        )
        except ImportError as e:
            self.log.error(str(e))
            return

        self._modules[module_name] = mdle
        if hasattr(mdle, 'DEFAULT_IRC_DATA'):
            for option in mdle.DEFAULT_IRC_DATA.iteritems():
                self.irc_data.setdefault(*option)
        
        #load plugin and commands
        for module_content in dir(mdle):
            stuff = getattr(mdle, module_content)
            if hasattr(stuff, 'plug_name') and stuff.plug_name:
                try:
                    plugg = stuff(self._output, self.plugins, self.irc_data)
                except Exception:
                    err = "{0} in {1} cannot be loaded"
                    self.log.error(err.format(module_content, module_name))
                    self.unload_ext(module_name)
                    return
                self.plugins[stuff.plug_name] = plugg
                self.log.debug('loaded ' + stuff.plug_name)

    def unload_ext_module(self, module_name):
        try:
            p = self._modules[module_name]
        except KeyError:
            self.log.error("unload {0}: no such module".format(module_name))
        else:
            self.log.debug('unload {0}: success'.format(module_name))

    def reload_ext_module(self, module_name):
        self.unload_ext_module(module_name)
        self.load_ext_module(module_name)

    def event(self, message):
        for evt in self.plugins.itervalues():
            try:
                evt_f = evt.evt_check(message)
                if evt_f:
                    evt_f(message)
            except Exception as e:
                error = '{0}: {1}'.format(e.__class__.__name__, str(e))
                self.log.critical(
                        'event {0!s}-"{1!s}"'.format(evt.plug_name, error)
                        )
                self._output.quit(error)
                raise

