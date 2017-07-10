
global parent


# def point_inside_gameobject(point, gameobject):
#     if gameobject.collision:
#         # check if point is inside box. //no rotation yet
#         if (point[0] >= gameobject.collider[0][0] - gameobject.collider[2][0]
#         and point[0] <= gameobject.collider[0][0] + gameobject.collider[2][0]
#         and point[1] >= gameobject.collider[0][1] - gameobject.collider[2][1]
#         and point[1] <= gameobject.collider[0][1] + gameobject.collider[2][1]):
#             return gameobject
#
#     return False



def point_inside_gameobject(point, gameobject):
    if gameobject.collision:
        # check if point is inside box. //no rotation yet
        if (point[0] >= gameobject.collider[0][0] - gameobject.collider[2][0]
        and point[0] <= gameobject.collider[0][0] + gameobject.collider[2][0]
        and point[1] >= gameobject.collider[0][1] - gameobject.collider[2][1]
        and point[1] <= gameobject.collider[0][1] + gameobject.collider[2][1]
        and point[2] >= gameobject.collider[0][2] - gameobject.collider[2][2]
        and point[2] <= gameobject.collider[0][2] + gameobject.collider[2][2]):
            return gameobject

        return False
    return False



def point(self, point=(0,0,0)):
    collided_with = list()
    for gameobject in parent.gameobjects:
        if point_inside_gameobject(point, gameobject):
            collided_with.append(gameobject)
        if len(collided_with) > 0:
            return True

    return False
