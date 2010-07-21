from core.simplebot import event_for, Pluggable

DEFAULT_IRC_DATA = {
        'nick' : "ChuzzBot",
        'user' : "bot_user",
        'info' : "Python Bot",
        'chans' : [],
        'motd' : ''
        }

class DefaultStartup(Pluggable):
    plug_name = "bot_startup"
    def start(self):
        #NICK botnick\r\n
        print "***SENDING NICK ***"
        self.do.nick(self.data['nick'])
        #USER bot_user 0 irc.server.on :bot info (or real name?)
        self.do.user(self.data['user'], '0', '*', self.data['info'])


@event_for('STARTOFMOTD', 'MOTD', 'MOTD2')
def save_motd(bot, message):
    bot.data['motd'] += message.trail

@event_for('NOMOTD', 'ENDOFMOTD')
def join_chans(bot, message):
    for chan in bot.data['chans']:
        bot.do.join(chan)

@event_for('NICKNAMEINUSE')
def on_nicknameinuse(bot, message):
    bot.data['nick'] += '_'
    bot.do.nick(bot.data['nick'])

@event_for('JOIN')
def greetz(bot, message):
    if message.source.nick == bot.data['nick']:
        bot.do.say(message.trail, 'hi all!')
    else:
        bot.do.say(message.trail, 
                'hello {0}!'.format(message.source.nick))

@event_for('PING')
def ping_reply(bot, message):
    bot.do.raw('PONG', message.trail)


@event_for('KICK')
def autorejoin(bot, message):
    kicked = message.arguments[1]
    chan = message.arguments[0]
    if kicked == bot.data['nick']:
        bot.do.join(chan)
        if message.source.is_user:
            bot.do.say(chan, message.source.nick + 
                    " mi ha kickato e sono triste :(")
    return


