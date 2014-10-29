import vizshape

grid = vizshape.addGrid(color=[0.2]*3)
viz.clearcolor(viz.GRAY)

#align the right side of the box with X = 0
#bottom of the box with Y = 0
#front of the box with Z = 0
cylinder = vizshape.addCylinder(height=1.0, radius=0.5, topRadius=None,bottomRadius=None, axis=vizshape.AXIS_Y, slices=10, bottom=True,top=True)
cylinder.setposition(0,0,1)
import vizcam
vizcam.PivotNavigate(center=[0,2,0],distance=10)
viz.go()
