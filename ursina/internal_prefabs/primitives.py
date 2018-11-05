from ursina import *

# from ursina.internal_prefabs import procedural_models
# import inspect
# model_names = inspect.getmembers(procedural_models, inspect.isclass)
# model_names = [e[0] for e in class_names if str(e[1].__module__) == 'ursina.internal_prefabs.procedural_models']
model_names = ('quad', 'cube', 'sphere', 'plane', 'pyramid')

for colorname in color.color_names:
    for modelname in model_names:
        procedural_code = f'''
class {colorname.capitalize()}{modelname.capitalize()}(Entity):
    def __init__(self, **kwargs):
        super().__init__()
        self.model = '{modelname}'
        self.color = color.{colorname}
        for key, value in kwargs.items():
            setattr(self, key, value)
'''
        # try:
        exec(procedural_code)
        #     print(colorname.capitalize() + modelname.capitalize())
        # except:
        #     print('missing model:', modelname)
        # # print(procedural_code)


if __name__ == '__main__':
    app = Ursina()
    RedCube()
    VioletSphere(x=1)
    YellowCube(x=2, scale=(10,1,10), texture='white_cube', texture_scale=(10,10))
    # OrangePyramid(x=2)
    # GreenPlane(x=3)
    # EditorCamera()
    app.run()

    # print(class_names)
