#doing ok
import viz
import vizinfo
import vizshape
import math
import random
import vizact
import viztask
import vizproximity
import viztracker2 as viztracker
from viztracker import*
import time
import vizinput
viz.setMultiSample(4)
viz.fov(60)
control_array=[1,2,3,3,2,1,2,3,1,3,2,1]
control_array=[1,2,3]
x=len(control_array)
a=0
b=0
reaction_timer_initial= 0
reaction_timer_final= 0
main_data= open('Main_Data', 'w')
subj_numb=vizinput.input('Please input the Subject Number:\n ')
tri_per_subj=vizinput.input('Please input how many trials this subject will go through:\n ')
def write_func():
	main_data.truncate()
	main_data.write('Sub# Ord Tri# BxSz Dis RT MT #Crs #Err Xp Yp Zp')	
	
write_func()
	
	
	
	
	
#set default values for tracking errors
left_plane1=0
left_plane2=0
left_plane3=0
left_plane4=0 
left_plane5=0 
left_plane6=0
left_plane7=0
left_plane8=0
left_plane9=0
left_plane10=0
left_plane11=0
left_plane12=0
right_plane1=0
right_plane2=0
right_plane3=0
right_plane4=0
right_plane5=0
right_plane6=0
right_plane7=0
right_plane8=0
right_plane9=0
right_plane10=0
right_plane11=0
right_plane12=0

times_crossed=0
times_entered_left_plane=0
times_entered_right_plane=0
times_entered_start_plane=0
times_entered_end_plane=0
timer1=0
timer2=0
starting_time= viz.tick()
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
#x_translate2= distance_between_targets1
#x_translate3= distance_between_targets1

x_translate_shifted1=x_translate1+max(control_array)
#x_translate_shifted2=x_translate1+1.5
#x_translate_shifted3=x_translate1+1.5

