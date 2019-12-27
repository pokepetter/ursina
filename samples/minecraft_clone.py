from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController


app = Ursina()

level_parent = Entity()

class Voxel(Button):
    def __init__(self, position=(0,0,0), **kwargs):
        super().__init__(
            parent = level_parent,
            position = position,
            model = 'cube',
            origin_y = .5,
            texture = 'white_cube',
            color = color.color(0, 0, random.uniform(.9, 1.0)),
            highlight_color = color.lime,
        )
        self.org_col = self.color
        self.movable = False

        for key, value in kwargs.items():
            setattr(self, key, value)

    def input(self, key):
        if self.hovered:
            if key == 'left mouse down':
                voxel = Voxel(position=self.position + mouse.normal)

            if key == 'right mouse down':
                destroy(self)

    @property
    def movable(self):
        return self._movable

    @movable.setter
    def movable(self, value):
        if value:
            self.color = color.orange
        else:
            self.color = self.org_col

        self._movable = value



for z in range(8):
    for x in range(8):
        voxel = Voxel(position=(x,0,z))


player = FirstPersonController(position=(4,10,4))


def update():
    if level_parent:
        ray = raycast(player.position, player.down, distance=.1, traverse_target=level_parent)
        # print(ray.hit)
        if not ray.hit:
            player.y -= 10 * time.dt


def input(key):
    if key == 'f':
        e = mouse.hovered_entity
        e.movable = not e.movable
        print(e.movable)


    if held_keys['control'] and key == 's':
        save()

    if held_keys['control'] and key == 'l':
        load_level(0)

    if key.isdigit():
        load_level(int(key))

Entity(model=Cube())

scene_recipe = ''
def save():
    global scene_recipe

    for i, e in enumerate(scene.entities):
        # print(e.name)
        # print(json.dumps(e.__dict__))
        model = None
        if e.model:
            model = e.model.recipe

        parent = 'scene'
        if e.parent in scene.entities:
            parent = f'scene.entities[{scene.entities.index(e.parent)}]'

        # print(parent)

        l = f'''entity_{i} = {e.__class__.__name__}(position={tuple(e.position)})'''
        scene_recipe += l + '\n'

    for i, e in enumerate(scene.entities):
        parent = 'scene'
        if e.parent in scene.entities:
            parent = f'scene.entities[{scene.entities.index(e.parent)}]'

        # print(parent)
        l = f'''entity_{i}.parent = {parent}'''
        scene_recipe += l + '\n'

    destroy(player)
    scene.clear()


def load_level(i):

    print('load level:', i)
    print(scene_recipe)
    for l in scene_recipe.split('\n'):
        try:
            exec(l)
            print('yay:', l)
        except Exception as e:
            print('error:', l, e)
    # exec(scene_recipe)




level_parent.scale = 3
app.run()
