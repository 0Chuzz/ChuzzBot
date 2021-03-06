#!/usr/bin/env python

import logging
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
        self.plug_load()

    def __del__(self):
        self.plug_unload()
    
    def plug_load(self):
        pass

    def start(self):
        pass

    def plug_unload(self):
        pass

    def evt_check(self, message):
        return self.evt_call

    def evt_call(self,message):
        pass

    def on_error(self, errmsg):
        pass

class MainPlug(Pluggable):
    plug_name = 'Main'

def event_for(*params):
    def event_factor(func):
        def evt_check(self, message):
            if message.command in params:
                return self.evt_call
            else:
                return None
        def evt_call(self, message):
            func(self, message)
        nspace = dict(__doc__=func.__doc__, plug_name=func.__name__,
                evt_check=evt_check, evt_call=evt_call)
        return type(func.__name__,(Pluggable,), nspace)
    return event_factor


def command_for(command_name):
    def command_factor(func):
        def plug_load(self):
            myattr = getattr(self, "comm_" + command_name)
            self.plugins["commands"].register(command_name, myattr)
        def plug_unload(self):
            self.plugins["commands"].register(command_name)
        nspace = dict(plug_name=func.__name__, plug_load=plug_load,
                plug_unload=plug_unload)
        nspace['comm_' + command_name] = func
        return type(func.__name__, (Pluggable,), nspace)
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
            'core.aaa_stuff', 'core.privileged_commands')

    def __init__(self, irc_parser, irc_data, modules=tuple()):
        self._irc_parser = irc_parser
        self.send_msg = self._irc_parser.bind_events(
                    self.on_connect, self.event
                    )
        self.irc_data = irc_data
        self._modules = {}
        self.plugins = weakref.WeakValueDictionary()
        self._output = ChatOutput(self.send_msg)
        self.log = logging.getLogger('IRC bot')

        mainplug = MainPlug(self._output, self.plugins, self.irc_data)
        mainplug.load_mod = self.load_ext_module
        mainplug.unload_mod = self.unload_ext_module
        mainplug.reload_mod = self.reload_ext_module
        self.plugins['main'] = mainplug

        modules = self.DEFAULT_MODULES + modules
        for module in modules:
            self.load_ext_module(module)

    def __getattr__(self, attr_name):
        return getattr(self._irc_parser, attr_name)

    def on_connect(self):
        self.log.debug("start fired. starting {0!s}".format(
            self.plugins.keys()))
        for pname, plugin in self.plugins.iteritems():
            try:
                plugin.start()
            except Exception as e:
                self.log.exception("on " + " start")
                exit()

    def load_ext_module(self, module_name):
        self.log.debug("loading " + module_name)
        if module_name in self._modules:
            self.log.warning(module_name + 'already loaded')
            return
        try:
            #recursively load packag, [])s
            mdle = __import__(module_name) 
            for package in module_name.split('.')[1:]:
                mdle = getattr(mdle, package)
        except ImportError as e:
            self.log.exception(str(e))
            return

        self.log.debug(repr(mdle))
        if hasattr(mdle, 'DEFAULT_IRC_DATA'):
            for option in mdle.DEFAULT_IRC_DATA.iteritems():
                self.irc_data.setdefault(*option)
        
        #load plugins
        mdle_plugins = []
        for stuffname, stuff in  vars(mdle).iteritems():
            if not hasattr(stuff, 'plug_name') or not stuff.plug_name:
                continue
            try:
                plugg = stuff(self._output, self.plugins, self.irc_data)
            except Exception:
                err = "{0} in {1} cannot be loaded"
                self.log.exception(err.format(stuffname, module_name))
                self.log.debug(dir(mdle))
                exit()
            self.plugins[stuff.plug_name] = plugg
            mdle_plugins.append(plugg)
            self.log.debug('loaded ' + stuff.plug_name)

        self._modules[module_name] = (mdle,mdle_plugins)


    def unload_ext_module(self, module_name):
        try:
            del self._modules[module_name]
        except KeyError:
            self.log.error("unload {0}: no such module".format(module_name))
        else:
            self.log.debug('unload {0}: success'.format(module_name))

    def reload_ext_module(self, module_name):
        self.unload_ext_module(module_name)
        self.load_ext_module(module_name)

    def event(self, message):
        for evt in self.plugins.values():
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

