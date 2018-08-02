from ursina import *
#
# class Player(Entity):
#     def __init__(self):
#         super().__init__()
#
#         self.test = Entity(
#             name = 'weapon',
#             model = 'quad',
#             parent = 'camera.ui'
#             )
#
# game = Ursina()
# player = Player()
# game.run()
# def print_attributes(class):
#     pass
# def print_methods(class):
#     pass
#
# def print_functions(module):
#     pass

import inspect
import ursina

def class_info(classes):
    ignoremethods = (
        'start', 'on_enable', 'on_disable',
        'update', 'input', 'on_mouse_enter',
        'on_mouse_exit', 'on_click', 'destroy'
        )

    info = ''

    for c in classes:
        # try:
        #     print('instantiate:', c[0])
        #     instance = c[1]()
        #     print(vars(instance))
        #     # continue
        # except:
        #     pass

        info += '  * ' + c[0] + '\n'
        allvars = [v for v in vars(c[1]) if not v.startswith('_') and not callable(getattr(c[1], v))]
        for v in allvars:
            info +='     - ' + v + '\n'

        methods = [v for v in allvars
            if not v.startswith('_')
            and v not in ignoremethods
            and callable(getattr(c[1], v))
            ]
        # if len(methods) > 0:
        #     print('\n     methods:')

        for m in methods:
            info += '     - ' + m + '()\n'

        if len(allvars) > 0:
            info += '\n'
    return info


classes = inspect.getmembers(sys.modules['ursina'], inspect.isclass)
prefab_classes = [c for c in classes if c[1].__module__.startswith('ursina.internal_prefabs')]
core_classes = [
    c for c in classes
    if c[1].__module__.startswith('ursina')
    and not c[1].__module__.startswith('ursina.internal_prefabs')
    ]


print('classes in ursina:\n')
# print(class_info(core_classes))
# print(class_info(prefab_classes))
# app = Ursina()
# t = Text(class_info(core_classes))
# t.wordwrap = 50
# t.parent = camera.ui
# t.scale *= .1
# t.x = -.5
# app.run()

# modules = [m for m in sys.modules if m.startswith('ursina')]
# for m in modules:
# m = 'ursina.ursinastuff'
# print('\n*',m)
# funcs = [f for f in dir(sys.modules[m]) if not f.startswith('__')]
# for f in funcs:
#     print('  -', f)
    # modules = [m for m in sys.modules if 'ursina' in m)



class HelpMenu(Entity):
    def __init__(self):
        super().__init__()
        # self.add_script('grid_layout')
        import inspect
        import ursina
        classes = inspect.getmembers(sys.modules['ursina'], inspect.isclass)
        classes = [c for c in classes if c[1].__module__.startswith('ursina')]
        ignoremethods = (
            'start', 'on_enable', 'on_disable',
            'update', 'input', 'on_mouse_enter',
            'on_mouse_exit', 'on_click', 'destroy'
            )
        docstring = ''
        print('classes in ursina:\n')
        for c in classes:
            print('  *', c[0])
            docstring += '\n  <orange>* ' + c[0] + '<>\n'

            allvars = vars(c[1])
            for v in allvars:
                if v.startswith('_'):
                    continue
                if not callable(getattr(c[1], v)):
                    print('     -', v)
                    docstring += '     - ' + v

            methods = [v for v in allvars
                if not v.startswith('_')
                and v not in ignoremethods
                and callable(getattr(c[1], v))
                ]
            if len(methods) > 0:
                print('\n     methods:')
                # docstring += '\n     methods:\n'
                docstring += '<azure>'

            for m in methods:
                print('     -', m+'()')
                docstring += '     -'+ m+'()\n'

            if len(allvars) > 0:
                print('')
                docstring += '\n'


        self.t = Text(class_info(core_classes))
        self.t.wordwrap = 50
        self.t.parent = camera.ui
        self.t.scale *= .1
        self.t.x = -.5


    def input(self, key):
        if key == 'f1':
            self.visible = True
        elif key == 'f1 up':
            self.visible = False

        if self.visible:
            if key == 'scroll down':
                self.t.y += .1
            if key == 'scroll up':
                self.t.y -= .1

if __name__ == '__main__':
    app = Ursina()
    HelpMenu()
    app.run()
