#__ LGPL 3.0, 2014 Alexander Soloviev (no.friday@yandex.ru)

from comine.core.space  import Space
from comine.iface.infer import LayoutError
from comine.iface.bugs  import IBug
from comine.core.layout import Layout
from comine.core.bugs   import Bugs
from comine.cline.lib   import CLines

@CLines.register
class CMaint(CLines):
    def __init__(s):
        CLines.__init__(s, 'comine')

    def __sub_comine_info(s, infer, argv):
        info = Space().info()

        print 'Comine, core miner tool extension for GNU gdb'
        print 'GPLv3, copyright 2013-2014 Alexander Soloviev'

        if info is None:
            print 'Using with unknown runtime'

        else:
            ver = '%u.%u.%s' % info[1]

            print 'Using with %s %s%s runtime' \
                        % (info[0], ver, info[2])

    def __sub_comine_open(s, infer, argv):
        try:
            layout = Layout(argv.next())

        except LayoutError as E:
            print E

        else:
            Space().open(layout)

    def __sub_comine_attach(s, infer, argv):
        Space().open(int(argv.next()))

    def __sub_comine_this(s, infer, argv):
        Space().open(None)

    def __sub_comine_boot(s, infer, argv):
        Space().boot(fresh = (argv.next() == 'reload'))

    def __sub_comine_bugs(s, infer, argv):
        for bug in Bugs().check():
            name, rg = bug.__ver__()

            if rg == (None, None):
                vlit = 'all'

            elif rg[0] == None:
                vlit = '< %s' % IBug.vlit(rg[1])

            elif rg[1] == None:
                vlit = '> %s' % IBug.vlit(rg[0])

            else:
                vlit = '%s - %s' % tuple((map(IBug.vlit, rg)))

            print '%08s %16s  %s' % (name, vlit, bug)
