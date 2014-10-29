import viz
import vizshape
viz.setMultiSample(4)
viz.fov(60)
viz.go()

plane= vizshape.addPlane([2,2], vizshape.AXIS_Z,cullFace = True)


