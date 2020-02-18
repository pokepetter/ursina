# this will clear the scene and try to execute the main.py code without
# restarting the program


from ursina import *
import time
import ast


def is_valid_python(code):
   try:
       ast.parse(code)
   except Exception as e:
       return False, e

   return True


def make_code_reload_safe(code):
    newtext = ''
    dedent_next = False

    for line in code.split('\n'):
        if line.strip().endswith('Ursina()') or line.strip().endswith('app.run()') or line.strip().endswith('HotReloader()'):
            continue
        if 'eternal=True' in line:
            continue
        if line.startswith('''if __name__ == '__main__':'''):
            dedent_next = True
            continue
        if line.strip().startswith('#'):
            continue

        if dedent_next:
            newtext += dedent(line) + '\n'
        else:
            newtext += line + '\n'

    return newtext



class HotReloader(Entity):
    def __init__(self, path=__file__, **kwargs):
        super().__init__()
        self.eternal = True
        self.ignore_paused = True
        self.path = path

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.path = Path(self.path)
        self.realtime_editing = False   # toggle with f8
        # self.text_editor = InGameTextEditor(path=self.path, enabled=False)


    def input(self, key):
        if key == 'f5':
            # if self.text_editor.enabled:
            #     self.text_editor.reload()
            # else:
            self.reload()

        if key == 'f6':
            self.reload_texture()

        if key == 'f7':
            self.reload_model()

        if key == 'f8':
            self.realtime_editing = not self.realtime_editing


                # overwrite specific line
                # with open(info.filename, 'r') as f:
                #     lines = f.readlines()
                # lines[info.lineno] = 'OVERWRITTEN!'
                # with open(info.filename, 'w') as f:
                #     f.writelines(lines)

        # if key == '|':
        #     if not self.text_editor.enabled:
        #         invoke(setattr, self.text_editor, 'enabled', not self.text_editor.enabled, delay=.1)
        #     else:
        #         self.text_editor.enabled = not self.text_editor.enabled

    def update(self):
        if self.realtime_editing:
            self.hot_reload()



    def hot_reload(self):
        for e in [e for e in scene.entities if not e.eternal]:
            try:
                with open(e.line_definition.filename, 'r') as f:
                    # print(f.readlines())
                    code = f.readlines()[e.line_definition.lineno-1]

                # code = e.line_definition.code_context[0]
                # print(e,
                #     Path(info.filename).name,
                #     info.lineno, info.code_context)
                    print('---', code)
                    if '(' in code and ')' in code and code.count('(') == code.count(')'):
                        code = code.split('(', 1)[1][:-2]
                        code = code.split(',')
                        for arg in code:
                            name, value = arg.split('=')
                            name = name.strip()
                            value = value.strip()
                            print(name, eval(value))
                            setattr(e, name, eval(value))
            except:
                pass


    def reload(self, reset_camera=True):
        if not self.path.exists:
            print('trying to reload, but path does not exist:', self.path)
            return


        with open(self.path, 'r') as file:
            text = file.read()
            text = make_code_reload_safe(text)


        if not is_valid_python(text):
            print('invalid python code')
            return

        scene.clear()
        if reset_camera:
            camera.position = (0, 0, -20)

        t = time.time()
        try:
            exec(text)
        except Exception as e:
            print(e)
        #     for l in text.split('\n'):
        #         try:
        #             exec(l.strip())
        #         except:
        #             pass
        print('reloaded in:', time.time() - t)


    def reload_texture(self):
        textured_entities = [e for e in scene.entities if e.texture]
        for e in textured_entities:
            if e.texture.path.parent.name == application.compressed_textures_folder.name:
                print('texture is made from .psd file', e.texture.path.stem + '.psd')
                compress_textures(e.texture.path.stem)
            print('reloaded texture:', e.texture.path)
            e.texture._texture.reload()


    def reload_model(self):
        entities = [e for e in scene.entities if e.model and hasattr(e.model, 'path')]
        unique_paths = list(set([e.model.path for e in entities]))
        # ignore internal models
        unique_paths = [e for e in unique_paths if not str(application.package_folder).lower() in str(e).lower()]
        print(unique_paths)

        for model_path in unique_paths:
            if model_path.parent.name == application.compressed_models_folder.name:
                # print('model is made from .blend file', model_path.stem + '.blend')
                # print('try compres:', model_path.parent.parent, model_path.stem)
                compress_models(path=model_path.parent.parent, name=model_path.stem)
                print(f'compressed {model_path.stem} .blend sucessfully')

        for e in entities:
            if e.model.path.parent.parent == application.internal_models_folder:
                continue
            e.model = load_model(e.model.path.stem)
            # print('reloaded model:', e.model.path)


