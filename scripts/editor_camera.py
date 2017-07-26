import sys
sys.path.append("..")
import camera
import mouse

class EditorCamera():

    def __init__(self):
        self.pan = False
        self.mouse_start = (0,0)
        self.speed = 2
        self.move = False

    def input(self, key):
        if key == 'right mouse down':
            self.move = True
        if key == 'right mouse up':
            self.move = False


        if self.move:
            if key == 'd':
                camera.position += camera.right * self.speed
                print(camera.right)
            if key == 'a':
                camera.position += camera.left * self.speed

            if key == 's':
                camera.position += camera.back * self.speed
            if key == 'w':
                camera.position += camera.forward * self.speed



            if key == 'e':
                camera.position += camera.up * self.speed
            if key == 'q':
                 camera.position += camera.down * self.speed
            #
            # if key == 'r':
            #     camera.rotation_x += 1 #(camera.rotation[0] -1, camera.rotation[1], camera.rotation[2])
            if key == 'f':
                camera.rotation_x -= 1
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
            self.camera_start = camera.position
            self.pan = True

        if key == 'middle mouse up':
            self.pan = False

    def update(self, dt):

        if self.pan:
            camera.x = self.camera_start[0] - mouse.delta[0] * self.speed
            camera.z = self.camera_start[2] - mouse.delta[1] * self.speed
