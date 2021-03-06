#__ LGPL 3.0, 2014 Alexander Soloviev (no.friday@yandex.ru)

import gdb

from re     import match

from comine.iface.infer import ILayout
from comine.misc.types  import Types

class ECall(Exception): pass


class Tools(object):
    __slots__ = ('_Tools__space', '_Tools__gin', '_Tools__exec')

    def __enter(func):
        def _wrap(tool, *kl, **kw):
            with tool():
                return func(tool, *kl, **kw)

        return _wrap

    def __init__(s, gin = None):
        s.__gin     = Types.ensure(gin, gdb.Inferior, none = True)
        s.__exec    = gdb.execute

    def __gin__(s):     return s.__gin

    def __sel__(s):     return gdb.selected_inferior()

    def __call__(s):
        if s.__gin is None:
            raise Exception('tools has no attached infer')

        return _Enter(s)

    def call(s, cmd):
        try:
            return s.__exec(cmd, to_string = True)

        except gdb.error as E:
            raise ECall('catched="%s" for "%s"' % (str(E), cmd))

    def arch(s):
        line = s.call('show architecture')

        g = match('.*\(currently ([^ ]+)\).*', line)

        if g is not None:
            return g.group(1)

    def version(s):
        for line in s.call('show version').split('\n'):
            m = match('GNU gdb \([^)]+\) (.+)', line)

            if m is not None:
                g = match('(\d+)\.(\d+)(?:\.(\d+))?(.*)', m.group(1))

                if g is not None:
                    _conv = lambda x: x if x is None else int(x)

                    ver = tuple(map(_conv, g.groups()[:3]))

                    return ('gdb', ver, g.group(4))

    @__enter
    def attach(s, pid):
        pid = Types.ensure(pid, int)

        s.call('attach %u' %pid)

    @__enter
    def load(s, layout):
        layout = Types.ensure(layout, ILayout)

        if layout.__root__() is not None:
            debug = '%s/usr/lib/debug' % layout.__root__()

            s.call('set solib-absolute-prefix %s' %  layout.__root__())
            s.call('set debug-file-directory %s' % debug)

        s.call('set auto-load safe-path /')
        s.call('file %s' % layout.__binary__())
        s.call('core-file %s' % layout.__core__())

    def switch(s, num):
        s.call('inferior %u' % Types.ensure(num, (int, long)))

        assert s.__sel__().num == num

    def make(s):
        out = s.call('add-inferior')

        g = match('.*inferior (\d+)', out)

        if g is None:
            raise Exception('Unexpected gdb resp "%s"' % out)

        else:
            num = int(g.group(1))

            gins = filter(lambda x: x.num == num, gdb.inferiors())

            if len(gins) == 0:
                raise Exception('cannot find just created gin=%u' % num)

            elif len(gins) > 1:
                raise Exception('too much gins with num=%u found' % num)

            else:
                return gins[0]


class _Enter(object):
    __slots__ = ('_Enter__tools', '_Enter__was')

    def __init__(s, tools):
        s.__tools   = tools
        s.__was     = None

    def __enter__(s):
        sel = s.__tools.__sel__()
        gin = s.__tools.__gin__()

        if sel is None or sel != gin:
            s.__was = sel

            s.__tools.switch(gin.num)

        else:
            s.__was = None

    def __exit__(s, Et, Ev, tb):
        if s.__was is not None:
            s.__tools.switch(s.__was.num)

            s.__was = None
