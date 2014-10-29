"""This is a comment reminding you that the start box is currently being calculated. There is no
set value for it.It takes the highest possible box size and uses that for the start box dimensions. 
This is the Fitt. experiment that includes both visual and auditory cues."""

#general viz module
import viz
#vizinfo is used along w/ vizinput to gather input throughout the program 
import vizinfo
#vizshape is used for the creation and manipulation of the box sensors and tiles. 
import vizshape
#vizmath is used for various mathematical operations used in the program. 
import math
#import vizact
import viztask
#vizproximity is used for the creation and function of all proximity sensors.
import vizproximity
#viztracker2/viztracker is used for tracking the position and orientation of the head and hand. 
import viztracker3 as viztracker
#we will import everything from viztracker
from viztracker import*
#viztime is used primarilly for the viz.tick() function, which captures the value of the internal clock 
#that goes on in during vizard's runtime. 
import time
#vizinput is used along w/ vizinfo to gather input throughout the program 
import vizinput
#viz_matrix is a module that contains all the arrays for the control arrays we will use. 
import viz_matrix



#General screen setup. 
viz.setMultiSample(4)
viz.fov(60)

#Sometimes, the first "start" sound does not work. The second time, it always works, therefore, I have the start sound
#play when the program starts. This way, there is no chance of the sound not working when the experiment starts. 
viz.playSound('boing!.wav')

"""In viz_matrix, we have many arrays of possible orders of box lengths. Each has a distinct identifiying number, called
 a 'matrix id.' By knowing this in advance, the user inputs the matrix id when the program starts, and the viz_matrix
program will find the respective matrix for the trials.""" 
matrix_id=vizinput.input('Input Matrix ID Number:\n ')
#throughout the program, you may see "prints." This is only seen in the interactive window, and is used only for debugging
#the subject does not see any of the printed messages during experimentation. 
print('matrix_id'+ str(matrix_id))


#our control_array is the array that we have chosen when typing in the matrx_id
control_array=viz_matrix.matrix_controller(matrix_id)
#x is the length of the control array. our program acts differently based on the size of x. in other words,
# there are many conditional trees that are dependant on the size of x. 
x=len(control_array)
#max_lst=[]
#for p in control_array:
#	max_lst.append(p)
#max_lst.sort()
#max_lst.reverse()
#print('max_lst'+str(max_lst))

maximum_size=max(control_array)	
print(control_array)
#set global variables to 0. We will change these later. I will explain the when we use them. 
iter3=0
error_iter=0
a=0
b= int(vizinput.input('Input trial number: '))-1
reaction_timer_initial= 0
reaction_timer_final= 0
#main_data is the text file where all the data is written and saved to. The format currently is accurate with notepad. May
#be off in other text editors.
name=vizinput.input('Input name of file: ') 
main_data= open(name, 'a')
#The prompt for the subject number. 
subj_numb=vizinput.input('Please input the Subject Number:\n ')
#The prompt for the # of trials per subject. 
tri_per_subj=vizinput.input('Please input how many trials this subject will go through:\n ')
def write_func():
	#During debugging, we will truncate, though we should not during experimentation. 
#	main_data.truncate()
	"""Writing the main table. Subj#= Subjecting Number, Ord= Order, Tri#= Trial Number, BxSz= Box Size, 
	Dis=Distance between the two boxes, RT= Reaction Time, MT= Movement Time, #Crs= Number of Crosses 
	#Err= Number of Errors Xp,Yp,Zp= X,Y,and Z coordinate positions of the hand."""
#	main_data.write('Sub# Ord Tri# BxSz Dis RT   MT   #Crs #Err      Xp Yp Zp')	

write_func()
	
	
	
	
	
#We need to creat all 20 left and right planes, though we may not use all 20. 
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
left_plane13=0
left_plane14=0
left_plane15=0
left_plane16=0
left_plane17=0
left_plane18=0
left_plane19=0
left_plane20=0

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
right_plane13=0
right_plane14=0
right_plane15=0
right_plane16=0
right_plane17=0
right_plane18=0
right_plane19=0
right_plane20=0

#setting global variables to 0. 
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
scale_x1= 0

scale_z1=5
scale_x2=0

scale_z2=0
scale_x3=0

scale_z3=0
#The distance between targets. For now, we are only using the first one. 
distance_between_targets1=.15

#The height of the targets. 
y_height1= .74 

#NEW Y ALGORITHM:
#participant's_heights=vizinput.input('Input height of the participant sitting from floor to head.\n ')
#how many participants in the 20 trails? 
# 

#The depth of the targets. 
z_depth1= .23

#The manipulation used for finding the distance between targets. 
x_translate1= distance_between_targets1
#x_translate2= distance_between_targets1
#x_translate3= distance_between_targets1

#this is the manipulation for finding the distance of the end sensor and block. 
x_translate_shifted1=x_translate1+max(control_array)+.25
#NEW SHIFT!
#z_depth_translate= z_depth1-max(control_array)
#x_translate_shifted2=x_translate1+1.5
#x_translate_shifted3=x_translate1+1.5


height1= 1
#height2= .025
#height3=.025

#tracking data
import hand

    
    
    
viztracker.go()
#
#
composite = viztracker.getManager().getCompositeList()[0]
headTracker = composite.getRawTracker(composite.HEAD)
#handTracker = composite.getRawTracker(composite.RHAND)
handTracker = viztracker.main_sphere
#stupidhand = viztracker.get('righthand') 
#stupidhand.setScale(.01,.01,.01)
viewpoint = viztracker.get('viewpoint')
movable = viztracker.get("movable")
print('viewpoint')
#main_sphere=vizshape.addSphere(radius=.005,slices=20,stacks=20)
def printData():
	global main_sphere
	pass
	
#	main_sphere.setPosition(x)
#	print 'Tracker position',headTracker.getPosition()
#	print 'Tracker euler',headTracker.getEuler()
#	print 'Hand Tracker position',handTracker.getPosition() #just added this
#	print 'Hand Tracker euler',handTracker.getEuler() #and this
#	print 'Viewpoint position',viewpoint.getPosition()
#	print 'Movable position',movable.getPosition(),'\n'
vizact.ontimer(.005, printData)
# Setup tracking if this is the main script
if __name__ == "__main__":
	import viztracker
	viztracker.DEFAULT_HANDS = True
	viztracker.go()

#main_sphere=vizshape.addSphere(radius=1.0,slices=20,stacks=20)

#def move_sphere():
#	handTracker.getPosition(=
#	main_sphere.setPosition(x,y,z)


	

#Add a world axis with X,Y,Z labels
#world_axes = vizshape.addAxes()
#X = viz.addText3D('X',pos=[1.1,0,0],color=viz.RED,scale=[0.3,0.3,0.3],parent=world_axes)
#Y = viz.addText3D('Y',pos=[0,1.1,0],color=viz.GREEN,scale=[0.3,0.3,0.3],align=viz.ALIGN_CENTER_BASE,parent=world_axes)
#Z = viz.addText3D('Z',pos=[0,0,1.1],color=viz.BLUE,scale=[0.3,0.3,0.3],align=viz.ALIGN_CENTER_BASE,parent=world_axes)
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
end_box=(vizshape.addBox([.06,.06,.06],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color=viz.PURPLE))
left_node1=vizshape.addCylinder(height1, radius= .000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)        
#left_node2=vizshape.addCylinder(height1, radius= .000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)        
#left_node3=vizshape.addCylinder(height1, radius= .000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)        


