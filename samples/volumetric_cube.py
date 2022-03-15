from ursina import *

app = Ursina()

window.color = color.black
print(len(scene.entities))
base_cube = Entity(model='cube', color=color.yellow, texture='white_cube')

for i in range(8):
    print(curve.out_expo(i/8))
    Entity(parent=base_cube, model='cube', color=color.orange, scale=math.pow(1.14,i), alpha=.1)

base_cube.combine()
print(len(scene.entities))


combine_parent = Entity()
base_cube.parent = combine_parent

# for i in range(20):
#     duplicate(base_cube, position=(random.uniform(-100,100),random.uniform(-100,100),random.uniform(-100,100)))

# combine_parent.combine()

EditorCamera()


app.run()
