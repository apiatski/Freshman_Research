#doing ok
import viz
import vizshape
import viz
import math
import random
import vizact
import viztask
import vizproximity
#so far so good
viz.setMultiSample(4)
viz.fov(60)
viz.go()
#Add a world axis with X,Y,Z labels
world_axes = vizshape.addAxes()
X = viz.addText3D('X',pos=[1.1,0,0],color=viz.RED,scale=[0.3,0.3,0.3],parent=world_axes)
Y = viz.addText3D('Y',pos=[0,1.1,0],color=viz.GREEN,scale=[0.3,0.3,0.3],align=viz.ALIGN_CENTER_BASE,parent=world_axes)
Z = viz.addText3D('Z',pos=[0,0,1.1],color=viz.BLUE,scale=[0.3,0.3,0.3],align=viz.ALIGN_CENTER_BASE,parent=world_axes)


#grids are good
grid = vizshape.addGrid(color=[0.2]*3)
viz.clearcolor(viz.GRAY)

#Establish and translate our first cylinder
cylinder1= vizshape.addCylinder(height=1.0,radius=0.5,topRadius=None,bottomRadius=None,axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
cylinder1= cylinder1.translate(2,2,5)

#create our first plane
plane1= vizshape.addPlane(size=(20.0,20.0),axis=vizshape.AXIS_X, cullFace=False)

#Establish and translate our second cylinder

cylinder2= vizshape.addCylinder(height=1.0,radius=0.5,topRadius=None,bottomRadius=None,axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
cylinder2= cylinder2.translate(-2,2,5)
#Create proximity manager
manager = vizproximity.Manager()
manager.setDebug(viz.ON)
#create sensors
cylinder1_sensor= vizproximity.Sensor(vizproximity.Box([2,2,2],center=[2,2,5]),source = cylinder1)
manager.addSensor(cylinder1_sensor)

cylinder2_sensor= vizproximity.Sensor(vizproximity.Box([2,2,2],center=[-2,2,5]),source = cylinder2)
manager.addSensor(cylinder2_sensor)
plane1_sensor= vizproximity.Sensor(vizproximity.Box([1,20,20],center=[0,0,0]),source = cylinder2)
manager.addSensor(plane1_sensor)
#create proximity task (passive function)
def proximityTask1():
    
    yield vizproximity.waitEnter(cylinder1_sensor)

viztask.schedule(proximityTask1())

#print the enter/exits of cyl1
def EnterProximity_cylinder1(cylinder1_sensor):
    print('Entered cylinder1')


def ExitProximity_cylinder1(cylinder1_sensor):
	print('Exited cylinder1')

manager.onEnter(cylinder1_sensor,EnterProximity_cylinder1)
manager.onExit(cylinder1_sensor,ExitProximity_cylinder1)

#print the enter/exits of cyl2
def EnterProximity_cylinder2(cylinder2_sensor):
    print('Entered cylinder2')

def ExitProximity_cylinder2(cylinder2_sensor):
	print('Exited cylinder2')

manager.onEnter(cylinder2_sensor,EnterProximity_cylinder2)
manager.onExit(cylinder2_sensor,ExitProximity_cylinder2)

#print the enter/exits of pln1
	
def EnterProximity_plane1(plane1_sensor):
    print('Entered plane1')

def ExitProximity_plane1(plane1_sensor):
    print('Exited plane1')

manager.onEnter(plane1_sensor,EnterProximity_plane1)
manager.onExit(plane1_sensor,ExitProximity_plane1)
#We currently have the tracking as 
target = vizproximity.Target(viz.MainView)
manager.addTarget(target)

