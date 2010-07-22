from .baselex import BaseLexer

class MyLexer(BaseLexer):
    tokens = (
            'NUMBER',
            'STRING_SINGLEQUOTED',
            'ASSIGNMENT',
            'OPERATOR'
            )

    esc_seqs = {'\\\\': '\\', r'\n':'\n', r'\'':'\''}

    def t_newline(self, t):
        r'(?:\r?\n)+'
        t.lexer.lineno += t.value.count('\n')

    t_ignore = ' \t'

    def t_error(self, t):
        t.type = 'ERROR'
        t.value = 'syntax error at line {0}'.format(t.lexer.lineno)
        t.lexer.skip(1)
        return t

    t_OPERATOR = r'\+|\-|\*|/'

    t_ASSIGNMENT = r'='

    def t_NUMBER(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    def t_STRING_SINGLEQUOTED(self, t):
        r"'((\\.)|[^'])*'"
        val = []
        iter_val = iter(t.value[1:][:-1])
        for letter in iter_val:
            if letter == '\\': #if an escape sequence starts...
                esc_val = next(iter_val) #get the second char
                #fix the value, if escape sequence exists
                letter = self.esc_seqs.get(letter+esc_val, esc_val) 
            val.append(letter)
        t.value = ''.join(val)
        return t


if __name__ == '__main__':
    print('Try me')
    lx = MyLexer()
    inp = 'input'
    while inp:
        inp = input('>')
        print(inp)
        lx.write(inp+'\n')
        print('TOK:')
        #[print('\t',x) for x in lx]
        print('TOK END')
    input('DONE!')
