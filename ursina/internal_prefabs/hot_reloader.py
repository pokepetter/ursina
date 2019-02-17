# this will clear the scene and try to execute the main.py code without
# restarting the program


from ursina import *

class HotReloader(Entity):
    def __init__(self, path=__file__, **kwargs):
        super().__init__()
        self.eternal = True
        self.path = path

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.path = Path(self.path)

    def input(self, key):
        if held_keys['control'] and key == 'r':
            self.reload()

        if held_keys['control'] and key == 't':
            self.reload_texture()


    def reload(self):
        if not self.path.exists:
            print('trying to reload, but path does not exist:', self.path)
            return

        scene.clear()

        newtext = ''
        with open(self.path, 'r') as file:
            text = file.read()
            dedent_next = False

            for line in text.split('\n'):
                if line.startswith('from ursina'):
                    continue
                if 'Ursina()' in line or 'app.run()' in line or 'HotReloader(' in line:
                    continue
                if line.startswith('''if __name__ == '__main__':'''):
                    dedent_next = True
                    continue

                if dedent_next:
                    newtext += dedent(line) + '\n'
                else:
                    newtext += line + '\n'

        print(newtext)
        try:
            exec(newtext)
        except Exception as e:
            print(e)


    def reload_texture(self):
        textured_entities = [e for e in scene.entities if e.texture]
        for e in textured_entities:
            if e.texture.path.parent.name == 'compressed':
                print('texture is made from .psd file', e.texture.path.name.split('.')[0] + '.psd')
                compress_textures(e.texture.path.name.split('.')[0])
            print('reloaded texture:', e.texture.path)
            e.texture._texture.reload()


class ModelReloader(Entity):
    def __init__(self):
        super().__init__()
        self.parent = camera.ui
        self.i = 0
        self.position = window.top_left
        self.title = Text(parent=self, text='<azure>models:', background=True)


    def check_if_changed(self):
        [destroy(e) for e in self.children if not e == self.title]

        for filetype in ('.bam', '.ursinamesh'):
            for filename in application.asset_folder.glob(f'**/*{filetype}'):
                # b = Button(text='yolo')
                t = Button(
                    parent = self,
                    origin = (-.5, .5),
                    scale = (.3, .025),
                    text = str(filename)[len(str(application.asset_folder))+1:],
                    background = True,
                    y = -len(self.children)*.025
                    )
                t.text_entity.origin = (-.5, 0)
                t.text_entity.position = (0, 0)

                # last_changed = os.stat(filename).st_mtime
                # print(last_changed)
                t.text_entity.text = ' <orange>' + t.text_entity.text
                # t.background = True

        # print(models)
    def update(self):
        if self.i > 60:
            self.check_if_changed()
            self.i = 0

if __name__ == '__main__':
    app = Ursina()
    # Entity(model='hexagon')
    # Entity(model=Circle())
    Sprite('brick')
    # ModelReloader()
    app.hotreloader = HotReloader()
    app.hotreloader.path = application.asset_folder / 'platformer.py'
    app.run()
