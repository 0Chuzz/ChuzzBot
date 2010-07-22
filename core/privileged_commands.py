#!/usr/bin/python3

from .simplebot import command_for, CommandError

DEFAULT_IRC_DATA = {
        'ignored': []
        }

@command_for('loadplugin')
def do_loadplugin(bot, source, chan, args):
    bot.plugins['auth'].check_authed(source)
    bot.plugins['main'].load_mod(args[0])
    bot.do.say(chan, 'plugin loaded successfully')

        
@command_for('reloadplugin')
def do_reloadplugin(bot, source, chan, args):
    bot.plugins['auth'].check_authed(source)
    bot.plugins['main'].reload_mod(args[0])
    bot.do.say(chan, '{0} reloaded successfully'.format(*args))

@command_for('unloadplugin')
def do_unloadplugin(bot, source, chan, args):
    bot.plugins['auth'].check_authed(source)
    bot.plugins['main'].unload_mod(args[0])
    bot.do.say(chan, '{0} unloaded successfully'.format(*args))

@command_for('eval')
def do_eval(bot, source, chan, args):
    bot.plugins['auth'].check_authed(source)
    bot.do.say(chan, str(eval(' '.join(args))))
