# from pandaeditor.main import PandaEditor
#
import pandaeditor
from pandaeditor.entity import Entity
from pandaeditor import main
app = main.PandaEditor()
app.run()
# from pandaeditor.application import *
# from pandaeditor.pandastuff import *
# import pandaeditor.application
# from pandaeditor.main import PandaEditor
# app = pandaeditor.main.PandaEditor()
# app.run()
# import sys
# for m in sorted(sys.modules.keys()):
#     print(m)
# print(pandaeditor.__modules__)

# import sys
# import sys
# mods = [m.__name__ for m in sys.modules.values() if m]
# for m in sorted(mods):
#     print(m)

# import pkgutil
# package = pandaeditor
# for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
#     print ("Found submodule %s (is a package: %s)" % (modname, ispkg))