right_node1=vizshape.addCylinder(height1, radius=.00000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
#right_node2=vizshape.addCylinder(height1, radius=.00000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
#right_node3=vizshape.addCylinder(height1, radius=.00000001,topRadius= None,bottomRadius= None, axis=vizshape.AXIS_Y,slices=20,bottom=True,top=True)
#CHANGE: changed start_box's dimensions to max_size from .06 did the same w/ the start_sensor
table= vizshape.addBox([50,.775,50],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.PURPLE)
start_node= vizshape.addBox([.00001, .000001, .0000001],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color=viz.BLUE)
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
if x>12:
	left_plane13= vizshape.addBox([control_array[12],.00001,control_array[12]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane13.setPosition(-x_translate1+550,y_height1,z_depth1)
	right_plane13= vizshape.addBox([control_array[12],.00001,control_array[12]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane13.setPosition(x_translate1+550,y_height1,z_depth1)
if x>13:
	left_plane14= vizshape.addBox([control_array[13],.00001,control_array[13]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane14.setPosition(-x_translate1+600,y_height1,z_depth1)
	right_plane14= vizshape.addBox([control_array[13],.00001,control_array[13]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane14.setPosition(x_translate1+600,y_height1,z_depth1)
if x>14:
	left_plane15= vizshape.addBox([control_array[14],.00001,control_array[14]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane15.setPosition(-x_translate1+650,y_height1,z_depth1)
	right_plane15= vizshape.addBox([control_array[14],.00001,control_array[14]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane15.setPosition(x_translate1+650,y_height1,z_depth1)
if x>15:
	left_plane16= vizshape.addBox([control_array[15],.00001,control_array[15]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane16.setPosition(-x_translate1+700,y_height1,z_depth1)
	right_plane16= vizshape.addBox([control_array[15],.00001,control_array[15]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane16.setPosition(x_translate1+700,y_height1,z_depth1)
if x>16:
	left_plane17= vizshape.addBox([control_array[16],.00001,control_array[16]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane17.setPosition(-x_translate1+750,y_height1,z_depth1)
	right_plane17= vizshape.addBox([control_array[16],.00001,control_array[16]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane17.setPosition(x_translate1+750,y_height1,z_depth1)
if x>17:
	left_plane18= vizshape.addBox([control_array[17],.00001,control_array[17]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane18.setPosition(-x_translate1+800,y_height1,z_depth1)
	right_plane18= vizshape.addBox([control_array[17],.00001,control_array[17]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane18.setPosition(x_translate1+800,y_height1,z_depth1)
if x>18:
	left_plane19= vizshape.addBox([control_array[18],.00001,control_array[18]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane19.setPosition(-x_translate1+850,y_height1,z_depth1)
	right_plane19= vizshape.addBox([control_array[18],.00001,control_array[18]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane19.setPosition(x_translate1+850,y_height1,z_depth1)
if x>19:
	left_plane20= vizshape.addBox([control_array[19],.00001,control_array[19]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.RED)
	left_plane20.setPosition(-x_translate1+900,y_height1,z_depth1)
	right_plane20= vizshape.addBox([control_array[19],.00001,control_array[19]],right=True,left=True,top=True,bottom=True, front=True,back=True, splitFaces=False, color= viz.GREEN)
	right_plane20.setPosition(x_translate1+900,y_height1,z_depth1)





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
error_dim=x_translate1*2-.1
3
if x>0:
	times_entered_left_plane_error1=0
	times_entered_right_plane_error1=0
	left_plane_sensor_error1=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error1)
	
	def EnterProximity_left_plane_sensor_error1(left_plane_sensor_error1):
		print('Entered left_plane_error1')
	def ExitProximity_left_plane_sensor_error1(left_plane_sensor_error1):
		global times_entered_left_plane_error1
		times_entered_left_plane_error1+=1
		print('Times entered left plane error1: ', times_entered_left_plane_error1)
	manager.onEnter(left_plane_sensor_error1,EnterProximity_left_plane_sensor_error1)
	manager.onExit(left_plane_sensor_error1,ExitProximity_left_plane_sensor_error1)
	
	right_plane_sensor_error1=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error1)
	def EnterProximity_right_plane_sensor_error1(right_plane_sensor_error1):
		print('Entered right_plane_error1')
	def ExitProximity_right_plane_sensor_error1(right_plane_sensor_error1):
		global times_entered_right_plane_error1
		times_entered_right_plane_error1+=1
		print('Times entered right plane error1: ', times_entered_right_plane_error1)
	manager.onEnter(right_plane_sensor_error1,EnterProximity_right_plane_sensor_error1)
	manager.onExit(right_plane_sensor_error1,ExitProximity_right_plane_sensor_error1)
		
	left_plane_sensor1= vizproximity.Sensor(vizproximity.Box([control_array[0],5,control_array[0]],[-x_translate1,y_height1-2.49,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor1)
	def EnterProximity_left_plane_sensor1(left_plane_sensor1):
		viz.playSound('boing!.wav')
		print('Entered left_plane_sensor1')
		

	def ExitProximity_left_plane_sensor1(left_plane_sensor1):
		print('Exited left_plane_sensor1')
		global times_entered_left_plane
		times_entered_left_plane+=1
		print('Times entered left plane: ', times_entered_left_plane)
	manager.onEnter(left_plane_sensor1,EnterProximity_left_plane_sensor1)
	manager.onExit(left_plane_sensor1,ExitProximity_left_plane_sensor1)
	

	right_plane_sensor1= vizproximity.Sensor(vizproximity.Box([control_array[0],5,control_array[0]],[x_translate1,y_height1-2.49,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor1)
	
	def EnterProximity_right_plane_sensor1(right_plane_sensor1):
		viz.playSound('boing!.wav')
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
	left_plane_sensor_error2=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+50,y_height1,z_depth1]),left_node1)
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
	left_plane_sensor2= vizproximity.Sensor(vizproximity.Box([control_array[1],5,control_array[1]],[-x_translate1+50,y_height1-2.49,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor2)
	def EnterProximity_left_plane_sensor2(left_plane_sensor2):
		print('Entered left_plane_sensor2')
		viz.playSound('boing!.wav')
	
	


	def ExitProximity_left_plane_sensor2(left_plane_sensor2):
		print('Exited left_plane_sensor2')
		global times_entered_left_plane2
		times_entered_left_plane2+=1
		print('Times entered left plane2', times_entered_left_plane2)
	manager.onEnter(left_plane_sensor2,EnterProximity_left_plane_sensor2)
	manager.onExit(left_plane_sensor2,ExitProximity_left_plane_sensor2)
	
	right_plane_sensor_error2=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+50,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error2)
	def EnterProximity_right_plane_sensor_error2(right_plane_sensor_error2):
		print('Entered right_plane_error2')
	def ExitProximity_right_plane_sensor_error2(right_plane_sensor_error2):
		global times_entered_right_plane_error2
		times_entered_right_plane_error2+=1
		print('Times entered right plane error2: ', times_entered_right_plane_error2)
	manager.onEnter(right_plane_sensor_error2,EnterProximity_right_plane_sensor_error2)
	manager.onExit(right_plane_sensor_error2,ExitProximity_right_plane_sensor_error2)
	
	right_plane_sensor2= vizproximity.Sensor(vizproximity.Box([control_array[1],5,control_array[1]],[x_translate1+50,y_height1-2.49,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor2)
	def EnterProximity_right_plane_sensor2(right_plane_sensor2):
		print('Entered right_plane2')
		viz.playSound('boing!.wav')

	

	def ExitProximity_right_plane_sensor2(right_plane_sensor2):
		print('Exited right_plane_sensor2')
		global times_entered_right_plane2
		times_entered_right_plane2+=1
		print('Times Entered right Plane2: ', times_entered_right_plane2)
	manager.onEnter(right_plane_sensor2,EnterProximity_right_plane_sensor2)
	manager.onExit(right_plane_sensor2,ExitProximity_right_plane_sensor2)
	
if x>2:
	times_entered_left_plane_error3=0
	times_entered_right_plane_error3=0
	left_plane_sensor_error3=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+100,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error3)
	
	def EnterProximity_left_plane_sensor_error3(left_plane_sensor_error3):
		print('Entered left_plane_error3')
	def ExitProximity_left_plane_sensor_error3(left_plane_sensor_error3):
		global times_entered_left_plane_error3
		times_entered_left_plane_error3+=1
		print('Times entered left plane error3: ', times_entered_left_plane_error3)
	manager.onEnter(left_plane_sensor_error3,EnterProximity_left_plane_sensor_error3)
	manager.onExit(left_plane_sensor_error3,ExitProximity_left_plane_sensor_error3)
	
	right_plane_sensor_error3=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+100,y_height1,z_depth1]),right_node1)
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
	left_plane_sensor3= vizproximity.Sensor(vizproximity.Box([control_array[2],5,control_array[2]],[-x_translate1+100,y_height1-2.49,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor3)
	def EnterProximity_left_plane_sensor3(left_plane_sensor3):
		print('Entered left_plane_sensor3')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor3(left_plane_sensor2):
		print('Exited left_plane_sensor3')
		global times_entered_left_plane3
		times_entered_left_plane3+=1
		print('Times entered left plane3', times_entered_left_plane3)
	manager.onEnter(left_plane_sensor3,EnterProximity_left_plane_sensor3)
	manager.onExit(left_plane_sensor3,ExitProximity_left_plane_sensor3)
	right_plane_sensor3= vizproximity.Sensor(vizproximity.Box([control_array[2],5,control_array[2]],[x_translate1+100,y_height1-2.49,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor3)
	def EnterProximity_right_plane_sensor3(right_plane_sensor3):
		print('Entered right_plane3')
		viz.playSound('boing!.wav')
	

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
	left_plane_sensor_error4=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+150,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error4)
	
	def EnterProximity_left_plane_sensor_error4(left_plane_sensor_error4):
		print('Entered left_plane_error4')
	def ExitProximity_left_plane_sensor_error4(left_plane_sesnor_error4):
		global times_entered_left_plane_error4
		times_entered_left_plane_error4+=1
		print('Times entered left plane error4: ', times_entered_left_plane_error4)
	manager.onEnter(left_plane_sensor_error4,EnterProximity_left_plane_sensor_error4)
	manager.onExit(left_plane_sensor_error4,ExitProximity_left_plane_sensor_error4)
	
	right_plane_sensor_error4=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+150,y_height1,z_depth1]),right_node1)
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
	left_plane_sensor4= vizproximity.Sensor(vizproximity.Box([control_array[3],5,control_array[3]],[-x_translate1+150,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor4)
	def EnterProximity_left_plane_sensor4(left_plane_sensor4):
		print('Entered left_plane_sensor4')
		viz.playSound('boing!.wav')
	
	


	def ExitProximity_left_plane_sensor4(left_plane_sensor4):
		print('Exited left_plane_sensor4')
		global times_entered_left_plane4
		times_entered_left_plane4+=1
		print('Times entered left plane4', times_entered_left_plane4)
	manager.onEnter(left_plane_sensor4,EnterProximity_left_plane_sensor4)
	manager.onExit(left_plane_sensor4,ExitProximity_left_plane_sensor4)
	
	right_plane_sensor4= vizproximity.Sensor(vizproximity.Box([control_array[3],5,control_array[3]],[x_translate1+150,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor4)
	def EnterProximity_right_plane_sensor4(right_plane_sensor4):
		print('Entered right_plane4')
		viz.playSound('boing!.wav')
	

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
	left_plane_sensor_error5=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+200,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error5)
	
	def EnterProximity_left_plane_sensor_error5(left_plane_sensor_error5):
		print('Entered left_plane_error5')
	def ExitProximity_left_plane_sensor_error5(left_plane_sensor_error5):
		global times_entered_left_plane_error5
		times_entered_left_plane_error5+=1
		print('Times entered left plane error5: ', times_entered_left_plane_error5)
	manager.onEnter(left_plane_sensor_error5,EnterProximity_left_plane_sensor_error5)
	manager.onExit(left_plane_sensor_error5,ExitProximity_left_plane_sensor_error5)
	
	right_plane_sensor_error5=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+200,y_height1,z_depth1]),right_node1)
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
	left_plane_sensor5= vizproximity.Sensor(vizproximity.Box([control_array[4],5,control_array[4]],[-x_translate1+200,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor5)
	def EnterProximity_left_plane_sensor5(left_plane_sensor5):
		print('Entered left_plane_sensor5')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor5(left_plane_sensor5):
		print('Exited left_plane_sensor5')
		global times_entered_left_plane5
		times_entered_left_plane5+=1
		print('Times entered left plane5', times_entered_left_plane5)
	manager.onEnter(left_plane_sensor5,EnterProximity_left_plane_sensor4)
	manager.onExit(left_plane_sensor5,ExitProximity_left_plane_sensor5)
	
	right_plane_sensor5= vizproximity.Sensor(vizproximity.Box([control_array[4],.02,control_array[4]],[x_translate1+200,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor5)
	def EnterProximity_right_plane_sensor5(right_plane_sensor5):
		print('Entered right_plane5')
		viz.playSound('boing!.wav')
	

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
	left_plane_sensor_error6=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+250,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error6)
	
	def EnterProximity_left_plane_sensor_error6(left_plane_sensor_error6):
		print('Entered left_plane_error6')
	def ExitProximity_left_plane_sensor_error6(left_plane_sensor_error6):
		global times_entered_left_plane_error6
		times_entered_left_plane_error6+=1
		print('Times entered left plane error6: ', times_entered_left_plane_error6)
	manager.onEnter(left_plane_sensor_error6,EnterProximity_left_plane_sensor_error6)
	manager.onExit(left_plane_sensor_error6,ExitProximity_left_plane_sensor_error6)
	
	right_plane_sensor_error6=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+250,y_height1,z_depth1]),right_node1)
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
	left_plane_sensor6= vizproximity.Sensor(vizproximity.Box([control_array[5],5,control_array[5]],[-x_translate1+250,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor6)
	def EnterProximity_left_plane_sensor6(left_plane_sensor6):
		print('Entered left_plane_sensor6')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor6(left_plane_sensor6):
		print('Exited left_plane_sensor6')
		global times_entered_left_plane6
		times_entered_left_plane6+=1
		print('Times entered left plane6', times_entered_left_plane6)
	manager.onEnter(left_plane_sensor6,EnterProximity_left_plane_sensor6)
	manager.onExit(left_plane_sensor6,ExitProximity_left_plane_sensor6)
	
	right_plane_sensor6= vizproximity.Sensor(vizproximity.Box([control_array[5],5,control_array[5]],[x_translate1+250,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor6)
	def EnterProximity_right_plane_sensor6(right_plane_sensor6):
		print('Entered right_plane6')
		viz.playSound('boing!.wav')

	

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
	left_plane_sensor_error7=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+300,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error7)
	
	def EnterProximity_left_plane_sensor_error7(left_plane_sensor_error7):
		print('Entered left_plane_error7')
	def ExitProximity_left_plane_sensor_error7(left_plane_sensor_error7):
		global times_entered_left_plane_error7
		times_entered_left_plane_error7+=1
		print('Times entered left plane error7: ', times_entered_left_plane_error7)
	manager.onEnter(left_plane_sensor_error7,EnterProximity_left_plane_sensor_error7)
	manager.onExit(left_plane_sensor_error7,ExitProximity_left_plane_sensor_error7)
	
	right_plane_sensor_error7=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+300,y_height1,z_depth1]),right_node1)
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
	left_plane_sensor6= vizproximity.Sensor(vizproximity.Box([control_array[5],5,control_array[5]],[-x_translate1+250,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor6)
	def EnterProximity_left_plane_sensor6(left_plane_sensor6):
		print('Entered left_plane_sensor6')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor6(left_plane_sensor6):
		print('Exited left_plane_sensor6')
		global times_entered_left_plane6
		times_entered_left_plane6+=1
		print('Times entered left plane6', times_entered_left_plane6)
	manager.onEnter(left_plane_sensor6,EnterProximity_left_plane_sensor6)
	manager.onExit(left_plane_sensor6,ExitProximity_left_plane_sensor6)
	times_entered_left_plane7=0
	times_entered_right_plane7=0
	left_plane_sensor7= vizproximity.Sensor(vizproximity.Box([control_array[6],5,control_array[6]],[-x_translate1+300,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor7)
	def EnterProximity_left_plane_sensor7(left_plane_sensor7):
		print('Entered left_plane_sensor7')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor7(left_plane_sensor7):
		print('Exited left_plane_sensor7')
		global times_entered_left_plane7
		times_entered_left_plane7+=1
		print('Times entered left plane7', times_entered_left_plane7)
	manager.onEnter(left_plane_sensor7,EnterProximity_left_plane_sensor7)
	manager.onExit(left_plane_sensor7,ExitProximity_left_plane_sensor7)
	
	right_plane_sensor7= vizproximity.Sensor(vizproximity.Box([control_array[6],5,control_array[6]],[x_translate1+300,y_height1-2.9,z_depth1]),right_node1)
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
	left_plane_sensor_error8=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+350,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error8)
	
	def EnterProximity_left_plane_sensor_error8(left_plane_sensor_error8):
		print('Entered left_plane_error8')
	def ExitProximity_left_plane_sensor_error8(left_plane_sensor_error8):
		global times_entered_left_plane_error8
		times_entered_left_plane_error8+=1
		print('Times entered left plane error8: ', times_entered_left_plane_error8)
	manager.onEnter(left_plane_sensor_error8,EnterProximity_left_plane_sensor_error8)
	manager.onExit(left_plane_sensor_error8,ExitProximity_left_plane_sensor_error8)
	
	right_plane_sensor_error8=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+350,y_height1,z_depth1]),right_node1)
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
	left_plane_sensor8= vizproximity.Sensor(vizproximity.Box([control_array[7],5,control_array[7]],[-x_translate1+350,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor8)
	def EnterProximity_left_plane_sensor8(left_plane_sensor8):
		print('Entered left_plane_sensor8')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor8(left_plane_sensor8):
		print('Exited left_plane_sensor8')
		global times_entered_left_plane8
		times_entered_left_plane8+=1
		print('Times entered left plane8', times_entered_left_plane8)
	manager.onEnter(left_plane_sensor8,EnterProximity_left_plane_sensor8)
	manager.onExit(left_plane_sensor8,ExitProximity_left_plane_sensor8)
	
	right_plane_sensor8= vizproximity.Sensor(vizproximity.Box([control_array[7],5,control_array[7]],[x_translate1+350,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor8)
	def EnterProximity_right_plane_sensor8(right_plane_sensor8):
		print('Entered right_plane8')
		viz.playSound('boing!.wav')

	

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
	left_plane_sensor_error9=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+400,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error9)
	
	def EnterProximity_left_plane_sensor_error9(left_plane_sensor_error9):
		print('Entered left_plane_error9')
	def ExitProximity_left_plane_sensor_error9(left_plane_sensor_error9):
		global times_entered_left_plane_error9
		times_entered_left_plane_error9+=1
		print('Times entered left plane error9: ', times_entered_left_plane_error9)
	manager.onEnter(left_plane_sensor_error9,EnterProximity_left_plane_sensor_error9)
	manager.onExit(left_plane_sensor_error9,ExitProximity_left_plane_sensor_error9)
	
	right_plane_sensor_error9=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+400,y_height1,z_depth1]),right_node1)
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
	left_plane_sensor9= vizproximity.Sensor(vizproximity.Box([control_array[8],5,control_array[8]],[-x_translate1+400,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor9)
	def EnterProximity_left_plane_sensor9(left_plane_sensor9):
		print('Entered left_plane_sensor9')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor9(left_plane_sensor9):
		print('Exited left_plane_sensor9')
		global times_entered_left_plane9
		times_entered_left_plane9+=1
		print('Times entered left plane9', times_entered_left_plane9)
	manager.onEnter(left_plane_sensor9,EnterProximity_left_plane_sensor9)
	manager.onExit(left_plane_sensor9,ExitProximity_left_plane_sensor9)
	
	right_plane_sensor9= vizproximity.Sensor(vizproximity.Box([control_array[8],5,control_array[8]],[x_translate1+400,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor9)
	def EnterProximity_right_plane_sensor9(right_plane_sensor9):
		print('Entered right_plane9')
		viz.playSound('boing!.wav')

	

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
	left_plane_sensor_error10=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+450,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error10)
	
	def EnterProximity_left_plane_sensor_error10(left_plane_sensor_error10):
		print('Entered left_plane_error10')
	def ExitProximity_left_plane_sensor_error10(left_plane_sensor_error10):
		global times_entered_left_plane_error10
		times_entered_left_plane_error10+=1
		print('Times entered left plane error10: ', times_entered_left_plane_error10)
	manager.onEnter(left_plane_sensor_error10,EnterProximity_left_plane_sensor_error10)
	manager.onExit(left_plane_sensor_error10,ExitProximity_left_plane_sensor_error10)
	
	right_plane_sensor_error10=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+450,y_height1,z_depth1]),right_node1)
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
	left_plane_sensor10= vizproximity.Sensor(vizproximity.Box([control_array[9],5,control_array[9]],[-x_translate1+450,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor10)
	def EnterProximity_left_plane_sensor10(left_plane_sensor10):
		print('Entered left_plane_sensor10')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor10(left_plane_sensor10):
		print('Exited left_plane_sensor10')
		global times_entered_left_plane10
		times_entered_left_plane10+=1
		print('Times entered left plane10', times_entered_left_plane10)
	manager.onEnter(left_plane_sensor10,EnterProximity_left_plane_sensor10)
	manager.onExit(left_plane_sensor10,ExitProximity_left_plane_sensor10)
	
	right_plane_sensor10= vizproximity.Sensor(vizproximity.Box([control_array[9],5,control_array[9]],[x_translate1+450,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor10)
	def EnterProximity_right_plane_sensor10(right_plane_sensor10):
		print ('Entered right_plane10')
		viz.playSound('boing!.wav')

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
	left_plane_sensor_error11=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+500,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error11)
	
	def EnterProximity_left_plane_sensor_error11(left_plane_sensor_error11):
		print('Entered left_plane_error11')
	def ExitProximity_left_plane_sensor_error11(left_plane_sensor_error11):
		global times_entered_left_plane_error11
		times_entered_left_plane_error11+=1
		print('Times entered left plane error11: ', times_entered_left_plane_error11)
	manager.onEnter(left_plane_sensor_error11,EnterProximity_left_plane_sensor_error11)
	manager.onExit(left_plane_sensor_error11,ExitProximity_left_plane_sensor_error11)
	
	right_plane_sensor_error11=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+500,y_height1,z_depth1]),right_node1)
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
	left_plane_sensor11= vizproximity.Sensor(vizproximity.Box([control_array[10],5,control_array[10]],[-x_translate1+500,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor11)
	def EnterProximity_left_plane_sensor11(left_plane_sensor11):
		print('Entered left_plane_sensor11')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor11(left_plane_sensor11):
		print('Exited left_plane_sensor11')
		global times_entered_left_plane11
		times_entered_left_plane11+=1
		print('Times entered left plane11', times_entered_left_plane11)
	manager.onEnter(left_plane_sensor11,EnterProximity_left_plane_sensor11)
	manager.onExit(left_plane_sensor11,ExitProximity_left_plane_sensor11)
	
	right_plane_sensor11= vizproximity.Sensor(vizproximity.Box([control_array[10],5,control_array[10]],[x_translate1+500,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor11)
	def EnterProximity_right_plane_sensor11(right_plane_sensor11):
		print('Entered right_plane11')
		viz.playSound('boing!.wav')
	

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
	left_plane_sensor_error12=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+550,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error12)
	
	def EnterProximity_left_plane_sensor_error12(left_plane_sensor_error12):
		print('Entered left_plane_error12')
	def ExitProximity_left_plane_sensor_error12(left_plane_sensor_error12):
		global times_entered_left_plane_error12
		times_entered_left_plane_error12+=1
		print('Times entered left plane error12: ', times_entered_left_plane_error12)
	manager.onEnter(left_plane_sensor_error12,EnterProximity_left_plane_sensor_error12)
	manager.onExit(left_plane_sensor_error12,ExitProximity_left_plane_sensor_error12)
	
	right_plane_sensor_error12=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+550,y_height1,z_depth1]),right_node1)
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
	left_plane_sensor12= vizproximity.Sensor(vizproximity.Box([control_array[11],5,control_array[11]],[-x_translate1+550,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor12)
	def EnterProximity_left_plane_sensor12(left_plane_sensor12):
		print('Entered left_plane_sensor12')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor12(left_plane_sensor12):
		print('Exited left_plane_sensor12')
		global times_entered_left_plane12
		times_entered_left_plane12+=1
		print('Times entered left plane12', times_entered_left_plane12)
	manager.onEnter(left_plane_sensor12,EnterProximity_left_plane_sensor12)
	manager.onExit(left_plane_sensor12,ExitProximity_left_plane_sensor12)
	
	right_plane_sensor12= vizproximity.Sensor(vizproximity.Box([control_array[11],5,control_array[11]],[x_translate1+550,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor12)
	def EnterProximity_right_plane_sensor12(right_plane_sensor12):
		print('Entered right_plane1')
		viz.playSound('boing!.wav')

	def ExitProximity_right_plane_sensor12(right_plane_sensor12):
		print('Exited right_plane_sensor12')
		global times_entered_right_plane12
		times_entered_right_plane12+=1
		print('Times Entered right Plane12: ', times_entered_right_plane12)
	manager.onEnter(right_plane_sensor12,EnterProximity_right_plane_sensor12)
	manager.onExit(right_plane_sensor12,ExitProximity_right_plane_sensor12)
if x>12:
	times_entered_left_plane_error13=0
	times_entered_right_plane_error13=0
	left_plane_sensor_error13=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+600,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error13)
	
	def EnterProximity_left_plane_sensor_error13(left_plane_sensor_error13):
		print('Entered left_plane_error13')
	def ExitProximity_left_plane_sensor_error13(left_plane_sensor_error13):
		global times_entered_left_plane_error13
		times_entered_left_plane_error13+=1
		print('Times entered left plane error13: ', times_entered_left_plane_error13)
	manager.onEnter(left_plane_sensor_error13,EnterProximity_left_plane_sensor_error13)
	manager.onExit(left_plane_sensor_error13,ExitProximity_left_plane_sensor_error13)
	
	right_plane_sensor_error13=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+600,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error13)
	def EnterProximity_right_plane_sensor_error13(right_plane_sensor_error13):
		print('Entered right_plane_error13')
	def ExitProximity_right_plane_sensor_error13(right_plane_sensor_error13):
		global times_entered_right_plane_error13
		times_entered_right_plane_error13+=1
		print('Times entered right plane error13: ', times_entered_right_plane_error13)
	manager.onEnter(right_plane_sensor_error13,EnterProximity_right_plane_sensor_error13)
	manager.onExit(right_plane_sensor_error13,ExitProximity_right_plane_sensor_error13)	
	times_entered_left_plane13=0
	times_entered_right_plane13=0
	
	left_plane_sensor13= vizproximity.Sensor(vizproximity.Box([control_array[12],5,control_array[12]],[-x_translate1+600,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor13)
	def EnterProximity_left_plane_sensor13(left_plane_sensor13):
		print('Entered left_plane_sensor13')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor13(left_plane_sensor13):
		print('Exited left_plane_sensor13')
		global times_entered_left_plane13
		times_entered_left_plane13+=1
		print('Times entered left plane13', times_entered_left_plane13)
	manager.onEnter(left_plane_sensor13,EnterProximity_left_plane_sensor13)
	manager.onExit(left_plane_sensor13,ExitProximity_left_plane_sensor13)
	
	right_plane_sensor13= vizproximity.Sensor(vizproximity.Box([control_array[12],5,control_array[12]],[x_translate1+600,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor13)
	def EnterProximity_right_plane_sensor13(right_plane_sensor13):
		print('Entered right_plane13')
		viz.playSound('boing!.wav')

	def ExitProximity_right_plane_sensor13(right_plane_sensor13):
		print('Exited right_plane_sensor13')
		global times_entered_right_plane13
		times_entered_right_plane13+=1
		print('Times Entered right Plane13: ', times_entered_right_plane13)
	manager.onEnter(right_plane_sensor13,EnterProximity_right_plane_sensor13)
	manager.onExit(right_plane_sensor13,ExitProximity_right_plane_sensor13)
if x>13:
	times_entered_left_plane_error14=0
	times_entered_right_plane_error14=0
	
	left_plane_sensor_error14=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+650,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error14)
	
	def EnterProximity_left_plane_sensor_error14(left_plane_sensor_error14):
		print('Entered left_plane_error14')
	def ExitProximity_left_plane_sensor_error14(left_plane_sensor_error14):
		global times_entered_left_plane_error14
		times_entered_left_plane_error14+=1
		print('Times entered left plane error14: ', times_entered_left_plane_error14)
	manager.onEnter(left_plane_sensor_error14,EnterProximity_left_plane_sensor_error14)
	manager.onExit(left_plane_sensor_error14,ExitProximity_left_plane_sensor_error14)
	
	right_plane_sensor_error14=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+650,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error14)
	def EnterProximity_right_plane_sensor_error14(right_plane_sensor_error14):
		print('Entered right_plane_error14')
	def ExitProximity_right_plane_sensor_error13(right_plane_sensor_error14):
		global times_entered_right_plane_error14
		times_entered_right_plane_error14+=1
		print('Times entered right plane error14: ', times_entered_right_plane_error14)
	manager.onEnter(right_plane_sensor_error14,EnterProximity_right_plane_sensor_error14)
	manager.onExit(right_plane_sensor_error14,ExitProximity_right_plane_sensor_error14)	
	times_entered_left_plane14=0
	times_entered_right_plane14=0
	
	left_plane_sensor14= vizproximity.Sensor(vizproximity.Box([control_array[13],5,control_array[13]],[-x_translate1+650,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor14)
	def EnterProximity_left_plane_sensor14(left_plane_sensor14):
		print('Entered left_plane_sensor14')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor14(left_plane_sensor14):
		print('Exited left_plane_sensor14')
		global times_entered_left_plane14
		times_entered_left_plane14+=1
		print('Times entered left plane14', times_entered_left_plane14)
	manager.onEnter(left_plane_sensor14,EnterProximity_left_plane_sensor14)
	manager.onExit(left_plane_sensor14,ExitProximity_left_plane_sensor14)
	
	right_plane_sensor14= vizproximity.Sensor(vizproximity.Box([control_array[13],5,control_array[13]],[x_translate1+650,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor14)
	def EnterProximity_right_plane_sensor14(right_plane_sensor14):
		print('Entered right_plane14')
		viz.playSound('boing!.wav')

	def ExitProximity_right_plane_sensor14(right_plane_sensor14):
		print('Exited right_plane_sensor14')
		global times_entered_right_plane14
		times_entered_right_plane14+=1
		print('Times Entered right Plane14: ', times_entered_right_plane14)
	manager.onEnter(right_plane_sensor14,EnterProximity_right_plane_sensor14)
	manager.onExit(right_plane_sensor14,ExitProximity_right_plane_sensor14)
if x>14:
	times_entered_left_plane_error15=0
	times_entered_right_plane_error15=0
	
	left_plane_sensor_error15=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+700,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error15)
	
	def EnterProximity_left_plane_sensor_error15(left_plane_sensor_error15):
		print('Entered left_plane_error15')
	def ExitProximity_left_plane_sensor_error15(left_plane_sensor_error15):
		global times_entered_left_plane_error15
		times_entered_left_plane_error15+=1
		print('Times entered left plane error15: ', times_entered_left_plane_error15)
	manager.onEnter(left_plane_sensor_error15,EnterProximity_left_plane_sensor_error15)
	manager.onExit(left_plane_sensor_error15,ExitProximity_left_plane_sensor_error15)
	
	right_plane_sensor_error15=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+700,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error15)
	def EnterProximity_right_plane_sensor_error15(right_plane_sensor_error15):
		print('Entered right_plane_error15')
	def ExitProximity_right_plane_sensor_error15(right_plane_sensor_error15):
		global times_entered_right_plane_error15
		times_entered_right_plane_error15+=1
		print('Times entered right plane error15: ', times_entered_right_plane_error15)
	manager.onEnter(right_plane_sensor_error15,EnterProximity_right_plane_sensor_error15)
	manager.onExit(right_plane_sensor_error15,ExitProximity_right_plane_sensor_error15)	
	times_entered_left_plane15=0
	times_entered_right_plane15=0
	
	left_plane_sensor15= vizproximity.Sensor(vizproximity.Box([control_array[14],5,control_array[14]],[-x_translate1+700,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor15)
	def EnterProximity_left_plane_sensor15(left_plane_sensor15):
		print('Entered left_plane_sensor15')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor15(left_plane_sensor15):
		print('Exited left_plane_sensor15')
		global times_entered_left_plane15
		times_entered_left_plane15+=1
		print('Times entered left plane15', times_entered_left_plane15)
	manager.onEnter(left_plane_sensor15,EnterProximity_left_plane_sensor15)
	manager.onExit(left_plane_sensor15,ExitProximity_left_plane_sensor15)
	
	right_plane_sensor15= vizproximity.Sensor(vizproximity.Box([control_array[14],5,control_array[14]],[x_translate1+700,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor15)
	def EnterProximity_right_plane_sensor15(right_plane_sensor15):
		print('Entered right_plane15')
		viz.playSound('boing!.wav')

	def ExitProximity_right_plane_sensor15(right_plane_sensor15):
		print('Exited right_plane_sensor15')
		global times_entered_right_plane15
		times_entered_right_plane15+=1
		print('Times Entered right Plane15: ', times_entered_right_plane15)
	manager.onEnter(right_plane_sensor15,EnterProximity_right_plane_sensor15)
	manager.onExit(right_plane_sensor15,ExitProximity_right_plane_sensor15)
if x>15:
	times_entered_left_plane_error16
	times_entered_right_plane_error16
	 
	left_plane_sensor_error16=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+750,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error16)
	
	def EnterProximity_left_plane_sensor_error16(left_plane_sensor_error16):
		print('Entered left_plane_error16')
	def ExitProximity_left_plane_sensor_error16(left_plane_sensor_error16):
		global times_entered_left_plane_error16
		times_entered_left_plane_error16+=1
		print('Times entered left plane error16: ', times_entered_left_plane_error16)
	manager.onEnter(left_plane_sensor_error16,EnterProximity_left_plane_sensor_error16)
	manager.onExit(left_plane_sensor_error16,ExitProximity_left_plane_sensor_error16)
	
	right_plane_sensor_error16=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+750,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error16)
	def EnterProximity_right_plane_sensor_error16(right_plane_sensor_error16):
		print('Entered right_plane_error16')
	def ExitProximity_right_plane_sensor_error16(right_plane_sensor_error16):
		global times_entered_right_plane_error16
		times_entered_right_plane_error16+=1
		print('Times entered right plane error16: ', times_entered_right_plane_error16)
	manager.onEnter(right_plane_sensor_error16,EnterProximity_right_plane_sensor_error16)
	manager.onExit(right_plane_sensor_error16,ExitProximity_right_plane_sensor_error16)	
	times_entered_left_plane16=0
	times_entered_right_plane16=0
	
	left_plane_sensor16= vizproximity.Sensor(vizproximity.Box([control_array[15],5,control_array[15]],[-x_translate1+750,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor16)
	def EnterProximity_left_plane_sensor16(left_plane_sensor16):
		print('Entered left_plane_sensor16')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor16(left_plane_sensor16):
		print('Exited left_plane_sensor16')
		global times_entered_left_plane16
		times_entered_left_plane16+=1
		print('Times entered left plane16', times_entered_left_plane16)
	manager.onEnter(left_plane_sensor16,EnterProximity_left_plane_sensor16)
	manager.onExit(left_plane_sensor16,ExitProximity_left_plane_sensor16)
	
	right_plane_sensor16= vizproximity.Sensor(vizproximity.Box([control_array[15],5,control_array[15]],[x_translate1+750,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor16)
	def EnterProximity_right_plane_sensor16(right_plane_sensor16):
		print('Entered right_plane16')
		viz.playSound('boing!.wav')

	def ExitProximity_right_plane_sensor16(right_plane_sensor16):
		print('Exited right_plane_sensor16')
		global times_entered_right_plane16
		times_entered_right_plane16+=1
		print('Times Entered right Plane16: ', times_entered_right_plane16)
	manager.onEnter(right_plane_sensor16,EnterProximity_right_plane_sensor16)
	manager.onExit(right_plane_sensor16,ExitProximity_right_plane_sensor16)
if x>16:
	times_entered_left_plane_error17
	times_entered_right_plane_error17
	 
	left_plane_sensor_error17=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+800,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error17)
	
	def EnterProximity_left_plane_sensor_error17(left_plane_sensor_error17):
		print('Entered left_plane_error17')
	def ExitProximity_left_plane_sensor_error17(left_plane_sensor_error17):
		global times_entered_left_plane_error17
		times_entered_left_plane_error17+=1
		print('Times entered left plane error17: ', times_entered_left_plane_error17)
	manager.onEnter(left_plane_sensor_error17,EnterProximity_left_plane_sensor_error17)
	manager.onExit(left_plane_sensor_error17,ExitProximity_left_plane_sensor_error17)
	
	right_plane_sensor_error17=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+800,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error17)
	def EnterProximity_right_plane_sensor_error17(right_plane_sensor_error17):
		print('Entered right_plane_error17')
	def ExitProximity_right_plane_sensor_error17(right_plane_sensor_error17):
		global times_entered_right_plane_error17
		times_entered_right_plane_error17+=1
		print('Times entered right plane error17: ', times_entered_right_plane_error17)
	manager.onEnter(right_plane_sensor_error17,EnterProximity_right_plane_sensor_error17)
	manager.onExit(right_plane_sensor_error17,ExitProximity_right_plane_sensor_error17)	
	times_entered_left_plane17=0
	times_entered_right_plane17=0
	
	left_plane_sensor17= vizproximity.Sensor(vizproximity.Box([control_array[16],5,control_array[16]],[-x_translate1+800,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor17)
	def EnterProximity_left_plane_sensor17(left_plane_sensor17):
		print('Entered left_plane_sensor17')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor17(left_plane_sensor17):
		print('Exited left_plane_sensor17')
		global times_entered_left_plane17
		times_entered_left_plane17+=1
		print('Times entered left plane17', times_entered_left_plane17)
	manager.onEnter(left_plane_sensor17,EnterProximity_left_plane_sensor17)
	manager.onExit(left_plane_sensor17,ExitProximity_left_plane_sensor17)
	
	right_plane_sensor17= vizproximity.Sensor(vizproximity.Box([control_array[16],5,control_array[16]],[x_translate1+800,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor17)
	def EnterProximity_right_plane_sensor17(right_plane_sensor17):
		print('Entered right_plane17')
		viz.playSound('boing!.wav')

	def ExitProximity_right_plane_sensor17(right_plane_sensor17):
		print('Exited right_plane_sensor17')
		global times_entered_right_plane17
		times_entered_right_plane17+=1
		print('Times Entered right Plane17: ', times_entered_right_plane17)
	manager.onEnter(right_plane_sensor17,EnterProximity_right_plane_sensor17)
	manager.onExit(right_plane_sensor17,ExitProximity_right_plane_sensor17)
if x>17:
	times_entered_left_plane_error18
	times_entered_right_plane_error18
	 
	left_plane_sensor_error18=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+850,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error18)
	
	def EnterProximity_left_plane_sensor_error18(left_plane_sensor_error18):
		print('Entered left_plane_error18')
	def ExitProximity_left_plane_sensor_error18(left_plane_sensor_error18):
		global times_entered_left_plane_error18
		times_entered_left_plane_error18+=1
		print('Times entered left plane error18: ', times_entered_left_plane_error18)
	manager.onEnter(left_plane_sensor_error18,EnterProximity_left_plane_sensor_error18)
	manager.onExit(left_plane_sensor_error18,ExitProximity_left_plane_sensor_error18)
	
	right_plane_sensor_error18=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+850,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error18)
	def EnterProximity_right_plane_sensor_error18(right_plane_sensor_error18):
		print('Entered right_plane_error18')
	def ExitProximity_right_plane_sensor_error18(right_plane_sensor_error18):
		global times_entered_right_plane_error18
		times_entered_right_plane_error18+=1
		print('Times entered right plane error18: ', times_entered_right_plane_error18)
	manager.onEnter(right_plane_sensor_error18,EnterProximity_right_plane_sensor_error18)
	manager.onExit(right_plane_sensor_error18,ExitProximity_right_plane_sensor_error18)	
	times_entered_left_plane18=0
	times_entered_right_plane18=0
	
	left_plane_sensor18= vizproximity.Sensor(vizproximity.Box([control_array[17],5,control_array[17]],[-x_translate1+850,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor18)
	def EnterProximity_left_plane_sensor18(left_plane_sensor18):
		print('Entered left_plane_sensor18')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor18(left_plane_sensor18):
		print('Exited left_plane_sensor18')
		global times_entered_left_plane18
		times_entered_left_plane18+=1
		print('Times entered left plane18', times_entered_left_plane18)
	manager.onEnter(left_plane_sensor18,EnterProximity_left_plane_sensor18)
	manager.onExit(left_plane_sensor18,ExitProximity_left_plane_sensor18)
	
	right_plane_sensor18= vizproximity.Sensor(vizproximity.Box([control_array[17],5,control_array[17]],[x_translate1+850,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor18)
	def EnterProximity_right_plane_sensor18(right_plane_sensor18):
		print('Entered right_plane18')
		viz.playSound('boing!.wav')

	def ExitProximity_right_plane_sensor18(right_plane_sensor18):
		print('Exited right_plane_sensor18')
		global times_entered_right_plane18
		times_entered_right_plane18+=1
		print('Times Entered right Plane18: ', times_entered_right_plane18)
	manager.onEnter(right_plane_sensor18,EnterProximity_right_plane_sensor18)
	manager.onExit(right_plane_sensor18,ExitProximity_right_plane_sensor18)
if x>18:
	times_entered_left_plane_error19
	times_entered_right_plane_error19
	 
	left_plane_sensor_error19=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+900,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error19)
	
	def EnterProximity_left_plane_sensor_error19(left_plane_sensor_error19):
		print('Entered left_plane_error19')
	def ExitProximity_left_plane_sensor_error19(left_plane_sensor_error19):
		global times_entered_left_plane_error19
		times_entered_left_plane_error19+=1
		print('Times entered left plane error19: ', times_entered_left_plane_error19)
	manager.onEnter(left_plane_sensor_error19,EnterProximity_left_plane_sensor_error19)
	manager.onExit(left_plane_sensor_error19,ExitProximity_left_plane_sensor_error19)
	
	right_plane_sensor_error19=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+900,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error19)
	def EnterProximity_right_plane_sensor_error19(right_plane_sensor_error19):
		print('Entered right_plane_error19')
	def ExitProximity_right_plane_sensor_error19(right_plane_sensor_error19):
		global times_entered_right_plane_error19
		times_entered_right_plane_error19+=1
		print('Times entered right plane error19: ', times_entered_right_plane_error19)
	manager.onEnter(right_plane_sensor_error19,EnterProximity_right_plane_sensor_error19)
	manager.onExit(right_plane_sensor_error19,ExitProximity_right_plane_sensor_error19)	
	times_entered_left_plane19=0
	times_entered_right_plane19=0
	
	left_plane_sensor19= vizproximity.Sensor(vizproximity.Box([control_array[18],5,control_array[18]],[-x_translate1+900,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor19)
	def EnterProximity_left_plane_sensor19(left_plane_sensor19):
		print('Entered left_plane_sensor19')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor19(left_plane_sensor19):
		print('Exited left_plane_sensor19')
		global times_entered_left_plane19
		times_entered_left_plane19+=1
		print('Times entered left plane19', times_entered_left_plane19)
	manager.onEnter(left_plane_sensor19,EnterProximity_left_plane_sensor19)
	manager.onExit(left_plane_sensor19,ExitProximity_left_plane_sensor19)
	
	right_plane_sensor19= vizproximity.Sensor(vizproximity.Box([control_array[18],5,control_array[18]],[x_translate1+900,y_height1-2.9,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor19)
	def EnterProximity_right_plane_sensor19(right_plane_sensor19):
		print('Entered right_plane19')
		viz.playSound('boing!.wav')

	def ExitProximity_right_plane_sensor19(right_plane_sensor19):
		print('Exited right_plane_sensor19')
		global times_entered_right_plane19
		times_entered_right_plane19+=1
		print('Times Entered right Plane19: ', times_entered_right_plane19)
	manager.onEnter(right_plane_sensor19,EnterProximity_right_plane_sensor19)
	manager.onExit(right_plane_sensor19,ExitProximity_right_plane_sensor19)
if x>19:
	times_entered_left_plane_error20
	times_entered_right_plane_error20
	 
	left_plane_sensor_error20=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[-x_translate1+950,y_height1,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor_error20)
	
	def EnterProximity_left_plane_sensor_error20(left_plane_sensor_error20):
		print('Entered left_plane_error20')
	def ExitProximity_left_plane_sensor_error20(left_plane_sensor_error20):
		global times_entered_left_plane_error20
		times_entered_left_plane_error20+=1
		print('Times entered left plane error20: ', times_entered_left_plane_error20)
	manager.onEnter(left_plane_sensor_error20,EnterProximity_left_plane_sensor_error20)
	manager.onExit(left_plane_sensor_error20,ExitProximity_left_plane_sensor_error20)
	
	right_plane_sensor_error20=vizproximity.Sensor(vizproximity.Box([error_dim,error_dim,error_dim],[x_translate1+950,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor_error20)
	def EnterProximity_right_plane_sensor_error20(right_plane_sensor_error20):
		print('Entered right_plane_error20')
	def ExitProximity_right_plane_sensor_error20(right_plane_sensor_error20):
		global times_entered_right_plane_error20
		times_entered_right_plane_error20+=1
		print('Times entered right plane error20: ', times_entered_right_plane_error20)
	manager.onEnter(right_plane_sensor_error20,EnterProximity_right_plane_sensor_error20)
	manager.onExit(right_plane_sensor_error20,ExitProximity_right_plane_sensor_error20)	
	times_entered_left_plane20=0
	times_entered_right_plane20=0
	
	left_plane_sensor20= vizproximity.Sensor(vizproximity.Box([control_array[19],5,control_array[19]],[-x_translate1+950,y_height1-2.9,z_depth1]),left_node1)
	manager.addSensor(left_plane_sensor20)
	def EnterProximity_left_plane_sensor20(left_plane_sensor20):
		print('Entered left_plane_sensor20')
		viz.playSound('boing!.wav')
	def ExitProximity_left_plane_sensor20(left_plane_sensor19):
		print('Exited left_plane_sensor20')
		global times_entered_left_plane20
		times_entered_left_plane20+=1
		print('Times entered left plane20', times_entered_left_plane20)
	manager.onEnter(left_plane_sensor20,EnterProximity_left_plane_sensor20)
	manager.onExit(left_plane_sensor20,ExitProximity_left_plane_sensor20)
	
	right_plane_sensor20= vizproximity.Sensor(vizproximity.Box([control_array[20],5,control_array[20]],[x_translate1+900,y_height1,z_depth1]),right_node1)
	manager.addSensor(right_plane_sensor20)
	def EnterProximity_right_plane_sensor20(right_plane_sensor20):
		print('Entered right_plane20')

	def ExitProximity_right_plane_sensor20(right_plane_sensor20):
		print('Exited right_plan3e_sensor20')
		global times_entered_right_plane20
		times_entered_right_plane20+=1
		print('Times Entered right Plane20: ', times_entered_right_plane20)
	manager.onEnter(right_plane_sensor20,EnterProximity_right_plane_sensor20)
	manager.onExit(right_plane_sensor20,ExitProximity_right_plane_sensor20)
#create sensors
#still need to make a set of left/right sensors/proximity functions for left_plane2/3 and right_plane 2/3
#left_plane_sensor1= vizproximity.Sensor(vizproximity.Box([scale_x1,.25,scale_x1],[-x_translate1,y_height1,z_depth1]),left_node1)
#manager.addSensor(left_plane_sensor1)
#right_plane_sensor1= vizproximity.Sensor(vizproximity.Box([scale_x1,.25,scale_x1],[x_translate1,y_height1,z_depth1]),right_node1)
#manager.addSensor(right_plane_sensor1)

mid_plane_sensor= vizproximity.Sensor(vizproximity.Box([.025,20,20],center=[0,0,0]),source = mid_plane)
manager.addSensor(mid_plane_sensor)        
     
start_sensor=vizproximity.Sensor(vizproximity.Box([maximum_size, maximum_size, maximum_size],center=[0,0,0]),start_node)
manager.addSensor(start_sensor)

end_sensor=vizproximity.Sensor(vizproximity.Box([.06,.06,.06],center= [x_translate_shifted1, y_height1,z_depth1]),end_node)
manager.addSensor(end_sensor)


    
def timer3():
	viz.playSound('boing!.wav')
	global reaction_timer_initial
	a=viz.tick()
	print('in timer!')
	global timer2
	reaction_timer_initial=viz.tick()
	
	
def EnterProximity_start_sensor(start_sensor):
	vizact.ontimer2(1,0, timer3)
	global times_entered_start_plane
	times_entered_start_plane =times_entered_start_plane+1
	print('Entered start_sensor',str(times_entered_start_plane))
	shift_all_planes(x)
	
	
	
	
	
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
#	end_box.setPosition(x_translate_shifted1,y_height1,z_depth1)
	end_box.setPosition(x_translate_shifted1,y_height1,z_depth1)
	#CHANGED THIS. Let's see if it works!
	reaction_timer_final=viz.tick()
	

def EnterProximity_end_sensor(end_sensor):
	end_of_trial=viz.tick()
	global matrix_id
	global right
	global times_crossed
	global subj_numb
	global tri_per_subj
	global a
	global b
	global error_iter
	
	
	trial=b+1
	box_size=control_array[a]
	distance=distance_between_targets1*2
	reaction_time=round((reaction_timer_final-reaction_timer_initial),2)
	movement_time= round((end_of_trial-reaction_timer_initial),2)
	num_cycles= times_crossed-1
	if error_iter==0:
		left_error= (times_entered_left_plane_error1-times_entered_left_plane)
		right_error= (times_entered_right_plane_error1-times_entered_right_plane)
	elif error_iter==1: 
		left_error= (times_entered_left_plane_error2-times_entered_left_plane2)
		right_error= (times_entered_right_plane_error2-times_entered_right_plane2)
	elif error_iter==2: 
		left_error= (times_entered_left_plane_error3-times_entered_left_plane3)
		right_error= (times_entered_right_plane_error3-times_entered_right_plane3)
	elif error_iter==3: 
		left_error= (times_entered_left_plane_error4-times_entered_left_plane4)
		right_error= (times_entered_right_plane_error4-times_entered_right_plane4)
	elif error_iter==4: 
		left_error= (times_entered_left_plane_error5-times_entered_left_plane5)
		right_error= (times_entered_right_plane_error5-times_entered_right_plane5)
	elif error_iter==5: 
		left_error= (times_entered_left_plane_error6-times_entered_left_plane6)
		right_error= (times_entered_right_plane_error6-times_entered_right_plane6)
	elif error_iter==6: 
		left_error= (times_entered_left_plane_error7-times_entered_left_plane7)
		right_error= (times_entered_right_plane_error7-times_entered_right_plane7)
	elif error_iter==7: 
		left_error= (times_entered_left_plane_error8-times_entered_left_plane8)
		right_error= (times_entered_right_plane_error8-times_entered_right_plane8)
	elif error_iter==8: 
		left_error= (times_entered_left_plane_error9-times_entered_left_plane9)
		right_error= (times_entered_right_plane_error9-times_entered_right_plane9)
	elif error_iter==9: 
		left_error= (times_entered_left_plane_error10-times_entered_left_plane10)
		right_error= (times_entered_right_plane_error10-times_entered_right_plane10)
	elif error_iter==10: 
		left_error= (times_entered_left_plane_error11-times_entered_left_plane11)
		right_error= (times_entered_right_plane_error11-times_entered_right_plane11)
	elif error_iter==11: 
		left_error= (times_entered_left_plane_error12-times_entered_left_plane12)
		right_error= (times_entered_right_plane_error12-times_entered_right_plane12)
	elif error_iter==12: 
		left_error= (times_entered_left_plane_error13-times_entered_left_plane13)
		right_error= (times_entered_right_plane_error13-times_entered_right_plane13)
	elif error_iter==13: 
		left_error= (times_entered_left_plane_error14-times_entered_left_plane14)
		right_error= (times_entered_right_plane_error14-times_entered_right_plane14)
	elif error_iter==14: 
		left_error= (times_entered_left_plane_error15-times_entered_left_plane15)
		right_error= (times_entered_right_plane_error15-times_entered_right_plane15)
	elif error_iter==15: 
		left_error= (times_entered_left_plane_error16-times_entered_left_plane16)
		right_error= (times_entered_right_plane_error16-times_entered_right_plane16)
	elif error_iter==16: 
		left_error= (times_entered_left_plane_error17-times_entered_left_plane17)
		right_error= (times_entered_right_plane_error17-times_entered_right_plane17)
	elif error_iter==17: 
		left_error= (times_entered_left_plane_error18-times_entered_left_plane18)
		right_error= (times_entered_right_plane_error18-times_entered_right_plane18)
	elif error_iter==18: 
		left_error= (times_entered_left_plane_error19-times_entered_left_plane19)
		right_error= (times_entered_right_plane_error19-times_entered_right_plane19)
	elif error_iter==19: 
		left_error= (times_entered_left_plane_error20-times_entered_left_plane20)
		right_error= (times_entered_right_plane_error20-times_entered_right_plane20)
	
	
	print ('right_error:'+ str(right_error-1))
	print ('left_error:'+ str(left_error))
	main_data.write(' '*1+ str(subj_numb))
	main_data.write(' '*4+ str(matrix_id))
	main_data.write(' '*3 + str(trial))
	main_data.write(' '*4 + str(box_size))
	main_data.write(' '*4 + str(distance*2))
	main_data.write(' '*2 + str(reaction_time))
	main_data.write(' '*1+ str(movement_time))
	main_data.write(' '*3 + str(num_cycles))
	main_data.write(' '*3+'le:'+str(left_error))
	main_data.write(' '*0+'re:'+str(right_error)+'\n')
	if b+1==int(tri_per_subj):
		subj_numb=vizinput.input('Please input the Subject Number:\n ')
		tri_per_subj=vizinput.input('Please input how many trials this subject will go through:\n ')
		print('in da loop')
		b=-1	
	b+=1
	a+=1	
	error_iter+=1
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
#
#def EnterProximity_right_plane_sensor1(right_plane_sensor1):
#	print('Entered right_plane1')
#	
#
#def ExitProximity_right_plane_sensor1(right_plane_sensor1):
#    print('Exited right_plane_sensor1')
#    global times_entered_right_plane
#    times_entered_right_plane+=1
#    print('Times Entered right Plane1: ', times_entered_right_plane)
#
#manager.onEnter(right_plane_sensor1,EnterProximity_right_plane_sensor1)
#manager.onExit(right_plane_sensor1,ExitProximity_right_plane_sensor1)

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

target = vizproximity.Target(handTracker)
manager.addTarget(target)

array_manipulator(control_array)
def reset_main_viewer():
	viz.move(0,0,0)
	
vizact.onkeydown('y', reset_main_viewer)
  
vizact.onkeydown('d',manager.setDebug,viz.TOGGLE)   
viz.go()

