from ursina import *

class EditorCamera(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'editor_camera_controller'

        self.camera_pivot = Entity()
        self.camera_pivot.name = 'camera_pivot'
        self.camera_pivot.is_editor = True

        self.rotation_speed = 100
        self.pan_speed = (4, 4)
        self.move_speed = .1
        self.zoom_speed = 1

        # self.original_camera_parent = camera.parent
        # camera.reparent_to(self.camera_pivot)
        # self.camera_pivot.rotation_x += 45
        # camera.reparent_to(self.original_camera_parent)

    def input(self, key):
        if key == '+':
            camera.fov += 1
            printvar(camera.fov)
        elif key == '-':
            camera.fov -= 1
            printvar(camera.fov)

        if key == 'p':
            camera.orthographic = not camera.orthographic


        if key == 'right mouse down' or key == 'middle mouse down':
            self.original_camera_parent = camera.parent
            camera.reparent_to(self.camera_pivot)

        if key == 'right mouse up' or key == 'middle mouse up':
            camera.reparent_to(self.original_camera_parent)
        # zooming, don't zoom if hovering an editor panel
        if not mouse.hovered_entity or mouse.hovered_entity.is_editor == False:
            if mouse.left or mouse.right or mouse.middle:
                return
            if key == 'scroll up':
                camera.position += camera.forward * self.zoom_speed
            if key == 'scroll down':
                camera.position += camera.back * self.zoom_speed



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
    sky = load_prefab('sky')
    # e = Entity(model='quad')
    ground = Plane(scale=(10,10), color=color.dark_gray)
    camera.add_script('editor_camera')
    app.run()
