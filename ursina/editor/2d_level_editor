from ursina import *

# Sir, it's 2d level editor but the class doesn't take numbers

class LevelEditor(Entity):
    def __init__(self, ver_file, tri_file):
        super().__init__()

        self.entity_1 = Draggable(model='quad', scale=.3, color=color.gold, position=(0,0,0), parent=scene)
        self.entity_2 = Draggable(model='quad', scale=.3, color=color.orange, position=(1,0,0),parent=scene)
        self.entity_3 = Draggable(model='quad', scale=.3, color=color.red, position=(1,1,0), parent=scene)
        self.vertices_file = ver_file
        self.triangles_file = tri_file

        self.a = -1

        EditorCamera()

    def input(self, key):
        if key == 'enter':
            self.vertices = (self.entity_1.position, self.entity_2.position, self.entity_3.position)
            self.triangles = (0, 1, 2)
            self.main_mesh = Mesh(vertices=self.vertices, triangles=self.triangles)
            self.mesh_entity = Entity(model=self.main_mesh, collider='mesh')

            b = self.a + 2
            f1 = open(self.vertices_file, 'r')
            p = f1.read()
            f1.close()
            f = open(self.vertices_file, 'w')
            f.write(f'{p}{self.entity_1.position},{self.entity_2.position},{self.entity_3.position}, \n')
            f.close()

            f1 = open(self.triangles_file, 'r')
            p = f1.read()
            f1.close()
            f = open(self.triangles_file, 'w')
            self.a += 1
            f.write(f'{p}{self.a}, ')
            f.close()

            f1 = open(self.triangles_file, 'r')
            p = f1.read()
            f1.close()
            f = open(self.triangles_file, 'w')
            self.a += 1
            f.write(f'{p}{self.a}, ')
            f.close()

            f1 = open(self.triangles_file, 'r')
            p = f1.read()
            f1.close()
            f = open(self.triangles_file, 'w')
            self.a += 1
            f.write(f'{p}{self.a}, ')
            f.close()

if __name__ == '__main__':
    app=Ursina()

    LevelEditor('filename.txt', 'try.txt')

    app.run()