# class InGameTextEditor(Entity):
#     def __init__(self, path, **kwargs):
#         super().__init__(parent=camera.ui, z=-10)
#         self.file_path = path
#
#         self.add_script(Scrollable(min=0, max=10))
#         self.bg = Entity(parent=self, model='quad', scale_x=camera.aspect_ratio, color=color.color(0,0,0,.9), z=1, collider='box', origin_y=.5, y=.5, scale_y=10, eternal=True)
#         self.header = Text(parent=self, x=-.5, y=.475, text=self.file_path.name)
#         self.text_editor = TextField(parent=self, font_size=14, max_lines=50)
#         self.text_editor.text_entity.text_colors['default'] = color.color(219, .0, .95)
#         self.text_editor.text_entity.text_colors['class_color'] = color.color(40, .61, .9)
#         self.text_editor.text_entity.text_colors['kw_color'] = color.color(210, .59, .94)
#         self.text_editor.text_entity.text_colors['func_color'] = color.color(250, .46, .87)
#         self.text_editor.text_entity.text_colors['param_clor'] = color.color(30, .71, .92)
#         self.text_editor.text_entity.text_colors['string_color'] = color.color(90, .48, .86)
#
#
#         self.text_editor.replacements = {
#
#             'from ':    f'☾kw_color☽from ☾default☽',
#             'import ':  f'☾kw_color☽import ☾default☽',
#             'def ':     f'☾kw_color☽def ☾default☽',
#             'for ':     f'☾kw_color☽for ☾default☽',
#             'if ':      f'☾kw_color☽if ☾default☽',
#             ' in ':     f'☾kw_color☽ in ☾default☽',
#
#             'print(':   f'☾func_color☽print☾default☽(',
#             'range(':   f'☾func_color☽range☾default☽(',
#             '__init__': f'☾func_color☽__init__☾default☽',
#             'super':    f'☾func_color☽super☾default☽',
#
#             'class ':   f'☾class_color☽class ☾default☽',
#             'Entity':   f'☾lime☽Entity☾default☽',
#             'self.':    f'☾class_color☽self☾default☽.',
#             '(self)':   f'(☾class_color☽self☾default☽)',
#             'self,':    f'☾class_color☽self☾default☽,',
#
#             'highlight_color = ':    f'☾param_clor☽highlight_color☾default☽ = ',
#
#             '\',':    f'\',☾default☽',   # end quote
#             '\':':    f'\':☾default☽',   # end quote
#             '\')':    f'\')☾default☽',   # end quote
#             '\'':    f'☾string_color☽\'', # start quote
#             }
#
#         self.eternal = True
#         self.ignore_paused = True
#
#         with self.file_path.open() as f:
#             self.text_editor.text = f.read()
#             self.text_editor.render()
#
#
#         for key, value in kwargs.items():
#             setattr(self, key, value)
#
#
#     def on_enable(self):
#         application.pause()
#         self.ignore_input = False
#
#
#     def on_disable(self):
#         application.resume()
#         self.ignore_input = True
#
#
#     def input(self, key):
#         if held_keys['control'] and key == 'enter':
#             if self.reload():
#                 if held_keys['shift']:
#                     self.enabled = False
#
#
#     def reload(self):
#         cleaned_text = make_code_reload_safe(self.text_editor.text)
#
#         try:
#             scene.clear()
#             exec(cleaned_text)
#             print('...............')
#             print(cleaned_text)
#             print('...............')
#             return True
#         except Exception as e:
#             # exception = is_valid_python(cleaned_text)
#             if type(e) == SyntaxError:
#                 print('Error on line:', e)
#             else:
#                 import traceback
#                 error_message = traceback.format_exc()
#                 print(error_message)
#
#             return False
#


if __name__ == '__main__':
    from ursina import *
    window.set_z_order(window.Z_top)
    app = Ursina()
    # hot_reloader = HotReloader()
    application.hot_reloader.path = application.asset_folder.parent.parent / 'samples' / 'platformer.py'
    # Sky()

    '''
    By default you can press F5 to reload the starting script, F6 to reimport textures and F7 to reload models.
    '''
    # window.size *= .5
    # window.position += Vec2(1000,400)
    # butttt = Button(text='test_buttonsss', x=.0, y=.0, color=color.red)

    app.run()
