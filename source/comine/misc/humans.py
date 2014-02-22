
from time   import time, localtime, strftime
from re     import match

class Humans(object):
    @staticmethod
    def bytes(value):
        v, ex = value, True
        pref = ['b', 'kb', 'mb', 'gb', 'tb', 'pb', 'eb', 'zb', 'yb']

        def _f(v, exact, x):
            return '%s%.1f%s' % (['', '='][exact], v, pref[x])

        if v < 1024: return '%ib' % v

        for x in xrange(1, len(pref)):
            q, v = (v & 0x3ff, v >> 10)

            ex = ex and q == 0

            if v & 0x3ff == v:
                if v & 0x200: continue

                return _f(v + q / 1024., ex, x)

    @staticmethod
    def delta(time):
        scale = [('s', 60.), ('min', 60.), ('hour', 24.), ('day', 7.),
                    ('week', 4.), ('month', 52.), ('year', None) ]

        for pref, div in scale:
            if not div or time < div:
                return '%0.1f %s' % (time, pref)

            else:
                time /= div

    @staticmethod
    def region(rg):
        return Humans.bytes(rg[1] - rg[0])

    @staticmethod
    def time(when):
        return strftime('%Y-%m-%d %H:%M:%S', localtime(when))

    @staticmethod
    def ago(stamp):
        return Humans.delta(int(time()) - stamp)

    @staticmethod
    def hexdump(s, bpl = 16, ident = 0):
        out = []

        total = (len(s) + bpl - 1) / bpl

        for x in xrange(total):
            out.append(' ' * ident)
            out.append('%3.3x' % (x * bpl,))

            line = s[x*bpl: (x+1)*bpl]

            for y in xrange(len(line)):
                out.append(' %02.2x' % ord(line[y]))

            out.append('   ' * (bpl - y))
            out.append('  ')

            for y in xrange(len(line)):
                if 0x1f < ord(line[y]) < 0x80:
                    out.append(line[y])
                else:
                    out.append('.')

            out.append('\n')

        return ''.join(out)


class From(object):
    __BI_SCALE = { None : 0, 'kb' : 10, 'mb':  20, 'gb': 30, 'tb' : 40,
                    'pb' : 50, 'eb' : 60, 'zb' : 70, 'yb' : 80 }

    @classmethod
    def bytes(cls, line):
        g = match('((?:\d+\.?)?(?:\.\d+)?)(\w+)?', line.strip())

        if g is not None:
            g = g.groups()

            val = int(g[0] or '1')

            if g[1] in cls.__BI_SCALE:
                return val * (1 << cls.__BI_SCALE[g[1]])