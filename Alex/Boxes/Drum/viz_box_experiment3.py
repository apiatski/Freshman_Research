#doing ok
import viz
import vizshape
import math
import random
import vizact
import viztask
import vizproximity
import viztracker2 as viztracker
from viztracker import*
import time
#set default values for tracking errors
times_crossed=0
times_entered_left_plane=0
times_entered_right_plane=0
times_entered_start_plane=0
times_entered_end_plane=0
timer1=0
timer2=0
starting_time= viz.tick()
control_array=[1,4,2,10,3,10]
def quick_test():
	global scale_x1
	scale_x1=5
	print('scale_x1 is now 5')
vizact.onkeydown('a',quick_test)
time_data= open('time collect for boxes', 'a')
sensor_data= open('sensor collect for boxes', 'a')
tracking_data= open('head and hand collect for boxes', 'a')
def getdata(timer1,timer2):
	global var1
	global var2 
	var1= viz.tick()-timer1
	var2= (viz.tick()-timer2)
#set changeable scales for the the box sensors and distance between them
scale_x1=1

scale_z1=5
scale_x2=0

scale_z2=0
scale_x3=0

scale_z3=0
distance_between_targets1=2
distance_between_targets2=0
distance_between_targets3=0
y_height1= 2.5
y_height2= 0
y_height3= 0
z_depth1= 5
z_depth2= 0
z_depth3= 0
x_translate1= distance_between_targets1
x_translate2= distance_between_targets1
x_translate3= distance_between_targets1

x_translate_shifted1=x_translate1+x_translate1*2
x_translate_shifted2=x_translate1+1.5
x_translate_shifted3=x_translate1+1.5

height1=.025
height2= .025
height3=.025
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

start_node= vizshape.addCylinder(height1, radius=.00000000005,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)

left_node1=vizshape.addCylinder(height1, radius= .000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)        
left_node2=vizshape.addCylinder(height1, radius= .000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)        
left_node3=vizshape.addCylinder(height1, radius= .000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)        


