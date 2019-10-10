# this will clear the scene and try to execute the main.py code without
# restarting the program


from ursina import *
import time
import ast


def is_valid_python(code):
   try:
       ast.parse(code)
   except SyntaxError:
       return False
   return True


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


    def reload(self, reset_camera=True):
        if not self.path.exists:
            print('trying to reload, but path does not exist:', self.path)
            return


        newtext = ''
        with open(self.path, 'r') as file:
            text = file.read()
            dedent_next = False

            for line in text.split('\n'):
                # if line.startswith('from ursina'):
                #     continue
                if 'Ursina()' in line or 'app.run()' in line or 'HotReloader(' in line:
                    continue
                if 'eternal=True' in line:
                    continue
                if line.startswith('''if __name__ == '__main__':'''):
                    dedent_next = True
                    continue

                if dedent_next:
                    newtext += dedent(line) + '\n'
                else:
                    newtext += line + '\n'

        # print(newtext)
        if not is_valid_python(newtext):
            print('invalid python code')
            return

        scene.clear()
        if reset_camera:
            camera.position = (0, 0, -20)

        t = time.time()
        try:
            exec(newtext)
        except:
            for l in newtext.split('\n'):
                try:
                    exec(l.strip())
                except:
                    pass
        print('reloaded in:', time.time() - t)


    def reload_texture(self):
        textured_entities = [e for e in scene.entities if e.texture]
        for e in textured_entities:
            if e.texture.path.parent.name == 'compressed':
                print('texture is made from .psd file', e.texture.path.name.split('.')[0] + '.psd')
                compress_textures(e.texture.path.name.split('.')[0])
            print('reloaded texture:', e.texture.path)
            e.texture._texture.reload()



if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    hotreloader = HotReloader()
    hotreloader.path = application.asset_folder.parent.parent / 'samples' / 'platformer.py'

    '''
    By default you can press Ctrl+R to reload the starting script and Ctrl+T to reimport textures.
    '''

    def input(key):
        if held_keys['control'] and key == 'r':
            print('reload textures')
            reload_texture()

    def reload():
        print(window.getZOrder())
        # hotreloader.reload(reset_camera=False)
        invoke(reload, delay=1)

    reload()




    app.run()
