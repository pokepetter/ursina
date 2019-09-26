# from ursina import *
#
# class Inventory(Entity):
#     def __init__(self):
#         super().__init__(
#             parent = camera.ui,
#             model = 'quad'
#             )
#
#
#
# if __name__ == '__main__':
#     app = Ursina()
#     inventory = Inventory()
#     app.run()



# from ursina import *
#
# class Inventory(Entity):
#     def __init__(self):
#         super().__init__(
#             parent = camera.ui,
#             model = 'quad',
#             scale = (.5, .8),
#             origin = (-.5, .5),
#             position = (-.3,.4),
#             texture = 'white_cube',
#             texture_scale = (5,8),
#             color = color.dark_gray
#             )
#
#
#
# if __name__ == '__main__':
#     app = Ursina()
#     inventory = Inventory()
#     app.run()


            # from ursina import *
            #
            # class Inventory(Entity):
            #     def __init__(self):
            #         super().__init__(
            #             parent = camera.ui,
            #             model = 'quad',
            #             scale = (.5, .8),
            #             origin = (-.5, .5),
            #             position = (-.3,.4),
            #             texture = 'white_cube',
            #             texture_scale = (5,8),
            #             color = color.dark_gray
            #             )
            #
            #         self.item_parent = Entity(parent=self, scale=(1/5,1/8))
            #
            #
            #     def append(self, item):
            #         Button(
            #             parent = inventory.item_parent,
            #             model = 'quad',
            #             origin = (-.5,.5),
            #             color = color.random_color(),
            #             z = -.1
            #             )
            #
            #
            # if __name__ == '__main__':
            #     app = Ursina()
            #     inventory = Inventory()
            #     inventory.append('test item')
            #     inventory.append('test item')
            #     app.run()


# from ursina import *
#
# class Inventory(Entity):
#     def __init__(self):
#         super().__init__(
#             parent = camera.ui,
#             model = 'quad',
#             scale = (.5, .8),
#             origin = (-.5, .5),
#             position = (-.3,.4),
#             texture = 'white_cube',
#             texture_scale = (5,8),
#             color = color.dark_gray
#             )
#
#         self.item_parent = Entity(parent=self, scale=(1/5,1/8))
#
#
#     def find_free_spot(self):
#         taken_spots = [(int(e.x), int(e.y)) for e in self.item_parent.children]
#         for y in range(8):
#             for x in range(5):
#                 if not (x,-y) in taken_spots:
#                     return (x,-y)
#
#
#     def append(self, item):
#         Button(
#             parent = inventory.item_parent,
#             model = 'quad',
#             origin = (-.5,.5),
#             color = color.random_color(),
#             position = self.find_free_spot(),
#             z = -.1
#             )
#
#
# if __name__ == '__main__':
#     app = Ursina()
#     inventory = Inventory()
#     for i in range(7):
#         inventory.append('test item')
#     app.run()


# code, size .8
from ursina import *

class Inventory(Entity):
    def __init__(self):
        super().__init__(
            parent = camera.ui,
            model = 'quad',
            scale = (.5, .8),
            origin = (-.5, .5),
            position = (-.3,.4),
            texture = 'white_cube',
            texture_scale = (5,8),
            color = color.dark_gray
            )

        self.item_parent = Entity(parent=self, scale=(1/5,1/8))


    def find_free_spot(self):
        taken_spots = [(int(e.x), int(e.y)) for e in self.item_parent.children]
        for y in range(8):
            for x in range(5):
                if not (x,-y) in taken_spots:
                    return (x,-y)


    def append(self, item):
        icon = Button(                                                  # +
            parent = inventory.item_parent,
            model = 'quad',
            texture = item,                                             # +
            color = color.white,                                        # +
            origin = (-.5,.5),
            position = self.find_free_spot(),
            z = -.1,
            )
        name = item.replace('_', ' ').title()                           # +
        icon.tooltip = Tooltip(name)                                    # +
        icon.tooltip.background.color = color.color(0,0,0,.8)           # +


if __name__ == '__main__':
    app = Ursina()
    inventory = Inventory()

    def add_item():
        inventory.append(random.choice(('bag', 'bow_arrow', 'gem', 'orb', 'sword')))

    for i in range(7):
        add_item()

    add_item_button = Button(
        scale = (.1,.1),
        x = -.5,
        color = color.lime.tint(-.25),
        text = '+',
        tooltip = Tooltip('Add random item'),
        on_click = add_item
        )

    app.run()
