import scene
global parent


# def point_inside_entity(point, entity):
#     if entity.collision:
#         # check if point is inside box. //no rotation yet
#         if (point[0] >= entity.collider[0][0] - entity.collider[2][0]
#         and point[0] <= entity.collider[0][0] + entity.collider[2][0]
#         and point[1] >= entity.collider[0][1] - entity.collider[2][1]
#         and point[1] <= entity.collider[0][1] + entity.collider[2][1]):
#             return entity
#
#     return False



def point_inside_entity(point, entity):
    if entity.enabled and not entity.node_path.isHidden() and entity.collision:
        entity.collider = (entity.model.getPos(scene.render), (0,0,0),
                        (entity.model.getScale(scene.render)[0] /4, 1,
                        entity.model.getScale(scene.render)[2] /4))
        # check if point is inside box. //no rotation yet
        if (point[0] >= entity.collider[0][0] - entity.collider[2][0]
        and point[0] <= entity.collider[0][0] + entity.collider[2][0]
        and point[1] >= entity.collider[0][1] - entity.collider[2][1]
        and point[1] <= entity.collider[0][1] + entity.collider[2][1]
        and point[2] >= entity.collider[0][2] - entity.collider[2][2]
        and point[2] <= entity.collider[0][2] + entity.collider[2][2]):
            return entity

        return False
    return False



def point(self, point=(0,0,0)):
    collided_with = list()
    for entity in parent.entities:
        if point_inside_entity(point, entity):
            collided_with.append(entity)
        if len(collided_with) > 0:
            return True

    return False
