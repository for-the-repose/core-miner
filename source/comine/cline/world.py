#__ LGPL 3.0, 2014 Alexander Soloviev (no.friday@yandex.ru)

from struct import pack

from comine.core.flat   import Flatten
from comine.core.world  import World
from comine.core.base   import ECore
from comine.cline.lib   import CFail, CLines
from comine.maps.tools  import Tools
from comine.misc.humans import Humans, From

@CLines.register
class CWorld(CLines):
    def __init__(s):
        CLines.__init__(s, 'maps')

    def __sub_maps_use(s, infer, argv):
        infer.attach(argv.next())

    def __sub_maps_ring(s, infer, argv):
        world = infer.__world__()

        for rec in world:
            plit = rec.__prov__() or ''

            print " %2u %8s %s" \
                    % (rec.__seq__(), plit, rec.__ring__())

    def __sub_maps_walk(s, infer, argv):
        ring = infer.__world__().by_seq(seq = int(argv.next()))

        print ring

        for span in ring:
            print '  ', span

    def __sub_maps_flat(s, infer, argv):
        short = not(argv.next() == 'full')

        it = Flatten(infer.__world__())

        for seq, (rg, spans, cov) in enumerate(it):
            cont = '%u spans' % len(spans)
            size    = Humans.region(rg)
            place   = Tools.str(rg, digits = 16)

            if seq > 0 and not short: print

            print '-rg=%s %8s %0.2f %0.2f %s' \
                    % ((place, size) + cov + (cont,))

            if short is False:
                spans.sort(key = lambda x: x.__rg__()[0])

                for span in spans:
                    is_core = isinstance(span.exten(), ECore)
                    rlit    = Tools.str(span.__rg__(), digits = 16)
                    slit    = 'Core' if is_core else 'Span'

                    print ' | %s %s' % (slit, rlit)

                    if not is_core:
                        print '  + %s' % (span.desc(prep = ''), )

    def __sub_maps_find(s, infer, argv):
        blob = pack('Q',  int(argv.next(), 0))

        look_heap = (argv.next() == 'heap')
        
        it = infer.__world__().search(blob)

        for seq, (at, offset, span) in enumerate(it):
            rg = span.__rg__()

            print "%2u: %016x, +%08x, %s" \
                    % (seq, at, offset, span)

            if look_heap is True:
                cmd_heap_lookup._lookup(at, '  ')

    def __sub_maps_lookup(s, infer, argv):
        at      = int(argv.next(), 0)
        world   = infer.__world__()

        for offset, rec, span in world.lookup(at):
            print '  %+06x  %s' % (offset, span)

    def __sub_maps_save(s, infer, argv):
        name, base = argv.next(), argv.next()

        world = infer.__world__()

        entity = world.by_path(name)

        if entity is None:
            print 'cannot locate span by path %s' % name

        else:
            res = world.save(entity, base, padd = False)

            if res is not None:
                elit = entity.__class__.__name__

                print 'dumped %s -> (%u ch, %s data, %s padd)' \
                        % (elit, res[0],
                            Humans.bytes(res[1]),
                            Humans.bytes(res[2]))

    def __sub_maps_show(s, infer, argv):
        kind = argv.next()

        if kind in ('unused', 'conflict', 'virtual'):
            kw = dict([(kind, True)])

        elif kind == 'all':
            kw = dict(map(lambda x: (x, True), kind))

        else:
            raise CFail('give one of unused, conflict')

        world = infer.__world__()

        ulits = {
            World.USAGE_UNUSED : 'free',
            World.USAGE_CONFLICT : 'confl',
            World.USAGE_VIRTUAL : 'virt' }

        def _dsingle(rg, spans):
            if len(spans) == 1:
                span = spans[0]

                if span.__rg__() == rg:
                    exten = span.exten()

                    return 'Span' if exten is None else exten.__desc__()

                else:
                    return str(span)

            elif len(spans) > 1:
                return '%u spans' % len(spans)

            else:
                return '-'

        for kind, rg, phys, logic in world.enum(**kw):
            ulit    = ulits.get(kind, '?%x' % kind)
            size    = Humans.region(rg)

            if kind == World.USAGE_UNUSED:
                desc = _dsingle(rg, phys)

            elif kind == World.USAGE_VIRTUAL:
                desc = _dsingle(rg, logic)

            elif kind == World.USAGE_CONFLICT:
                desc = _dsingle(rg, logic)

            else:
                desc = '?'

            print '  %5s %8s %s %s' \
                    % (ulit, size, Tools.str(rg, digits=16), desc)

