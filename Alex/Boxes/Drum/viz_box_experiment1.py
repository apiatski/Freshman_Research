#doing ok
import viz
import vizshape
import viz
import math
import random
import vizact
import viztask
import vizproximity
import viztracker2 as viztracker
from viztracker import*
#set default values for tracking errors
times_crossed=0
times_entered_left_plane=0
times_entered_right_plane=0

time_data= open('time collect for boxes', 'a')
sensor_data= open('sensor collect for boxes', 'a')
tracking_data= open('head and hand collect for boxes', 'a')
#set changeable scales for the the box sensors and distance between them
scale_x=1
scale_y=1
scale_z= 1
distance_between_targets=4
y_height= 2
z_depth= 5
x_translate= distance_between_targets/2
height=.025
#tracking data
#import hand

    
    
    
#viztracker.go()
#
#
#composite = viztracker.getManager().getCompositeList()[0]
#headTracker = composite.getRawTracker(composite.HEAD)
#handTracker = composite.getRawTracker(composite.RHAND)
#stupidhand = viztracker.get('righthand') 
#
#viewpoint = viztracker.get('viewpoint')
#movable = viztracker.get("movable")
#print('viewpoint')
#def printData():
#    print 'Tracker position',headTracker.getPosition()
#    print 'Tracker euler',headTracker.getEuler()
#    print 'Hand Tracker position',handTracker.getPosition() #just added this
#    print 'Hand Tracker euler',handTracker.getEuler() #and this
#    print 'Viewpoint position',viewpoint.getPosition()
#    print 'Movable position',movable.getPosition(),'\n'
#vizact.ontimer(5, printData)
## Setup tracking if this is the main script
#if __name__ == "__main__":
#	import viztracker
#	viztracker.DEFAULT_HANDS = True
#	viztracker.go()

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

#Create proximity manager
manager = vizproximity.Manager()
manager.setDebug(viz.ON)



#create our bisecting plane
mid_plane= vizshape.addPlane(size=(.00001,.00001),axis=vizshape.AXIS_X, cullFace=False)

