from ursina import *

class NineSlice(Mesh):
    def __init__(self, xSize:float, ySize:float):
        corner_size = min(xSize, ySize) / 4 # Set a fixed corner size for 9-slicing texture

        # Define vertices for a 3x3 grid (9-slice pattern)
        vertices = [
            # Top row
            Vec3(-xSize / 2, ySize / 2, 0),  # 0: Top-left corner
            Vec3(-xSize / 2 + corner_size, ySize / 2, 0),  # 1: Top-left border-right
            Vec3(xSize / 2 - corner_size, ySize / 2, 0),  # 2: Top-right border-left
            Vec3(xSize / 2, ySize / 2, 0),  # 3: Top-right corner

            # Middle row
            Vec3(-xSize / 2, ySize / 2 - corner_size, 0),  # 4: Middle-left border-down
            Vec3(-xSize / 2 + corner_size, ySize / 2 - corner_size, 0),  # 5: Top-left of center
            Vec3(xSize / 2 - corner_size, ySize / 2 - corner_size, 0),  # 6: Top-right of center
            Vec3(xSize / 2, ySize / 2 - corner_size, 0),  # 7: Middle-right border-down

            # Bottom row
            Vec3(-xSize / 2, -ySize / 2 + corner_size, 0),  # 8: Bottom-left border-up
            Vec3(-xSize / 2 + corner_size, -ySize / 2 + corner_size, 0),  # 9: Bottom-left of center
            Vec3(xSize / 2 - corner_size, -ySize / 2 + corner_size, 0),  # 10: Bottom-right of center
            Vec3(xSize / 2, -ySize / 2 + corner_size, 0),  # 11: Bottom-right border-up

            # Bottom row corners
            Vec3(-xSize / 2, -ySize / 2, 0),  # 12: Bottom-left corner
            Vec3(-xSize / 2 + corner_size, -ySize / 2, 0),  # 13: Bottom-left border-right
            Vec3(xSize / 2 - corner_size, -ySize / 2, 0),  # 14: Bottom-right border-left
            Vec3(xSize / 2, -ySize / 2, 0)  # 15: Bottom-right corner
        ]

        # Define triangles for 9-slice grid
        triangles = [
            # Top row
            (0, 4, 1), (1, 4, 5),  # Top-left corner
            (1, 5, 2), (2, 5, 6),  # Top border
            (2, 6, 3), (3, 6, 7),  # Top-right corner

            # Middle row
            (4, 8, 5), (5, 8, 9),  # Left border
            (5, 9, 6), (6, 9, 10),  # Center
            (6, 10, 7), (7, 10, 11),  # Right border

            # Bottom row
            (8, 12, 9), (9, 12, 13),  # Bottom-left corner
            (9, 13, 10), (10, 13, 14),  # Bottom border
            (10, 14, 11), (11, 14, 15)  # Bottom-right corner
        ]

        # Define UV coordinates for a 3x3 grid layout (relative to a 1x1 texture space)
        uvs = [
            # Top row
            (0, 1), (0.25, 1), (0.75, 1), (1, 1),
            (0, 0.75), (0.25, 0.75), (0.75, 0.75), (1, 0.75),
            # Bottom row
            (0, 0.25), (0.25, 0.25), (0.75, 0.25), (1, 0.25),
            (0, 0), (0.25, 0), (0.75, 0), (1, 0)
        ]

        super().__init__(vertices=vertices, triangles=triangles, uvs=uvs, colors=[color.white] * 16, mode='triangle')

if __name__ == '__main__':
    app = Ursina()
    button1 = Button(text="Hi !!", model=NineSlice(0.2, 0.3), position=(-0.2, -0.3), texture="nine_sliced", color=color.white)
    button2 = Button(text="Hello !!!", model=NineSlice(0.5, 0.3), position=(0.2, -0.3), texture="nine_sliced", color=color.white)
    button3 = Button(text="As you can see, the texture goes \nwell for every button size.", model=NineSlice(0.4, 0.4), position=(0, 0.1), texture="nine_sliced", color=color.white)
    app.run()