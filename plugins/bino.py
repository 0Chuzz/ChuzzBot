from itertools import izip_longest as izip
from core.simplebot import command_for, CommandError

def my_bino(n, k):
    ret = 1
    for u, d in izip(xrange(n, n-k, -1), xrange(1, k+1), fillvalue=1):
        ret *= u; ret /= d
    return ret


def my_tartaglia(size):
    return ("\n".join(" ".join(str(my_bino(i, x)).center(3) for x in
            xrange(i+1)).center(size*4) for i in xrange(size)))


def test_bino(x): 
    assert sum(my_bino(x,a) for a in xrange(x+1)) == 2**x

@command_for('bino')
def binomial(self, who, where, args):
    try:
        n, k = map(int, args)
    except:
        raise CommandError("invalid values")
    if k > 1000 or n > 1000:
        self.do.say(where, "NO U")
    else:
        self.do.say(where,str( my_bino(n, k)))


@command_for("tartaglia")
def tartaglia(self, who, where, args):
    try:
        n = int(args.pop())
    except:
        raise CommandError("invalid argument")
    if "all" in args:
        maxline = 30
        result = my_tartaglia
    else:
        maxline = 300
        result = lambda n: " ".join(str(my_bino(n, i)) for i in xrange(n + 1))
    if n > maxline:
        self.do.say(where, "NO U")
    else:
        self.do.say(where, result(n))
