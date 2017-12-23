from pandaeditor import camera
from panda3d.core import LineSegs


def draw_box_collider(box_collider):
    linesegs = LineSegs("lines")
    linesegs.setColorScale(0,1,0,1)

    # linesegs.drawTo(box_collider[0])
    # linesegs.drawTo(0.1, 0, 0)

    node = linesegs.create(False)
    # return node

    nodePath = camera.render.attachNewNode(node)
    # nodePAth = ui.target.model.attachNewNode(node)
