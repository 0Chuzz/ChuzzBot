import ply.lex as lex

class BaseLexer:
    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def write(self, data):
        self.lexer.input(data)

    def read(self, len = None):
        tok_iter = iter(self)
        if len is None:
            return list(tok_iter)
        ret = []
        for x in xrange(len):
            ret.append(next(tok_iter))
        return ret

    def __iter__(self):
        tok = self.lexer.token()
        while tok:
            yield tok
            tok = self.lexer.token()