start_node= right_node=vizshape.addCylinder(height, radius=2,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
     
left_node=vizshape.addCylinder(height, radius= 3,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)        
right_node=vizshape.addCylinder(height, radius=2,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
left_plane1= vizshape.addPlane(size=(1*scale_x,1*scale_y,),axis=vizshape.AXIS_Y, cullFace=False)
left_plane2= vizshape.addPlane(size=(1*scale_x,1*scale_y,),axis=vizshape.AXIS_Y, cullFace=False)


box_and_sensor_parameters=[x_translate,y_height,z_depth]
box_and_sensor_parameters2= [-x_translate,y_height,z_depth]
left_plane=left_plane1.translate(x_translate,y_height,z_depth)
left_plane2.translate(-x_translate,y_height,z_depth)


#left_plane=plane(list_pos_ori_left)
#right_plane=plane(list_pos_ori_right)

#manager
manager = vizproximity.Manager()		
manager.setDebug(True)
sensor_parameters= [scale_x,height,scale_z]

#create sensors
left_plane_sensor= vizproximity.Sensor(vizproximity.Box(sensor_parameters,box_and_sensor_parameters),left_node)
manager.addSensor(left_plane_sensor)

#right_plane_sensor= vizproximity.Sensor(vizproximity.Box(sensor_parameters,box_and_sensor_parameters2),right_node)
#manager.addSensor(right_plane_sensor) 

right_plane_sensor= vizproximity.Sensor(vizproximity.Box(sensor_parameters,[50,50,0]),right_node)
manager.addSensor(right_plane_sensor)

mid_plane_sensor= vizproximity.Sensor(vizproximity.Box([.025,20,20],center=[0,0,0]),source = mid_plane)
manager.addSensor(mid_plane_sensor)        
     
start_sensor=vizproximity.Sensor(vizproximity.Box(sensor_parameters,box_and_sensor_parameters),left_node)
manager.addSensor(start_sensor)

        
    
    
##Establish and translate our first cylinder
#cylinder1= vizshape.addCylinder(height=.000000000001,radius=0.000000000000001,topRadius=None,bottomRadius=None,axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
#cylinder1= cylinder1.translate(2,2,5)
#
#
##Establish and translate our second cylinder
#
#cylinder2= vizshape.addCylinder(height=1.0,radius=0.5,topRadius=None,bottomRadius=None,axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
#cylinder2= cylinder2.translate(-2,2,5)


#create proximity task (passive function)
def proximityTask1():
    
    yield vizproximity.waitEnter(left_plane_sensor)

viztask.schedule(proximityTask1())

#print the enter/exits of cyl1
def EnterProximity_left_plane_sensor(left_plane_sensor):
    print('Entered left_plane_sensor')


def ExitProximity_left_plane_sensor(left_plane_sensor):
    print('Exited left_plane_sensor')
    global times_entered_left_plane
    times_entered_left_plane+=1
    print('Times entered Right plane', times_entered_left_plane)
    sensor_data.write('\n Right Plane Entered' + str(times_entered_left_plane)+ 'Times')
manager.onEnter(left_plane_sensor,EnterProximity_left_plane_sensor)
manager.onExit(left_plane_sensor,ExitProximity_left_plane_sensor)

def EnterProximity_start_sensor(start_sensor):
    print('Entered start_center')
    start_sensor.translate(-50,-50,-50)
    right_plane_sensor.translate(0,0,0)

def ExitProximity_start_sensor(start_sensor):
    print('Exited start_center')
    translate
#print the enter/exits of cyl2
def EnterProximity_right_plane_sensor(right_plane_sensor):
    print('Entered right_plane_sensor')
    
def ExitProximity_right_plane_sensor(right_plane_sensor):
    print('Exited right_plane_sensor')
    global times_entered_right_plane
    times_entered_right_plane+=1
    print('Times Entered Left Plane: ', times_entered_right_plane)
    sensor_data.write('\n Left Plane Entered' + str(times_entered_right_plane)+ 'Times')
manager.onEnter(right_plane_sensor,EnterProximity_right_plane_sensor)
manager.onExit(right_plane_sensor,ExitProximity_right_plane_sensor)

#print the enter/exits of pln1
	
def EnterProximity_mid_plane_sensor(mid_plane_sensor):
    print('Entered mid_plane_sensor')
    
    

def ExitProximity_mid_plane_sensor(mid_plane_sensor):
    print('Exited mid_plane_sensor')
    global times_crossed
    times_crossed+=1
    print('Times Crossed Mid Plane: ', times_crossed)
    sensor_data.truncate()
    sensor_data.write('\n Mid Plane Crossed' + str(times_crossed) + 'Times')
    
manager.onEnter(mid_plane_sensor,EnterProximity_mid_plane_sensor)
manager.onExit(mid_plane_sensor,ExitProximity_mid_plane_sensor)

# when tracking use: target = vizproximity.Target((stupidhand)) 
#We currently have the tracking as main view 
#be able to time from a t(0) to the end of the cycles. be able to start the timer yourself.
#be able to record/save? how many cycles they do
#they will start in a square. once they leave the square, the time should start. the first exit implies time trial starting. 

target = vizproximity.Target(viz.MainView)
manager.addTarget(target)

#Create an event class. 
class modelMaker( viz.EventClass ): 
    def __init__(self, modelName): 
        #Initialize the base class 
        viz.EventClass.__init__(self) 
        #Create a callback to our own event class function 
        self.callback(viz.TIMER_EVENT,self.myTimer) 
        #Start a perpetual timer for this event class 
        #to go once per second. 
        self.starttimer(0,.1,viz.PERPETUAL) 
        #Add a counter. 
        self.counter = 0 
        self.counter2 = 0
        #Store the model name in this class. 
        self.modelName = modelName 
    
    def myTimer( self, num ): 
        #Add a model by the given name and place it according to the counter.
        #Advance the counter. 
        self.counter += .1
        data = ' ' + str(self.counter)
        time_data.truncate()
        time_data.write(data)
    
        
        
        
starting_time= viz.tick()

def getdata():
    #orientation = viz.MainView.getEuler()
    #position = viz.MainView.getPosition()
    #data = str(subject) + '\t' + str(orientation) + '\t' + str(position) + '\n' 
    elapsed_time= starting_time-viz.tick()
    
vizact.ontimer(1,getdata)
        



#Call the class. 
modelMaker('box.wrl')
viz.move(0,1.5,2) 


