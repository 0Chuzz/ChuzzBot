#!/usr/bin/python
#vim:fileencoding=utf-8

from core.simplebot import command_for, CommandError
import urllib
import os.path

lexerpath = os.path.abspath('lexers')

@command_for('lextest')
def do_lextest(self, source, chan, args):
    '''MyLexer <test line here>'''
    lexclass = args.pop(0)
    try:
        lexmodule = __import__("lexers."+lexclass.lower(),
                globals(), locals(), [lexclass])
    except ImportError as e:
        raise CommandError(str(e))
    else:
        lexr = getattr(lexmodule, lexclass)()
        lexr.write(' '.join(args))
        try:
                self.do.say(chan, iter(lexr))
        except Exception as e:
            raise CommandError(str(e))

#@command_for('showlexer')#TODO
def do_showlexer(self, chan, source, args):
    '''<lexer_name>'''
    lexclass = os.path.join(lexerpath, args[0].lower() +'.py')
    lexclass = os.path.normpath(lexclass)
    if not lexclass.startswith(self.lexerpath):
        raise CommandError('invalid file')
    if lexclass not in self.memoized:
        post_text = open(lexclass, 'rb').read()
        post_text = urllib.parse.urlencode({'boh':post_text})
        try:
            post_req = urlib.request.urlopen(self.nopaste, post_text)
        except urllib.error.URLError:
            raise CommandError('unable to upload')
        else:
            link_req = post_req.geturl()
            self.memoized[lexclass] = link_req
    self.talk(chan, 
            '{}, {}'.format(source.nick, self.memoized[lexclass]))
            