right_node1=vizshape.addCylinder(height1, radius=.00000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
right_node2=vizshape.addCylinder(height1, radius=.00000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
right_node3=vizshape.addCylinder(height1, radius=.00000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)


left_plane1= vizshape.addPlane(size=(1*scale_x1,1*scale_x1,),axis=vizshape.AXIS_Y, cullFace=False)
right_plane1= vizshape.addPlane(size=(1*scale_x1,1*scale_x1,),axis=vizshape.AXIS_Y, cullFace=False)

left_plane2= vizshape.addPlane(size=(1*scale_x2,1*scale_x2,),axis=vizshape.AXIS_Y, cullFace=False)
right_plane2= vizshape.addPlane(size=(1*scale_x2,1*scale_x2,),axis=vizshape.AXIS_Y, cullFace=False)

left_plane3= vizshape.addPlane(size=(1*scale_x3,1*scale_x3,),axis=vizshape.AXIS_Y, cullFace=False)
right_plane3= vizshape.addPlane(size=(1*scale_x3,1*scale_x3,),axis=vizshape.AXIS_Y, cullFace=False)

box_and_sensor_parameters_r1=[x_translate1,x_translate1,z_depth1]
box_and_sensor_parameters_r2=[x_translate2,x_translate2,z_depth2]
box_and_sensor_parameters_r3=[x_translate3,x_translate3,z_depth3]

box_and_sensor_parameters_l1= [-x_translate1,y_height1,z_depth1]
box_and_sensor_parameters_l2= [-x_translate2,y_height2,z_depth2]
box_and_sensor_parameters_l3= [-x_translate3,y_height3,z_depth3]

left_plane1=left_plane1.translate(-x_translate1,y_height1,z_depth1)
right_plane1=right_plane1.translate(x_translate1,y_height1,z_depth1)


#left_plane=plane(list_pos_ori_left)
#right_plane=plane(list_pos_ori_right)

#manager
manager = vizproximity.Manager()		
manager.setDebug(True)
sensor_parameters= [scale_x1,height1,scale_z1]
start_parameters= [scale_x1,1,scale_z1]
right_node1.translate(0,500,0)
start_node.translate(x_translate1,y_height1,z_depth1)
n=0
rdim=[control_array[n],.25,control_array[n]]
#create sensors
#still need to make a set of left/right sensors/proximity functions for left_plane2/3 and right_plane 2/3
left_plane_sensor1= vizproximity.Sensor(vizproximity.Box([scale_x1,.25,scale_x1],[-x_translate1,y_height1,z_depth1]),left_node1)
manager.addSensor(left_plane_sensor1)

right_plane_sensor1= vizproximity.Sensor(vizproximity.Box((rdim),[x_translate1,y_height1,z_depth1]),right_node1)
manager.addSensor(right_plane_sensor1)

mid_plane_sensor= vizproximity.Sensor(vizproximity.Box([.025,20,20],center=[0,0,0]),source = mid_plane)
manager.addSensor(mid_plane_sensor)        
     
start_sensor=vizproximity.Sensor(vizproximity.Box([scale_x1,.25,scale_x1],center=[0,0,0]),start_node)
manager.addSensor(start_sensor)

end_sensor=vizproximity.Sensor(vizproximity.Box([scale_x1,1,scale_x1],center= [x_translate_shifted1, y_height1,z_depth1]),right_node1)
manager.addSensor(end_sensor)
 
    



#print the enter/exits of cyl1
def EnterProximity_left_plane_sensor1(left_plane_sensor1):
	print('Entered left_plane_sensor1')
	sensor_data.write('\nEntered the left plane at:'+ str(viz.tick()))
	
	


def ExitProximity_left_plane_sensor1(left_plane_sensor1):
    print('Exited left_plane_sensor1')
    global times_entered_left_plane
    times_entered_left_plane+=1
    print('Times entered left plane', times_entered_left_plane)
    sensor_data.write('\n left Plane Entered' + str(times_entered_left_plane)+ 'Times')
manager.onEnter(left_plane_sensor1,EnterProximity_left_plane_sensor1)
manager.onExit(left_plane_sensor1,ExitProximity_left_plane_sensor1)

def timer3():
	viz.playSound('boing!.wav')
	a=viz.tick()
	global timer2
	timer2=viz.tick()
	sensor_data.write('\nSound goes off at this time'+ str(viz.tick()))
	
def EnterProximity_start_sensor(start_sensor):
	vizact.ontimer2(1,0, timer3)
	global times_entered_start_plane
	times_entered_start_plane =times_entered_start_plane+1
	print('Entered start_sensor',str(times_entered_start_plane))

	
	
	
	
	
	
def ExitProximity_start_sensor(start_sensor):
#	if times_entered_start_plane==1:
	start_node.translate(0,100,0)
	right_node1.setPosition(0,0,0)
#	elif times_entered_start_plane==2:
#		start_node.translate(0,100,0)
#		right_node2.setPosition(0,0,0)
#	elif times_entered_start_plane==3:
#		start_node.translate(0,100,0)
#		right_node3.setPosition(0,0,0)
	sensor_data.write('\nExited start_sensor1 at: ' + str(viz.tick()))

def EnterProximity_end_sensor(end_sensor):
	start_node.translate(x_translate1,y_height1,z_depth1)
	right_node1.setPosition(0,100,0)
	right_node2.setPosition(0,100,0)
	right_node3.setPosition(0,100,0)
	sensor_data.write('\nEntered End sensor at:' + str(viz.tick()))
	print('Entered end_sensor')
	
def array_manipulator(array):
	global scale_x1
	global times_entered_end_plane
	scale_x1=array[times_entered_end_plane-1]
	return scale_x1
def ExitProximity_end_sensor(end_sensor):
	sensor_data.write('\nexited start plane at: ' + str(viz.tick())+'seconds')
	global times_entered_end_plane
	global scale_x1
	global n
	times_entered_end_plane=+1
	array_manipulator(control_array)
	n=n+1

manager.onEnter(end_sensor,EnterProximity_end_sensor)
manager.onExit(end_sensor,ExitProximity_end_sensor)	



	


manager.onEnter(start_sensor,EnterProximity_start_sensor)
manager.onExit(start_sensor,ExitProximity_start_sensor)
#print the enter/exits of cyl2

def EnterProximity_right_plane_sensor1(right_plane_sensor1):
    time_data.write('\nEntered the right plane at:'+ str(viz.tick())+ 'seconds')

	

def ExitProximity_right_plane_sensor1(right_plane_sensor1):
    print('Exited right_plane_sensor1')
    global times_entered_right_plane
    times_entered_right_plane+=1
    print('Times Entered right Plane1: ', times_entered_right_plane)
    sensor_data.write('\n Right Plane Entered' + str(times_entered_right_plane)+ 'Times')
manager.onEnter(right_plane_sensor1,EnterProximity_right_plane_sensor1)
manager.onExit(right_plane_sensor1,ExitProximity_right_plane_sensor1)

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

x=len(control_array)
if x=3:
	
	
	

target = vizproximity.Target(viz.MainView)
manager.addTarget(target)

array_manipulator(control_array)
viz.move(0,1.5,2) 

    
        
    
        
        