height1=.025
#height2= .025
#height3=.025

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
end_node= vizshape.addCylinder(height1, radius=.00000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
end_box=(vizshape.addBox([1,1,1],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color=viz.PURPLE))
left_node1=vizshape.addCylinder(height1, radius= .000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)        
#left_node2=vizshape.addCylinder(height1, radius= .000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)        
#left_node3=vizshape.addCylinder(height1, radius= .000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)        


right_node1=vizshape.addCylinder(height1, radius=.00000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
#right_node2=vizshape.addCylinder(height1, radius=.00000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
#right_node3=vizshape.addCylinder(height1, radius=.00000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
start_node= vizshape.addBox([1,.25,1],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color=viz.BLUE)
if x>0:
	left_plane1= vizshape.addBox([control_array[0],.00001,control_array[0]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane1.setPosition(-x_translate1,y_height1,z_depth1)
	right_plane1= vizshape.addBox([control_array[0],.00001,control_array[0]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane1.translate(x_translate1,y_height1,z_depth1)
if x>1:
	left_plane2= vizshape.addBox([control_array[1],.00001,control_array[1]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane2.setPosition(-x_translate1+50,y_height1,z_depth1)
	right_plane2= vizshape.addBox([control_array[1],.00001,control_array[1]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane2.translate(x_translate1+50,y_height1,z_depth1)
if x>2:
	left_plane3= vizshape.addBox([control_array[2],.00001,control_array[2]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane3.setPosition(-x_translate1+100,y_height1,z_depth1)
	right_plane3= vizshape.addBox([control_array[2],.00001,control_array[2]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane3.setPosition(x_translate1+100,y_height1,z_depth1)
if x>3:
	left_plane4= vizshape.addBox([control_array[3],.00001,control_array[3]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane4.setPosition(-x_translate1+150,y_height1,z_depth1)
	right_plane4= vizshape.addBox([control_array[3],.00001,control_array[3]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane4.setPosition(x_translate1+150,y_height1,z_depth1)
if x>4:
	left_plane5= vizshape.addBox([control_array[4],.00001,control_array[4]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane5.setPosition(-x_translate1+200,y_height1,z_depth1)
	right_plane5= vizshape.addBox([control_array[4],.00001,control_array[4]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane5.setPosition(x_translate1+200,y_height1,z_depth1)	
if x>5:
	left_plane6= vizshape.addBox([control_array[5],.00001,control_array[5]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane6.setPosition(-x_translate1+200,y_height1,z_depth1)
	right_plane6= vizshape.addBox([control_array[5],.00001,control_array[5]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane6.setPosition(x_translate1+200,y_height1,z_depth1)
if x>6:
	left_plane7= vizshape.addBox([control_array[6],.00001,control_array[6]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane7.setPosition(-x_translate1+250,y_height1,z_depth1)
	right_plane7= vizshape.addBox([control_array[6],.00001,control_array[6]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane7.setPosition(x_translate1+250,y_height1,z_depth1)
if x>7:
	left_plane8= vizshape.addBox([control_array[7],.00001,control_array[7]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane8.setPosition(-x_translate1+300,y_height1,z_depth1)
	right_plane8= vizshape.addBox([control_array[7],.00001,control_array[7]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane8.setPosition(x_translate1+300,y_height1,z_depth1)
if x>8:
	left_plane9= vizshape.addBox([control_array[8],.00001,control_array[8]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane9.setPosition(-x_translate1+350,y_height1,z_depth1)
	right_plane9= vizshape.addBox([control_array[8],.00001,control_array[8]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane9.setPosition(x_translate1+350,y_height1,z_depth1)
if x>9:
	left_plane10= vizshape.addBox([control_array[9],.00001,control_array[9]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane10.setPosition(-x_translate1+400,y_height1,z_depth1)
	right_plane10= vizshape.addBox([control_array[9],.00001,control_array[9]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane10.setPosition(x_translate1+400,y_height1,z_depth1)
if x>10:
	left_plane11= vizshape.addBox([control_array[10],.00001,control_array[10]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane11.setPosition(-x_translate1+450,y_height1,z_depth1)
	right_plane11= vizshape.addBox([control_array[10],.00001,control_array[10]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane11.setPosition(x_translate1+450,y_height1,z_depth1)
if x>11:
	left_plane12= vizshape.addBox([control_array[11],.00001,control_array[11]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane12.setPosition(-x_translate1+500,y_height1,z_depth1)
	right_plane12= vizshape.addBox([control_array[11],.00001,control_array[11]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane12.setPosition(x_translate1+500,y_height1,z_depth1)



#left_plane2= vizshape.addPlane(size=(1*scale_x2,1*scale_x2,),axis=vizshape.AXIS_Y, cullFace=False)
#right_plane2= vizshape.addPlane(size=(1*scale_x2,1*scale_x2,),axis=vizshape.AXIS_Y, cullFace=False)

#left_plane3= vizshape.addPlane(size=(1*scale_x3,1*scale_x3,),axis=vizshape.AXIS_Y, cullFace=False)
#right_plane3= vizshape.addPlane(size=(1*scale_x3,1*scale_x3,),axis=vizshape.AXIS_Y, cullFace=False)
#left_plane=plane(list_pos_ori_left)
#right_plane=plane(list_pos_ori_right)
#manager
manager = vizproximity.Manager()		
manager.setDebug(True)
sensor_parameters= [scale_x1,height1,scale_z1]
start_parameters= [scale_x1,1,scale_z1]
right_node1.translate(0,500,0)
start_node.translate(x_translate1,y_height1,z_depth1)
#n=0
#rdim=[control_array[n],.25,control_array[n]]
if x>0:
	times_entered_left_plane_error1=0
	times_entered_right_plane_error1=0
	left_plane_sensor_error1=vizproximity.Sensor(vizproximity.Box([control_array[0]+.25,.5,control_array[0]+.25],[-x_translate1,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error1)
	
	def EnterProximity_left_plane_sensor_error1(left_plane_sensor_error1):
		print('Entered left_plane_error1')
	def ExitProximity_left_plane_sensor_error1(left_plane_sensor_error1):
		global times_entered_left_plane_error1
		times_entered_left_plane_error1+=1
		print('Times entered left plane error1: ', times_entered_left_plane_error1)
	manager.onEnter(left_plane_sensor_error1,EnterProximity_left_plane_sensor_error1)
	manager.onExit(left_plane_sensor_error1,ExitProximity_left_plane_sensor_error1)
	
	right_plane_sensor_error1=vizproximity.Sensor(vizproximity.Box([control_array[0]+.25,.5,control_array[0]+.25],[x_translate1,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error1)
	def EnterProximity_right_plane_sensor_error1(right_plane_sensor_error1):
		print('Entered right_plane_error1')
	def ExitProximity_right_plane_sensor_error1(right_plane_sensor_error1):
		global times_entered_right_plane_error1
		times_entered_right_plane_error1+=1
		print('Times entered right plane error1: ', times_entered_right_plane_error1)
	manager.onEnter(right_plane_sensor_error1,EnterProximity_right_plane_sensor_error1)
	manager.onExit(right_plane_sensor_error1,ExitProximity_right_plane_sensor_error1)
		
	left_plane_sensor1= vizproximity.Sensor(vizproximity.Box([control_array[0],.25,control_array[0]],[-x_translate1,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor1)
	def EnterProximity_left_plane_sensor1(left_plane_sensor1):
		print('Entered left_plane_sensor1')
		

	def ExitProximity_left_plane_sensor1(left_plane_sensor1):
		print('Exited left_plane_sensor1')
		global times_entered_left_plane
		times_entered_left_plane+=1
		print('Times entered left plane: ', times_entered_left_plane)
	manager.onEnter(left_plane_sensor1,EnterProximity_left_plane_sensor1)
	manager.onExit(left_plane_sensor1,ExitProximity_left_plane_sensor1)
	

	right_plane_sensor1= vizproximity.Sensor(vizproximity.Box([control_array[0],.25,control_array[0]],[x_translate1,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor1)
	
	def EnterProximity_right_plane_sensor1(right_plane_sensor1):
		print('Entered right_plane1')

	

	def ExitProximity_right_plane_sensor1(right_plane_sensor1):
		print('Exited right_plane_sensor1')
		global times_entered_right_plane
		times_entered_right_plane+=1
		print('Times Entered right Plane1: ', times_entered_right_plane)
	manager.onEnter(right_plane_sensor1,EnterProximity_right_plane_sensor1)
	manager.onExit(right_plane_sensor1,ExitProximity_right_plane_sensor1)
if x>1:
	times_entered_left_plane_error2=0
	times_entered_right_plane_error2=0
	left_plane_sensor_error2=vizproximity.Sensor(vizproximity.Box([control_array[1]+.25,.5,control_array[1]+.25],[-x_translate1+50,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error2)
	
	def EnterProximity_left_plane_sensor_error2(left_plane_sensor_error2):
		print('Entered left_plane_error2')
	def ExitProximity_left_plane_sensor_error2(left_plane_sensor_error2):
		global times_entered_left_plane_error2
		times_entered_left_plane_error2+=1
		print('Times entered left plane error2: ', times_entered_left_plane_error2)
	manager.onEnter(left_plane_sensor_error2,EnterProximity_left_plane_sensor_error2)
	manager.onExit(left_plane_sensor_error2,ExitProximity_left_plane_sensor_error2)
	times_entered_left_plane2=0
	times_entered_right_plane2=0
	left_plane_sensor2= vizproximity.Sensor(vizproximity.Box([control_array[1],.25,control_array[1]],[-x_translate1+50,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor2)
	def EnterProximity_left_plane_sensor2(left_plane_sensor2):
		print('Entered left_plane_sensor2')
	
	


	def ExitProximity_left_plane_sensor2(left_plane_sensor2):
		print('Exited left_plane_sensor2')
		global times_entered_left_plane2
		times_entered_left_plane2+=1
		print('Times entered left plane2', times_entered_left_plane2)
	manager.onEnter(left_plane_sensor2,EnterProximity_left_plane_sensor2)
	manager.onExit(left_plane_sensor2,ExitProximity_left_plane_sensor2)
	
	right_plane_sensor_error2=vizproximity.Sensor(vizproximity.Box([control_array[1]+.25,.5,control_array[1]+.25],[x_translate1+50,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error2)
	def EnterProximity_right_plane_sensor_error2(right_plane_sensor_error2):
		print('Entered right_plane_error2')
	def ExitProximity_right_plane_sensor_error2(right_plane_sensor_error2):
		global times_entered_right_plane_error2
		times_entered_right_plane_error2+=1
		print('Times entered right plane error2: ', times_entered_right_plane_error2)
	manager.onEnter(right_plane_sensor_error2,EnterProximity_right_plane_sensor_error2)
	manager.onExit(right_plane_sensor_error2,ExitProximity_right_plane_sensor_error2)
	
	right_plane_sensor2= vizproximity.Sensor(vizproximity.Box([control_array[1],.25,control_array[1]],[x_translate1+50,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor2)
	def EnterProximity_right_plane_sensor2(right_plane_sensor2):
		print('Entered right_plane2')

	

	def ExitProximity_right_plane_sensor2(right_plane_sensor2):
		print('Exited right_plane_sensor2')
		global times_entered_right_plane2
		times_entered_right_plane2+=1
		print('Times Entered right Plane2: ', times_entered_right_plane2)
	manager.onEnter(right_plane_sensor1,EnterProximity_right_plane_sensor2)
	manager.onExit(right_plane_sensor1,ExitProximity_right_plane_sensor2)
	
if x>2:
	times_entered_left_plane_error3=0
	times_entered_right_plane_error3=0
	left_plane_sensor_error3=vizproximity.Sensor(vizproximity.Box([control_array[2]+.25,.5,control_array[2]+.25],[-x_translate1+100,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error3)
	
	def EnterProximity_left_plane_sensor_error3(left_plane_sensor_error3):
		print('Entered left_plane_error3')
	def ExitProximity_left_plane_sensor_error3(left_plane_sensor_error3):
		global times_entered_left_plane_error3
		times_entered_left_plane_error3+=1
		print('Times entered left plane error3: ', times_entered_left_plane_error3)
	manager.onEnter(left_plane_sensor_error3,EnterProximity_left_plane_sensor_error3)
	manager.onExit(left_plane_sensor_error3,ExitProximity_left_plane_sensor_error3)
	
	right_plane_sensor_error3=vizproximity.Sensor(vizproximity.Box([control_array[2]+.25,.5,control_array[2]+.25],[x_translate1+100,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error3)
	def EnterProximity_right_plane_sensor_error3(right_plane_sensor_error3):
		print('Entered right_plane_error3')
	def ExitProximity_right_plane_sensor_error3(right_plane_sensor_error3):
		global times_entered_right_plane_error3
		times_entered_right_plane_error3+=1
		print('Times entered right plane error3: ', times_entered_right_plane_error3)
	manager.onEnter(right_plane_sensor_error3,EnterProximity_right_plane_sensor_error3)
	manager.onExit(right_plane_sensor_error3,ExitProximity_right_plane_sensor_error3)
	times_entered_left_plane3=0
	times_entered_right_plane3=0
	left_plane_sensor3= vizproximity.Sensor(vizproximity.Box([control_array[2],.25,control_array[2]],[-x_translate1+100,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor3)
	def EnterProximity_left_plane_sensor3(left_plane_sensor3):
		print('Entered left_plane_sensor3')
		
	def ExitProximity_left_plane_sensor3(left_plane_sensor2):
		print('Exited left_plane_sensor3')
		global times_entered_left_plane3
		times_entered_left_plane3+=1
		print('Times entered left plane3', times_entered_left_plane3)
	manager.onEnter(left_plane_sensor3,EnterProximity_left_plane_sensor3)
	manager.onExit(left_plane_sensor3,ExitProximity_left_plane_sensor3)
	right_plane_sensor3= vizproximity.Sensor(vizproximity.Box([control_array[2],.25,control_array[2]],[x_translate1+100,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor3)
	def EnterProximity_right_plane_sensor3(right_plane_sensor3):
		print('Entered right_plane3')

	

	def ExitProximity_right_plane_sensor3(right_plane_sensor3):
		print('Exited right_plane_sensor3')
		global times_entered_right_plane3
		times_entered_right_plane3+=1
		print('Times Entered right Plane3: ', times_entered_right_plane3)
	manager.onEnter(right_plane_sensor3,EnterProximity_right_plane_sensor3)
	manager.onExit(right_plane_sensor3,ExitProximity_right_plane_sensor3)
if x>3:
	times_entered_left_plane_error4=0
	times_entered_right_plane_error4=0
	left_plane_sensor_error4=vizproximity.Sensor(vizproximity.Box([control_array[3]+.25,.5,control_array[3]+.25],[-x_translate1+150,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error4)
	
	def EnterProximity_left_plane_sensor_error4(left_plane_sensor_error4):
		print('Entered left_plane_error4')
	def ExitProximity_left_plane_sensor_error4(left_plane_sensor_error4):
		global times_entered_left_plane_error4
		times_entered_left_plane_error4+=1
		print('Times entered left plane error4: ', times_entered_left_plane_error4)
	manager.onEnter(left_plane_sensor_error4,EnterProximity_left_plane_sensor_error4)
	manager.onExit(left_plane_sensor_error4,ExitProximity_left_plane_sensor_error4)
	
	right_plane_sensor_error4=vizproximity.Sensor(vizproximity.Box([control_array[3]+.25,.5,control_array[3]+.25],[x_translate1+150,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error4)
	def EnterProximity_right_plane_sensor_error4(right_plane_sensor_error4):
		print('Entered right_plane_error4')
	def ExitProximity_right_plane_sensor_error4(right_plane_sensor_error4):
		global times_entered_right_plane_error4
		times_entered_right_plane_error4+=1
		print('Times entered right plane error4: ', times_entered_right_plane_error4)
	manager.onEnter(right_plane_sensor_error4,EnterProximity_right_plane_sensor_error4)
	manager.onExit(right_plane_sensor_error4,ExitProximity_right_plane_sensor_error4)
	times_entered_left_plane4=0
	times_entered_right_plane4=0
	left_plane_sensor4= vizproximity.Sensor(vizproximity.Box([control_array[3],.25,control_array[3]],[-x_translate1+150,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor4)
	def EnterProximity_left_plane_sensor4(left_plane_sensor4):
		print('Entered left_plane_sensor4')
	
	


	def ExitProximity_left_plane_sensor4(left_plane_sensor4):
		print('Exited left_plane_sensor4')
		global times_entered_left_plane4
		times_entered_left_plane4+=1
		print('Times entered left plane4', times_entered_left_plane4)
	manager.onEnter(left_plane_sensor4,EnterProximity_left_plane_sensor4)
	manager.onExit(left_plane_sensor4,ExitProximity_left_plane_sensor4)
	
	right_plane_sensor4= vizproximity.Sensor(vizproximity.Box([control_array[3],.25,control_array[3]],[x_translate1+150,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor4)
	def EnterProximity_right_plane_sensor4(right_plane_sensor4):
		print('Entered right_plane4')

	

	def ExitProximity_right_plane_sensor4(right_plane_sensor4):
		print('Exited right_plane_sensor4')
		global times_entered_right_plane4
		times_entered_right_plane4+=1
		print('Times Entered right Plane4: ', times_entered_right_plane4)
	manager.onEnter(right_plane_sensor4,EnterProximity_right_plane_sensor4)
	manager.onExit(right_plane_sensor4,ExitProximity_right_plane_sensor4)
if x>4:
	times_entered_left_plane_error5=0
	times_entered_right_plane_error5=0
	left_plane_sensor_error5=vizproximity.Sensor(vizproximity.Box([control_array[4]+.25,.5,control_array[4]+.25],[-x_translate1+200,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error5)
	
	def EnterProximity_left_plane_sensor_error5(left_plane_sensor_error5):
		print('Entered left_plane_error5')
	def ExitProximity_left_plane_sensor_error5(left_plane_sensor_error5):
		global times_entered_left_plane_error5
		times_entered_left_plane_error5+=1
		print('Times entered left plane error5: ', times_entered_left_plane_error5)
	manager.onEnter(left_plane_sensor_error5,EnterProximity_left_plane_sensor_error5)
	manager.onExit(left_plane_sensor_error5,ExitProximity_left_plane_sensor_error5)
	
	right_plane_sensor_error5=vizproximity.Sensor(vizproximity.Box([control_array[4]+.25,.5,control_array[4]+.25],[x_translate1+200,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error5)
	def EnterProximity_right_plane_sensor_error5(right_plane_sensor_error5):
		print('Entered right_plane_error5')
	def ExitProximity_right_plane_sensor_error5(right_plane_sensor_error5):
		global times_entered_right_plane_error5
		times_entered_right_plane_error5+=1
		print('Times entered right plane error5: ', times_entered_right_plane_error5)
	manager.onEnter(right_plane_sensor_error5,EnterProximity_right_plane_sensor_error5)
	manager.onExit(right_plane_sensor_error5,ExitProximity_right_plane_sensor_error5)
	times_entered_left_plane5=0
	times_entered_right_plane5=0
	left_plane_sensor5= vizproximity.Sensor(vizproximity.Box([control_array[4],.25,control_array[4]],[-x_translate1+200,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor5)
	def EnterProximity_left_plane_sensor5(left_plane_sensor5):
		print('Entered left_plane_sensor5')
	def ExitProximity_left_plane_sensor5(left_plane_sensor5):
		print('Exited left_plane_sensor5')
		global times_entered_left_plane5
		times_entered_left_plane5+=1
		print('Times entered left plane5', times_entered_left_plane5)
	manager.onEnter(left_plane_sensor5,EnterProximity_left_plane_sensor4)
	manager.onExit(left_plane_sensor5,ExitProximity_left_plane_sensor5)
	
	right_plane_sensor5= vizproximity.Sensor(vizproximity.Box([control_array[4],.25,control_array[4]],[x_translate1+200,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor5)
	def EnterProximity_right_plane_sensor5(right_plane_sensor5):
		print('Entered right_plane5')

	

	def ExitProximity_right_plane_sensor5(right_plane_sensor5):
		print('Exited right_plane_sensor5')
		global times_entered_right_plane5
		times_entered_right_plane5+=1
		print('Times Entered right Plane5: ', times_entered_right_plane5)
	manager.onEnter(right_plane_sensor5,EnterProximity_right_plane_sensor5)
	manager.onExit(right_plane_sensor5,ExitProximity_right_plane_sensor5)
if x>5:
	times_entered_left_plane_error6=0
	times_entered_right_plane_error6=0
	left_plane_sensor_error6=vizproximity.Sensor(vizproximity.Box([control_array[5]+.25,.5,control_array[5]+.25],[-x_translate1+250,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error6)
	
	def EnterProximity_left_plane_sensor_error6(left_plane_sensor_error6):
		print('Entered left_plane_error6')
	def ExitProximity_left_plane_sensor_error6(left_plane_sensor_error6):
		global times_entered_left_plane_error6
		times_entered_left_plane_error6+=1
		print('Times entered left plane error6: ', times_entered_left_plane_error6)
	manager.onEnter(left_plane_sensor_error6,EnterProximity_left_plane_sensor_error6)
	manager.onExit(left_plane_sensor_error6,ExitProximity_left_plane_sensor_error6)
	
	right_plane_sensor_error6=vizproximity.Sensor(vizproximity.Box([control_array[5]+.25,.5,control_array[5]+.25],[x_translate1+250,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error6)
	def EnterProximity_right_plane_sensor_error6(right_plane_sensor_error6):
		print('Entered right_plane_error6')
	def ExitProximity_right_plane_sensor_error6(right_plane_sensor_error6):
		global times_entered_right_plane_error6
		times_entered_right_plane_error6+=1
		print('Times entered right plane error6: ', times_entered_right_plane_error6)
	manager.onEnter(right_plane_sensor_error6,EnterProximity_right_plane_sensor_error6)
	manager.onExit(right_plane_sensor_error6,ExitProximity_right_plane_sensor_error6)
	times_entered_left_plane6=0
	times_entered_right_plane6=0
	left_plane_sensor6= vizproximity.Sensor(vizproximity.Box([control_array[5],.25,control_array[5]],[-x_translate1+250,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor6)
	def EnterProximity_left_plane_sensor6(left_plane_sensor6):
		print('Entered left_plane_sensor6')
	def ExitProximity_left_plane_sensor6(left_plane_sensor6):
		print('Exited left_plane_sensor6')
		global times_entered_left_plane6
		times_entered_left_plane6+=1
		print('Times entered left plane6', times_entered_left_plane6)
	manager.onEnter(left_plane_sensor6,EnterProximity_left_plane_sensor6)
	manager.onExit(left_plane_sensor6,ExitProximity_left_plane_sensor6)
	
	right_plane_sensor6= vizproximity.Sensor(vizproximity.Box([control_array[5],.25,control_array[5]],[x_translate1+250,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor6)
	def EnterProximity_right_plane_sensor6(right_plane_sensor6):
		print('Entered right_plane6')

	

	def ExitProximity_right_plane_sensor6(right_plane_sensor6):
		print('Exited right_plane_sensor6')
		global times_entered_right_plane6
		times_entered_right_plane6+=1
		print('Times Entered right Plane6: ', times_entered_right_plane6)
	manager.onEnter(right_plane_sensor6,EnterProximity_right_plane_sensor6)
	manager.onExit(right_plane_sensor6,ExitProximity_right_plane_sensor6)
if x>6:
	times_entered_left_plane_error7=0
	times_entered_right_plane_error7=0
	left_plane_sensor_error7=vizproximity.Sensor(vizproximity.Box([control_array[6]+.25,.5,control_array[6]+.25],[-x_translate1+300,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error7)
	
	def EnterProximity_left_plane_sensor_error7(left_plane_sensor_error7):
		print('Entered left_plane_error7')
	def ExitProximity_left_plane_sensor_error7(left_plane_sensor_error7):
		global times_entered_left_plane_error7
		times_entered_left_plane_error7+=1
		print('Times entered left plane error7: ', times_entered_left_plane_error7)
	manager.onEnter(left_plane_sensor_error7,EnterProximity_left_plane_sensor_error7)
	manager.onExit(left_plane_sensor_error7,ExitProximity_left_plane_sensor_error7)
	
	right_plane_sensor_error7=vizproximity.Sensor(vizproximity.Box([control_array[6]+.25,.5,control_array[6]+.25],[x_translate1+300,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error7)
	def EnterProximity_right_plane_sensor_error7(right_plane_sensor_error7):
		print('Entered right_plane_error7')
	def ExitProximity_right_plane_sensor_error7(right_plane_sensor_error7):
		global times_entered_right_plane_error7
		times_entered_right_plane_error7+=1
		print('Times entered right plane error7: ', times_entered_right_plane_error7)
	manager.onEnter(right_plane_sensor_error7,EnterProximity_right_plane_sensor_error7)
	manager.onExit(right_plane_sensor_error7,ExitProximity_right_plane_sensor_error7)
	times_entered_left_plane6=0
	times_entered_right_plane6=0
	left_plane_sensor6= vizproximity.Sensor(vizproximity.Box([control_array[5],.25,control_array[5]],[-x_translate1+250,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor6)
	def EnterProximity_left_plane_sensor6(left_plane_sensor6):
		print('Entered left_plane_sensor6')
	def ExitProximity_left_plane_sensor6(left_plane_sensor6):
		print('Exited left_plane_sensor6')
		global times_entered_left_plane6
		times_entered_left_plane6+=1
		print('Times entered left plane6', times_entered_left_plane6)
	manager.onEnter(left_plane_sensor6,EnterProximity_left_plane_sensor6)
	manager.onExit(left_plane_sensor6,ExitProximity_left_plane_sensor6)
	times_entered_left_plane7=0
	times_entered_right_plane7=0
	left_plane_sensor7= vizproximity.Sensor(vizproximity.Box([control_array[6],.25,control_array[6]],[-x_translate1+300,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor7)
	def EnterProximity_left_plane_sensor7(left_plane_sensor7):
		print('Entered left_plane_sensor7')
	def ExitProximity_left_plane_sensor7(left_plane_sensor7):
		print('Exited left_plane_sensor7')
		global times_entered_left_plane7
		times_entered_left_plane7+=1
		print('Times entered left plane7', times_entered_left_plane7)
	manager.onEnter(left_plane_sensor7,EnterProximity_left_plane_sensor7)
	manager.onExit(left_plane_sensor7,ExitProximity_left_plane_sensor7)
	
	right_plane_sensor7= vizproximity.Sensor(vizproximity.Box([control_array[6],.25,control_array[6]],[x_translate1+300,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor7)
	def EnterProximity_right_plane_sensor7(right_plane_sensor7):
		print('Entered right_plane7')

	

	def ExitProximity_right_plane_sensor7(right_plane_sensor7):
		print('Exited right_plane_sensor7')
		global times_entered_right_plane7
		times_entered_right_plane7+=1
		print('Times Entered right Plane7: ', times_entered_right_plane7)
	manager.onEnter(right_plane_sensor7,EnterProximity_right_plane_sensor7)
	manager.onExit(right_plane_sensor7,ExitProximity_right_plane_sensor7)
if x>7:
	times_entered_left_plane_error8=0
	times_entered_right_plane_error8=0
	left_plane_sensor_error8=vizproximity.Sensor(vizproximity.Box([control_array[7]+.25,.5,control_array[7]+.25],[-x_translate1+350,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error8)
	
	def EnterProximity_left_plane_sensor_error8(left_plane_sensor_error8):
		print('Entered left_plane_error8')
	def ExitProximity_left_plane_sensor_error8(left_plane_sensor_error8):
		global times_entered_left_plane_error8
		times_entered_left_plane_error8+=1
		print('Times entered left plane error8: ', times_entered_left_plane_error8)
	manager.onEnter(left_plane_sensor_error8,EnterProximity_left_plane_sensor_error8)
	manager.onExit(left_plane_sensor_error8,ExitProximity_left_plane_sensor_error8)
	
	right_plane_sensor_error8=vizproximity.Sensor(vizproximity.Box([control_array[7]+.25,.5,control_array[7]+.25],[x_translate1+350,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error8)
	def EnterProximity_right_plane_sensor_error8(right_plane_sensor_error8):
		print('Entered right_plane_error8')
	def ExitProximity_right_plane_sensor_error8(right_plane_sensor_error8):
		global times_entered_right_plane_error8
		times_entered_right_plane_error8+=1
		print('Times entered right plane error8: ', times_entered_right_plane_error8)
	manager.onEnter(right_plane_sensor_error8,EnterProximity_right_plane_sensor_error8)
	manager.onExit(right_plane_sensor_error8,ExitProximity_right_plane_sensor_error8)
	times_entered_left_plane8=0
	times_entered_right_plane8=0
	left_plane_sensor8= vizproximity.Sensor(vizproximity.Box([control_array[7],.25,control_array[7]],[-x_translate1+350,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor8)
	def EnterProximity_left_plane_sensor8(left_plane_sensor8):
		print('Entered left_plane_sensor8')
	def ExitProximity_left_plane_sensor8(left_plane_sensor8):
		print('Exited left_plane_sensor8')
		global times_entered_left_plane8
		times_entered_left_plane8+=1
		print('Times entered left plane8', times_entered_left_plane8)
	manager.onEnter(left_plane_sensor8,EnterProximity_left_plane_sensor8)
	manager.onExit(left_plane_sensor8,ExitProximity_left_plane_sensor8)
	
	right_plane_sensor8= vizproximity.Sensor(vizproximity.Box([control_array[7],.25,control_array[7]],[x_translate1+350,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor8)
	def EnterProximity_right_plane_sensor8(right_plane_sensor8):
		print('Entered right_plane8')

	

	def ExitProximity_right_plane_sensor8(right_plane_sensor8):
		print('Exited right_plane_sensor8')
		global times_entered_right_plane8
		times_entered_right_plane8+=1
		print('Times Entered right Plane8: ', times_entered_right_plane8)
	manager.onEnter(right_plane_sensor8,EnterProximity_right_plane_sensor8)
	manager.onExit(right_plane_sensor8,ExitProximity_right_plane_sensor8)

if x>8:
	times_entered_left_plane_error9=0
	times_entered_right_plane_error9=0
	left_plane_sensor_error9=vizproximity.Sensor(vizproximity.Box([control_array[8]+.25,.5,control_array[8]+.25],[-x_translate1+400,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error9)
	
	def EnterProximity_left_plane_sensor_error9(left_plane_sensor_error9):
		print('Entered left_plane_error9')
	def ExitProximity_left_plane_sensor_error9(left_plane_sensor_error9):
		global times_entered_left_plane_error9
		times_entered_left_plane_error9+=1
		print('Times entered left plane error9: ', times_entered_left_plane_error9)
	manager.onEnter(left_plane_sensor_error9,EnterProximity_left_plane_sensor_error9)
	manager.onExit(left_plane_sensor_error9,ExitProximity_left_plane_sensor_error9)
	
	right_plane_sensor_error9=vizproximity.Sensor(vizproximity.Box([control_array[8]+.25,.5,control_array[8]+.25],[x_translate1+400,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error9)
	def EnterProximity_right_plane_sensor_error9(right_plane_sensor_error9):
		print('Entered right_plane_error9')
	def ExitProximity_right_plane_sensor_error9(right_plane_sensor_error9):
		global times_entered_right_plane_error9
		times_entered_right_plane_error9+=1
		print('Times entered right plane error9: ', times_entered_right_plane_error9)
	manager.onEnter(right_plane_sensor_error9,EnterProximity_right_plane_sensor_error9)
	manager.onExit(right_plane_sensor_error9,ExitProximity_right_plane_sensor_error9)
	times_entered_left_plane9=0
	times_entered_right_plane9=0
	left_plane_sensor9= vizproximity.Sensor(vizproximity.Box([control_array[8],.25,control_array[8]],[-x_translate1+400,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor9)
	def EnterProximity_left_plane_sensor9(left_plane_sensor9):
		print('Entered left_plane_sensor9')
	def ExitProximity_left_plane_sensor9(left_plane_sensor9):
		print('Exited left_plane_sensor9')
		global times_entered_left_plane9
		times_entered_left_plane9+=1
		print('Times entered left plane9', times_entered_left_plane9)
	manager.onEnter(left_plane_sensor9,EnterProximity_left_plane_sensor9)
	manager.onExit(left_plane_sensor9,ExitProximity_left_plane_sensor9)
	
	right_plane_sensor9= vizproximity.Sensor(vizproximity.Box([control_array[8],.25,control_array[8]],[x_translate1+400,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor9)
	def EnterProximity_right_plane_sensor9(right_plane_sensor9):
		print('Entered right_plane9')

	

	def ExitProximity_right_plane_sensor9(right_plane_sensor9):
		print('Exited right_plane_sensor9')
		global times_entered_right_plane9
		times_entered_right_plane9+=1
		print('Times Entered right Plane9: ', times_entered_right_plane9)
	manager.onEnter(right_plane_sensor9,EnterProximity_right_plane_sensor9)
	manager.onExit(right_plane_sensor9,ExitProximity_right_plane_sensor9)

if x>9:
	times_entered_left_plane_error10=0
	times_entered_right_plane_error10=0
	left_plane_sensor_error10=vizproximity.Sensor(vizproximity.Box([control_array[9]+.25,.5,control_array[9]+.25],[-x_translate1+450,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error10)
	
	def EnterProximity_left_plane_sensor_error10(left_plane_sensor_error10):
		print('Entered left_plane_error10')
	def ExitProximity_left_plane_sensor_error10(left_plane_sensor_error10):
		global times_entered_left_plane_error10
		times_entered_left_plane_error10+=1
		print('Times entered left plane error10: ', times_entered_left_plane_error10)
	manager.onEnter(left_plane_sensor_error10,EnterProximity_left_plane_sensor_error10)
	manager.onExit(left_plane_sensor_error10,ExitProximity_left_plane_sensor_error10)
	
	right_plane_sensor_error10=vizproximity.Sensor(vizproximity.Box([control_array[9]+.25,.5,control_array[9]+.25],[x_translate1+450,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error10)
	def EnterProximity_right_plane_sensor_error10(right_plane_sensor_error10):
		print('Entered right_plane_error10')
	def ExitProximity_right_plane_sensor_error10(right_plane_sensor_error10):
		global times_entered_right_plane_error10
		times_entered_right_plane_error10+=1
		print('Times entered right plane error10: ', times_entered_right_plane_error10)
	manager.onEnter(right_plane_sensor_error10,EnterProximity_right_plane_sensor_error10)
	manager.onExit(right_plane_sensor_error10,ExitProximity_right_plane_sensor_error10)
	times_entered_left_plane10=0
	times_entered_right_plane10=0
	left_plane_sensor10= vizproximity.Sensor(vizproximity.Box([control_array[9],.25,control_array[9]],[-x_translate1+450,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor10)
	def EnterProximity_left_plane_sensor10(left_plane_sensor10):
		print('Entered left_plane_sensor10')
	def ExitProximity_left_plane_sensor10(left_plane_sensor10):
		print('Exited left_plane_sensor10')
		global times_entered_left_plane10
		times_entered_left_plane10+=1
		print('Times entered left plane10', times_entered_left_plane10)
	manager.onEnter(left_plane_sensor10,EnterProximity_left_plane_sensor10)
	manager.onExit(left_plane_sensor10,ExitProximity_left_plane_sensor10)
	
	right_plane_sensor10= vizproximity.Sensor(vizproximity.Box([control_array[9],.25,control_array[9]],[x_translate1+450,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor10)
	def EnterProximity_right_plane_sensor10(right_plane_sensor10):
		print ('Entered right_plane10')
	

	def ExitProximity_right_plane_sensor10(right_plane_sensor10):
		print('Exited right_plane_sensor10')
		global times_entered_right_plane10
		times_entered_right_plane10+=1
		print('Times Entered right Plane10: ', times_entered_right_plane10)
	manager.onEnter(right_plane_sensor10,EnterProximity_right_plane_sensor10)
	manager.onExit(right_plane_sensor10,ExitProximity_right_plane_sensor10)
if x>10:
	times_entered_left_plane_error11=0
	times_entered_right_plane_error11=0
	left_plane_sensor_error11=vizproximity.Sensor(vizproximity.Box([control_array[10]+.25,.5,control_array[10]+.25],[-x_translate1+500,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error11)
	
	def EnterProximity_left_plane_sensor_error11(left_plane_sensor_error11):
		print('Entered left_plane_error11')
	def ExitProximity_left_plane_sensor_error11(left_plane_sensor_error11):
		global times_entered_left_plane_error11
		times_entered_left_plane_error11+=1
		print('Times entered left plane error11: ', times_entered_left_plane_error11)
	manager.onEnter(left_plane_sensor_error11,EnterProximity_left_plane_sensor_error11)
	manager.onExit(left_plane_sensor_error11,ExitProximity_left_plane_sensor_error11)
	
	right_plane_sensor_error11=vizproximity.Sensor(vizproximity.Box([control_array[10]+.25,.5,control_array[10]+.25],[x_translate1+500,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error11)
	def EnterProximity_right_plane_sensor_error11(right_plane_sensor_error11):
		print('Entered right_plane_error11')
	def ExitProximity_right_plane_sensor_error11(right_plane_sensor_error11):
		global times_entered_right_plane_error11
		times_entered_right_plane_error11+=1
		print('Times entered right plane error11: ', times_entered_right_plane_error11)
	manager.onEnter(right_plane_sensor_error11,EnterProximity_right_plane_sensor_error11)
	manager.onExit(right_plane_sensor_error11,ExitProximity_right_plane_sensor_error11)	
	times_entered_left_plane11=0
	times_entered_right_plane11=0
	left_plane_sensor11= vizproximity.Sensor(vizproximity.Box([control_array[10],.25,control_array[10]],[-x_translate1+500,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor11)
	def EnterProximity_left_plane_sensor11(left_plane_sensor11):
		print('Entered left_plane_sensor11')
	def ExitProximity_left_plane_sensor11(left_plane_sensor11):
		print('Exited left_plane_sensor11')
		global times_entered_left_plane11
		times_entered_left_plane11+=1
		print('Times entered left plane11', times_entered_left_plane11)
	manager.onEnter(left_plane_sensor11,EnterProximity_left_plane_sensor11)
	manager.onExit(left_plane_sensor11,ExitProximity_left_plane_sensor11)
	
	right_plane_sensor11= vizproximity.Sensor(vizproximity.Box([control_array[10],.25,control_array[10]],[x_translate1+500,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor11)
	def EnterProximity_right_plane_sensor11(right_plane_sensor11):
		print('Entered right_plane11')
	

	def ExitProximity_right_plane_sensor11(right_plane_sensor11):
		print('Exited right_plane_sensor11')
		global times_entered_right_plane11
		times_entered_right_plane11+=1
		print('Times Entered right Plane11: ', times_entered_right_plane11)
	manager.onEnter(right_plane_sensor11,EnterProximity_right_plane_sensor11)
	manager.onExit(right_plane_sensor11,ExitProximity_right_plane_sensor11)
if x>11:
	times_entered_left_plane_error12=0
	times_entered_right_plane_error12=0
	left_plane_sensor_error12=vizproximity.Sensor(vizproximity.Box([control_array[11]+.25,.5,control_array[11]+.25],[-x_translate1+550,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error12)
	
	def EnterProximity_left_plane_sensor_error12(left_plane_sensor_error12):
		print('Entered left_plane_error12')
	def ExitProximity_left_plane_sensor_error12(left_plane_sensor_error12):
		global times_entered_left_plane_error12
		times_entered_left_plane_error12+=1
		print('Times entered left plane error12: ', times_entered_left_plane_error12)
	manager.onEnter(left_plane_sensor_error12,EnterProximity_left_plane_sensor_error12)
	manager.onExit(left_plane_sensor_error12,ExitProximity_left_plane_sensor_error12)
	
	right_plane_sensor_error12=vizproximity.Sensor(vizproximity.Box([control_array[11]+.25,.5,control_array[11]+.25],[x_translate1+550,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error12)
	def EnterProximity_right_plane_sensor_error12(right_plane_sensor_error12):
		print('Entered right_plane_error12')
	def ExitProximity_right_plane_sensor_error12(right_plane_sensor_error12):
		global times_entered_right_plane_error12
		times_entered_right_plane_error12+=1
		print('Times entered right plane error12: ', times_entered_right_plane_error12)
	manager.onEnter(right_plane_sensor_error12,EnterProximity_right_plane_sensor_error12)
	manager.onExit(right_plane_sensor_error12,ExitProximity_right_plane_sensor_error12)	
	times_entered_left_plane12=0
	times_entered_right_plane12=0
	left_plane_sensor12= vizproximity.Sensor(vizproximity.Box([control_array[11],.25,control_array[11]],[-x_translate1+550,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor12)
	def EnterProximity_left_plane_sensor12(left_plane_sensor12):
		print('Entered left_plane_sensor12')
	def ExitProximity_left_plane_sensor12(left_plane_sensor12):
		print('Exited left_plane_sensor12')
		global times_entered_left_plane12
		times_entered_left_plane12+=1
		print('Times entered left plane12', times_entered_left_plane12)
	manager.onEnter(left_plane_sensor12,EnterProximity_left_plane_sensor12)
	manager.onExit(left_plane_sensor12,ExitProximity_left_plane_sensor12)
	
	right_plane_sensor12= vizproximity.Sensor(vizproximity.Box([control_array[11],.25,control_array[11]],[x_translate1+550,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor12)
	def EnterProximity_right_plane_sensor12(right_plane_sensor12):
		print('Entered right_plane1')
	

	def ExitProximity_right_plane_sensor12(right_plane_sensor12):
		print('Exited right_plane_sensor12')
		global times_entered_right_plane12
		times_entered_right_plane12+=1
		print('Times Entered right Plane12: ', times_entered_right_plane12)
	manager.onEnter(right_plane_sensor12,EnterProximity_right_plane_sensor12)
	manager.onExit(right_plane_sensor12,ExitProximity_right_plane_sensor12)
#create sensors
#still need to make a set of left/right sensors/proximity functions for left_plane2/3 and right_plane 2/3
#left_plane_sensor1= vizproximity.Sensor(vizproximity.Box([scale_x1,.25,scale_x1],[-x_translate1,y_height1,z_depth1]),left_node1)
#manager.addSensor(left_plane_sensor1)
#right_plane_sensor1= vizproximity.Sensor(vizproximity.Box([scale_x1,.25,scale_x1],[x_translate1,y_height1,z_depth1]),right_node1)
#manager.addSensor(right_plane_sensor1)

mid_plane_sensor= vizproximity.Sensor(vizproximity.Box([.025,20,20],center=[0,0,0]),source = mid_plane)
manager.addSensor(mid_plane_sensor)        
     
start_sensor=vizproximity.Sensor(vizproximity.Box([scale_x1,.25,scale_x1],center=[0,0,0]),start_node)
manager.addSensor(start_sensor)

end_sensor=vizproximity.Sensor(vizproximity.Box([scale_x1,1,scale_x1],center= [x_translate_shifted1, y_height1,z_depth1]),end_node)
manager.addSensor(end_sensor)

    
def timer3():
	global reaction_timer_initial
	viz.playSound('boing!.wav')
	a=viz.tick()
	global timer2
	reaction_timer_initial=viz.tick()
	
def EnterProximity_start_sensor(start_sensor):
	vizact.ontimer2(1,0, timer3)
	global times_entered_start_plane
	times_entered_start_plane =times_entered_start_plane+1
	print('Entered start_sensor',str(times_entered_start_plane))

	
	
	
	
	
right1=100
right2=100
iter_count=0
def shift_all_planes(x):
	global iter_count
	
	global right2
	right2=right2-50
	if (x>0 and iter_count==0):
		right_plane1.setPosition(x_translate1,y_height1,z_depth1)
		left_plane1.setPosition(-x_translate1,y_height1,z_depth1)
	elif (x>1 and iter_count==1):
		left_plane1.translate(0,50,0)
		left_plane2.translate(-x_translate1,y_height1,z_depth1)
		right_plane1.translate(0,50,0)
		right_plane2.translate(x_translate1,y_height1,z_depth1)
	elif (x>2 and iter_count==2):
		left_plane2.translate(0,50,0)
		left_plane3.translate(-x_translate1,y_height1,z_depth1)
		right_plane2.translate(0,50,0)
		right_plane3.translate(x_translate1,y_height1,z_depth1)
	elif (x>3 and iter_count==3):
		left_plane3.translate(0,50,0)
		left_plane4.translate(-x_translate1,y_height1,z_depth1)
		right_plane3.translate(0,50,0)
		right_plane4.translate(x_translate1,y_height1,z_depth1)
	elif (x>4 and iter_count==4):
		left_plane4.translate(0,50,0)
		left_plane5.translate(-x_translate1,y_height1,z_depth1)
		right_plane4.translate(0,50,0)
		right_plane5.translate(x_translate1,y_height1,z_depth1)
	elif (x>5 and iter_count==5):
		left_plane5.translate(0,50,0)
		left_plane6.translate(-x_translate1,y_height1,z_depth1)
		right_plane5.translate(0,50,0)
		right_plane6.translate(x_translate1,y_height1,z_depth1)
	elif (x>6 and iter_count==6):
		left_plane6.translate(0,50,0)
		left_plane7.translate(-x_translate1,y_height1,z_depth1)
		right_plane6.translate(0,50,0)
		right_plane7.translate(x_translate1,y_height1,z_depth1)
	elif (x>7 and iter_count==7):
		left_plane7.translate(0,50,0)
		left_plane8.translate(-x_translate1,y_height1,z_depth1)
		right_plane7.translate(0,50,0)
		right_plane8.translate(x_translate1,y_height1,z_depth1)
	elif (x>8 and iter_count==8):
		left_plane8.translate(0,50,0)
		left_plane9.translate(-x_translate1,y_height1,z_depth1)
		right_plane8.translate(0,50,0)
		right_plane9.translate(x_translate1,y_height1,z_depth1)
	elif (x>9 and iter_count==9):
		left_plane9.translate(0,50,0)
		left_plane10.translate(-x_translate1,y_height1,z_depth1)
		right_plane9.translate(0,50,0)
		right_plane10.translate(x_translate1,y_height1,z_depth1)
	elif (x>10 and iter_count==10):
		left_plane10.translate(0,50,0)
		left_plane11.translate(-x_translate1,y_height1,z_depth1)
		right_plane10.translate(0,50,0)
		right_plane11.translate(x_translate1,y_height1,z_depth1)
	elif (x>11 and iter_count==11):
		left_plane11.translate(0,50,0)
		left_plane12.translate(-x_translate1,y_height1,z_depth1)
		right_plane11.translate(0,50,0)
		right_plane12.translate(x_translate1,y_height1,z_depth1)

	
		
		
		print('in 2nd loop')
#	if x>0:
#		right_plane1.translate(x_translate1+right2-50,y_height1,z_depth1)
	iter_count+=1
		
def ExitProximity_start_sensor(start_sensor):
	global right1
	global x
	global reaction_timer_final
	right1=right1-50
	start_node.translate(0,100,0)
	right_node1.translate(right1-50,0,0)
	left_node1.translate(right1-50,0,0)
	end_node.setPosition(0,0,0)
	end_box.setPosition(x_translate_shifted1,y_height1,z_depth1)
	shift_all_planes(x)
	reaction_timer_final=viz.tick()
	

def EnterProximity_end_sensor(end_sensor):
	global right
	global times_crossed
	global subj_numb
	global tri_per_subj
	global a
	global b
	
	
	
	trial=b+1
	box_size=control_array[a]
	distance=distance_between_targets1*2
	num_cycles= times_crossed-1
	reaction_time=round((reaction_timer_final-reaction_timer_initial),2)
	
#	main_data.write('\n'+' '*2+ str(subj_numb))
#	main_data.write(' '*7 + str(trial))
#	main_data.write(' '*9 + str(box_size))
#	main_data.write(' '*9 + str(distance_between_targets1))
	main_data.write('\n' + str(reaction_time))
#	main_data.write(' '*3 + str(num_cycles))
	if b+1==int(tri_per_subj):
		subj_numb=vizinput.input('Please input the Subject Number:\n ')
		tri_per_subj=vizinput.input('Please input how many trials this subject will go through:\n ')
		print('in da loop')
		b=-1	
	b+=1
	a+=1	
	print(a)
	print(b)
	start_node.translate(x_translate1,y_height1,z_depth1)
	end_node.translate(0,100,0)
	end_box.translate(0,100,0)
	right_node1.translate(0,100,0)
#	left_node1.translate(right-50,0,0)
#	right_node1.setPosition(0,100,0)

	print('Entered end_sensor')
	
def array_manipulator(array):
	global scale_x1
	global times_entered_end_plane
	scale_x1=array[times_entered_end_plane-1]
	return scale_x1
def ExitProximity_end_sensor(end_sensor):
	global times_entered_end_plane
	global scale_x1
	times_entered_end_plane=+1
	
	
manager.onEnter(end_sensor,EnterProximity_end_sensor)
manager.onExit(end_sensor,ExitProximity_end_sensor)	

manager.onEnter(start_sensor,EnterProximity_start_sensor)
manager.onExit(start_sensor,ExitProximity_start_sensor)
#print the enter/exits of cyl2

def EnterProximity_right_plane_sensor1(right_plane_sensor1):
	print('Entered right_plane1')
	

def ExitProximity_right_plane_sensor1(right_plane_sensor1):
    print('Exited right_plane_sensor1')
    global times_entered_right_plane
    times_entered_right_plane+=1
    print('Times Entered right Plane1: ', times_entered_right_plane)

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
    
manager.onEnter(mid_plane_sensor,EnterProximity_mid_plane_sensor)
manager.onExit(mid_plane_sensor,ExitProximity_mid_plane_sensor)
# when tracking use: target = vizproximity.Target((stupidhand)) 
#We currently have the tracking as main view 
#be able to time from a t(0) to the end of the cycles. be able to start the timer yourself.
#be able to record/save? how many cycles they do
#they will start in a square. once they leave the square, the time should start. the first exit implies time trial starting. 

target = vizproximity.Target(viz.MainView)
manager.addTarget(target)

array_manipulator(control_array)
viz.move(0,1.5,2) 
vizact.onkeydown('d',manager.setDebug,viz.TOGGLE)   
viz.go()

