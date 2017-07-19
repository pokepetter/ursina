import mouse
import camera

class EditorCamera():

    def __init__(self):
        self.pan = False
        self.mouse_start = (0,0)

    def input(self, key):
        # print(key)
        if key == 'd' and key != 'd-repeat':
            camera.global_position += camera.right
            # camera.global_position = (camera.global_position[0] + 1, camera.global_position[1], camera.global_position[2])
        if key == 'a':
            camera.global_position += camera.left
            # camera.global_position = (camera.global_position[0] - 1, camera.global_position[1], camera.global_position[2])

        if key == 's':
            camera.global_position += camera.back
            # camera.global_position = (camera.global_position[0], camera.global_position[1] - 1, camera.global_position[2])
        if key == 'w':
            camera.global_position += camera.forward
            # camera.global_position = (camera.global_position[0], camera.global_position[1] + 1, camera.global_position[2])
        #
        #
        # if key == 'e':
        #     camera.global_position += camera.up
        # if key == 'q':
        #      camera.global_position += camera.down
        #
        # if key == 'r':
        #     camera.rotation_x += 1 #(camera.rotation[0] -1, camera.rotation[1], camera.rotation[2])
        # if key == 'f':
        #     camera.rotation_x -= 1
        # if key == 't':
        #     camera.rotation_y += 1
        # if key == 'g':
        #     camera.rotation_y -= 1
        # if key == 'y':
        #     camera.rotation_z += 1
        # if key == 'h':
        #     camera.rotation_z -= 1

        # print(camera.cam.getPos())



        if key == 'middle mouse down':
            print('start pan')
            self.pan = True
            self.mouse_start = mouse.position
        if key == 'middle mouse up':
            self.pan = False
            mouse.x += mouse.x - self.mouse_start[0]

    def update(self, dt):
        # print(self.pan)
        if self.pan:
            # print(mouse.x)
            print(mouse.x - self.mouse_start[0])
            # camera.x += mouse_start[0] + mouse.x
