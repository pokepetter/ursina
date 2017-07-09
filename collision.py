
global parent


# def point_inside_thing(point, thing):
#     if thing.collision:
#         # check if point is inside box. //no rotation yet
#         if (point[0] >= thing.collider[0][0] - thing.collider[2][0]
#         and point[0] <= thing.collider[0][0] + thing.collider[2][0]
#         and point[1] >= thing.collider[0][1] - thing.collider[2][1]
#         and point[1] <= thing.collider[0][1] + thing.collider[2][1]):
#             return thing
#
#     return False



def point_inside_thing(point, thing):
    if thing.collision:
        # check if point is inside box. //no rotation yet
        if (point[0] >= thing.collider[0][0] - thing.collider[2][0]
        and point[0] <= thing.collider[0][0] + thing.collider[2][0]
        and point[1] >= thing.collider[0][1] - thing.collider[2][1]
        and point[1] <= thing.collider[0][1] + thing.collider[2][1]
        and point[2] >= thing.collider[0][2] - thing.collider[2][2]
        and point[2] <= thing.collider[0][2] + thing.collider[2][2]):
            return thing

    return False



def point(self, point=(0,0,0)):
    collided_with = list()
    for thing in parent.things:
        if point_inside_thing(point, thing):
            collided_with.append(thing)
        if len(collided_with) > 0:
            return True

    return False
