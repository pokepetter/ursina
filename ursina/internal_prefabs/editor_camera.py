from ursina import *

class EditorCamera(Entity):

    def __init__(self, **kwargs):
        super().__init__()
        self.name = 'editor_camera_controller'

        self.camera_pivot = Entity(name='camera_pivot', is_editor=True, model='cube', color=color.green, scale=(.05,.05,.05))
        # t = Entity(position=(1,1,1), model='cube', color=color.red, scale=(.1,.3,.1), origin=(0,-1))
        t=camera
        self.dummy = Entity(
            model = Sphere(),
            scale = (.2,.2,.2),
            color = color.yellow,
            is_editor = True,
            position = t.position
            )
        self.dummy.world_parent = self.camera_pivot
        self.dummy.look_at(self.camera_pivot)
        # t = camera
        t.add_script(SmoothFollow(target=self.dummy, rotation_speed=10))

        self.rotation_speed = 100
        self.pan_speed = (4, 4)
        self.move_speed = .1
        self.zoom_speed = 1


        for key, value in kwargs.items():
            setattr(self, key, value)


    def input(self, key):
        if key == '+':
            camera.fov += 1
            printvar(camera.fov)
        elif key == '-':
            camera.fov -= 1
            printvar(camera.fov)

        if key == 'p':
            camera.orthographic = not camera.orthographic


        # if key == 'right mouse down' or key == 'middle mouse down':
        #     self.test.smooth_follow.target = self.dummy
            # self.original_camera_parent = camera.parent
            # camera.reparent_to(self.camera_pivot)

        # if key == 'right mouse up' or key == 'middle mouse up':
        #     self.test.smooth_follow.target = None
            # camera.reparent_to(self.original_camera_parent)

        # zooming, don't zoom if hovering an editor panel
        if not mouse.hovered_entity or mouse.hovered_entity.is_editor == False:
            if mouse.left or mouse.right or mouse.middle:
                return
            if key == 'scroll up':
                self.dummy.position += self.dummy.forward * self.zoom_speed
            if key == 'scroll down':
                self.dummy.position += self.dummy.back * self.zoom_speed



    def update(self):
        if mouse.right:
            self.camera_pivot.rotation_x -= mouse.velocity[1] * self.rotation_speed
            self.camera_pivot.rotation_y += mouse.velocity[0] * self.rotation_speed

            self.camera_pivot.position += camera.right * held_keys['d'] * self.move_speed
            self.camera_pivot.position += camera.left * held_keys['a'] * self.move_speed
            self.camera_pivot.position += camera.forward * held_keys['w'] * self.move_speed
            self.camera_pivot.position += camera.back * held_keys['s'] * self.move_speed
            self.camera_pivot.position += camera.up * held_keys['e'] * self.move_speed
            self.camera_pivot.position += camera.down * held_keys['q'] * self.move_speed


        if mouse.middle:
            self.camera_pivot.position -= camera.right * mouse.velocity[0] * self.pan_speed[0]
            self.camera_pivot.position -= camera.up * mouse.velocity[1] * self.pan_speed[1]



if __name__ == '__main__':
    app = main.Ursina()
    sky = Sky()
    # e = Entity(model='quad')
    # ground = Plane(scale=(10,10), color=color.dark_gray)
    Entity(model='cube', color=color.white33)
    camera.position=(20,20,-20)
    ec = EditorCamera(rotation_smoothing=2, rotation_speed=200)
    camera.look_at(ec)
    app.run()
