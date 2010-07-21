from core import simplebot

default_irc_data = {
        'loldata' : 'lolol'}

@simplebot.event_for('ASD')
def evt_asd(self, source, argv, text):
    self.send_msg('LOL', 'asd',  trail=self.irc_data['loldata'])
    
@simplebot.command_for('test')
def do_test(self, chan, source, args):
    self.talk(chan, '{}: {!r}'.format(source, args))
