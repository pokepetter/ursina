from pandaeditor import *

class UI():

    def __init__(self):
        self.entity = None
        # ui display region
        dr = win.makeDisplayRegion()
        dr.setSort(20)

        myCamera2d = NodePath(Camera('myCam2d'))
        lens = OrthographicLens()
        lens.setFilmSize(100 * camera.aspect_ratio, 100)
        lens.setNearFar(-1000, 1000)
        myCamera2d.node().setLens(lens)

        myRender2d = NodePath('myRender2d')
        myRender2d.setDepthTest(False)
        myRender2d.setDepthWrite(False)
        myCamera2d.reparentTo(myRender2d)
        dr.setCamera(myCamera2d)

    def input(self, key):
        if key == 'x':
            scene.clear()
