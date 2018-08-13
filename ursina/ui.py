from ursina import *

class UI():

    def __init__(self):
        self.entity = None
        # ui display region
        dr = win.makeDisplayRegion()
        dr.setSort(20)

        myCamera2d = NodePath(Camera('myCam2d'))
        self.lens = OrthographicLens()
        self.lens.setFilmSize(100 * camera.aspect_ratio, 100)
        self.lens.setNearFar(-1000, 1000)
        myCamera2d.node().setLens(self.lens)

        myRender2d = NodePath('myRender2d')
        myRender2d.setDepthTest(False)
        myRender2d.setDepthWrite(False)
        myCamera2d.reparentTo(myRender2d)
        dr.setCamera(myCamera2d)
