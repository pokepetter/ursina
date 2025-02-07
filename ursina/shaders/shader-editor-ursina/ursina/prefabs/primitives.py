from ursina import *

model_names = ('quad', 'cube', 'sphere', 'plane')

for colorname in color.color_names:
    for modelname in model_names:
        procedural_code = dedent(f'''
            class {colorname.capitalize()}{modelname.capitalize()}(Entity):
                def __init__(self, **kwargs):
                    super().__init__()
                    self.model = '{modelname}'
                    self.color = color.{colorname}
                    for key, value in kwargs.items():
                        setattr(self, key, value)
            ''')
        exec(procedural_code)


if __name__ == '__main__':
    '''procedurally generate classes like RedCube, GreenCube, BlueSphere and so on.'''
    from primitives import *
    app = Ursina()
    RedCube()
    VioletSphere(x=1)
    YellowCube(x=2, scale=(10,1,10), texture='white_cube', texture_scale=(10,10))
    app.run()
