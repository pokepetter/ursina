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

import inspect
import ursina
classes = inspect.getmembers(sys.modules['ursina'], inspect.isclass)
classes = [c for c in classes if c[1].__module__.startswith('ursina')]
ignoremethods = (
    'start', 'on_enable', 'on_disable',
    'update', 'input', 'on_mouse_enter',
    'on_mouse_exit', 'on_click', 'destroy'
    )

print('classes in ursina:\n')
for c in classes:
    print('  *', c[0])
    allvars = vars(c[1])
    for v in allvars:
        if v.startswith('_'):
            continue
        if not callable(getattr(c[1], v)):
            print('     -', v)

    methods = [v for v in allvars
        if not v.startswith('_')
        and v not in ignoremethods
        and callable(getattr(c[1], v))
        ]
    if len(methods) > 0:
        print('\n     methods:')

    for m in methods:
        print('     -', m+'()')

    if len(allvars) > 0:
        print('')


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


        self.t = Text(docstring)
        self.t.wordwrap = 50
        self.t.parent = camera.ui
        self.t.scale *= .1
        self.t.x = -.5
        # for c in classes:
        #     b = Button(
        #         parent = self,
        #         text = c[0],
        #         scale_x = 2
        #         )
        #     b.scale *= .1
        #     b.text_entity.scale *= 10
        #     b.text_entity.x = -.25
        #
        #     classinfo = ''
        #     allvars = vars(c[1])
        #     for v in allvars:
        #         if v.startswith('_'):
        #             continue
        #         if not callable(getattr(c[1], v)):
        #             print('     -', v)
        #             classinfo += '\n     - ' + v
        #
        #     methods = [v for v in allvars
        #         if not v.startswith('_')
        #         and v not in ignoremethods
        #         and callable(getattr(c[1], v))
        #         ]
        #     for m in methods:
        #         print('     -', m+'()')
        #         classinfo += '     -'+ m+'()\n'
        #
        #     b.tooltip = Text(text=classinfo, background=True, enabled=False)
        #     b.tooltip.parent = b
        #     b.tooltip.position = (0,0,-1)
        #
        # self.add_script('grid_layout')
        # self.grid_layout.max_x = 4
        # self.grid_layout.update_grid()
        # self.x = -.25
        # self.model = None

        # self.origin = (-.5, .5)

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
