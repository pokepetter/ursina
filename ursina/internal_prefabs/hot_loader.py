# this will clear the scene and try to execute the main.py code without
# restarting the program


from ursina import *

class HotLoader(Entity):
    def __init__(self):
        super().__init__()
        self.eternal = True
        self.file_path = Path(__file__)


    def input(self, key):
        if held_keys['control'] and key == 'r':
            self.reload()


    def reload(self):
        if not self.file_path.exists:
            return

        scene.clear()

        with open(self.file_path, 'r') as file:
            # print(file.read())
            text = file.read()
            newtext = ''
            for line in text.split('\n'):
                if line.startswith('from ursina') or 'Ursina()' in line or 'app.run()' in line:
                    continue
                newtext += line + '\n'

            exec(newtext)


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
    # ModelReloader()
    app.hotloader = HotLoader()
    app.hotloader.file_path = application.asset_folder / 'platformer.py'
    app.run()
