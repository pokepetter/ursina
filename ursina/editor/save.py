from ursina import *
window.vsync = False

def save(scene_editor, save_new=False):
    if scene_editor.scene_name == 'untitled' and not scene_editor.ask_for_scene_name_window.enabled or save_new:
        scene_editor.ask_for_scene_name_window.enabled = True
        scene_editor.ask_for_scene_name_window.content[0].active = True
        # self.ask_for_scene_name_window.content[1].on_click = Func(self.save)

    if scene_editor.ask_for_scene_name_window.enabled:
        if scene_editor.ask_for_scene_name_window.content[0].text == '':
            print('please enter a scene name')
            return False
        if ' ' in scene_editor.ask_for_scene_name_window.content[0].text:
            print('spaces not allowed')
            return False

        scene_editor.scene_name = scene_editor.ask_for_scene_name_window.content[0].text
        scene_editor.ask_for_scene_name_window.content[0].text = ''
        scene_editor.ask_for_scene_name_window.enabled = False

    scene_editor.scene_folder.mkdir(parents=True, exist_ok=True)
    # create __init__ file in scene folder so we can import it during self.load()
    if not Path(scene_editor.scene_folder / '__init__.py').is_file():
        print('---------------')
        with open(scene_editor.scene_folder / '__init__.py', 'w', encoding='utf-8') as f:
            pass

    print('saving:', scene_editor.scene_name)
    scene_file_content = dedent(f'''
        class Scene(Entity):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
    ''')
    temp_entity= Entity()
    attrs_to_save = ('position', 'rotation', 'scale', 'model', 'origin', 'color', 'texture')

    for e in scene_editor.editor_icons:
        e = e.entity
        scene_file_content += '        ' + e.__class__.__name__ + '(parent=self'

        for i, name in enumerate(attrs_to_save):
            if not getattr(e, name) == getattr(temp_entity, name):
                if name == 'model':
                    model_name = e.model.name
                    scene_file_content += f", model='{model_name}'"
                    continue
                if name == 'color':
                    alpha = f',{e.color.a}' if e.color.a < 1 else ''
                    scene_file_content += f', color=color.hsv({e.color.h},{e.color.s},{e.color.v}{alpha})'.replace('.0,', ',').replace('.0)',')')
                    continue

                value = getattr(e, name)
                if isinstance(value, Vec3):
                    value = str(round(value)).replace(' ', '')
                scene_file_content += f", {name}={value}"

        scene_file_content += ', ignore=True)\n' # TODO: add if it has a custom name

    print('scene_file_content:\n', scene_file_content)
    with open(f'{scene_editor.scene_folder/scene_editor.scene_name}.py', 'w', encoding='utf-8') as f:
        f.write(scene_file_content)




if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    from scene_editor_2 import SceneEditor
    se = SceneEditor()
    se.scene_name = 'test2'
    app.run()
