from ursina.editor.level_editor import *


class PipeEditor(Entity):
    def __init__(self, points=[Vec3(0,0,0), Vec3(0,1,0)], **kwargs):
        super().__init__(original_parent=LEVEL_EDITOR, selectable=True, name='Pipe', **kwargs)
        LEVEL_EDITOR.entities.append(self)
        self._point_gizmos = LoopingList([Entity(parent=self, original_parent=self, position=e, selectable=False, name='PipeEditor_point', is_gizmo=True) for e in points])
        self.model = Pipe()
        self.edit_mode = False
        self.add_collider = False
        self.generate()


    def generate(self):
        self.model = Pipe(
            path = [e.get_position(relative_to=self) for e in self._point_gizmos],
            thicknesses = [e.scale.xz for e in self._point_gizmos]
        )
        self.texture = 'grass'

        if self.add_collider:
            self.collider = self.model


    def __deepcopy__(self, memo):
        return eval(repr(self))


    @property
    def points(self):
        return [e.position for e in self._point_gizmos]

    @property
    def edit_mode(self):
        return self._edit_mode

    @edit_mode.setter
    def edit_mode(self, value):
        # print('set edit mode', value)
        self._edit_mode = value
        if value:
            [setattr(e, 'selectable', False) for e in LEVEL_EDITOR.entities if not e == self]
            for e in self._point_gizmos:
                if not e in LEVEL_EDITOR.entities:
                    LEVEL_EDITOR.entities.append(e)

            [setattr(e, 'selectable', True) for e in self._point_gizmos]
        else:
            [LEVEL_EDITOR.entities.remove(e) for e in self._point_gizmos if e in LEVEL_EDITOR.entities]
            [setattr(e, 'selectable', True) for e in LEVEL_EDITOR.entities]
            if True in [e in LEVEL_EDITOR.selection for e in self._point_gizmos]: # if point is selected when exiting edit mode, select the poke shape
                LEVEL_EDITOR.selection = [self, ]

        LEVEL_EDITOR.render_selection()


    def input(self, key):
        combined_key = input_handler.get_combined_key(key)
        if combined_key == 'tab':
            if self in LEVEL_EDITOR.selection or True in [e in LEVEL_EDITOR.selection for e in self._point_gizmos]:
                self.edit_mode = not self.edit_mode
                return

        elif key == '+' and len(LEVEL_EDITOR.selection) == 1 and LEVEL_EDITOR.selection[0] in self._point_gizmos:
            print('add point')
            i = self._point_gizmos.index(LEVEL_EDITOR.selection[0])
        
            new_point = Entity(parent=self, original_parent=self, position=lerp(self._point_gizmos[i].position, self._point_gizmos[i+1].position, .5), selectable=True, is_gizmo=True)
            LEVEL_EDITOR.entities.append(new_point)
            self._point_gizmos.insert(i+1, new_point)
            LEVEL_EDITOR.render_selection()

        elif key == 'space':
            self.generate()

        elif self.edit_mode and key.endswith(' up'):
            invoke(self.generate, delay=3/60)


if __name__ == '__main__':

    app = Ursina(borderless=False)

    level_editor = LevelEditor()
    level_editor.goto_scene(0,0)
    # cube = WhiteCube(selectable=True)
    level_editor.entities.append(PipeEditor())
    app.run()
