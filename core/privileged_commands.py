#!/usr/bin/python3

from .simplebot import command_for, CommandError
from .aaa_stuff import only_if_authed

DEFAULT_IRC_DATA = {
        'ignored': []
        }

@command_for('loadplugin')
def do_loadplugin(bot, chan, source, args):
    only_if_authed(bot, source)
    err = bot.load_ext_module(args[0])
    if err: raise CommandError(err)
    else:
        bot.say(chan, 'plugin loaded successfully')

        
@command_for('reloadplugin')
def do_reloadplugin(bot, chan, source, args):
    only_if_authed(bot, source)
    err = bot.reload_ext_module(args[0])
    if err: raise CommandError(err)
    else:
        bot.say(chan, '{} reloaded successfully'.format(*args))

@command_for('unloadplugin')
def do_unloadplugin(bot, chan, source, args):
    only_if_authed(bot, source)
    err = bot.unload_ext_module(args[0])
    if err: raise CommandError(err)
    else:
        bot.say(chan, '{} unloaded successfully'.format(*args))

@command_for('eval')
def do_eval(bot, chan, source, args):
    only_if_authed(bot, source)
    bot.say(chan, str(eval(' '.join(args))))
