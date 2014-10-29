#################### DON'T TOUCH! ##############
# define all tracker/display modes			   #
DESKTOP_MODE = 0                               #
HMD_MODE = 1								   #
POWERWALL_MODE = 2							   #
CAVE_MODE = 2								   #
HMD_DESKTOP_MODE = 3						   #
											   #
# save actual display mode					   #
DISPLAY_MODE = HMD_MODE				

# for standalone debugging
if __name__ == '__main__':
	import sys
	sys.path.insert( 0, '../')
################################################		   
################################################

import viz
import vizact
import vizuniverse as VU
import hand
	
PPT_MACHINE = 'localhost'
PPT_WAND_ID = 1
INERTIALLABS_HEAD_PORT = 11
INERTIALLABS_HAND_PORT = 7

#INTERSENSE_PORT = 1 #no intersense in current system
OPTICAL_HEADING = False


#### VideoVision ###
#import VideoVision 
#video = VideoVision.add(VideoVision.UEYE)
#cam1 = video.leftcam
#cam2 = video.rightcam


mainUser = None
# Create a custom composite that handles tracking, display, and input devices all together
def addUser():
	global mainUser
	# ---- Trackers ----
	# Initialize an empty composite object to store all the trackers
	# The composite.storeTracker() method is used to combine the individual trackers for the user's body within the composite
	composite = VU.VUCompositeTrackers()
	
	#### FOR PPT MARKERS ######
	vrpn = viz.add('vrpn7.dle')
	headPos = vrpn.addTracker( 'PPT0@'+PPT_MACHINE,0)
	
	if not OPTICAL_HEADING:
	#### FOR INTERSENSE ######
#		isense = viz.addExtension( 'intersense.dle' )
#		headOri = isense.addTracker(INTERSENSE_PORT)
#		VU.onkeydownspecial('r', headOri.reset ) 
		
	#### FOR INERTIAL LABS #####
		iLabs = viz.addExtension( 'inertiallabs.dle' )
		headOri = iLabs.addSensorBus(port=INERTIALLABS_HEAD_PORT)[0]
		VU.onkeydownspecial('r', resetHead, headOri, 90 )

	# ---- Display ----
#### FOR NVIS ####
#	import nvis
#	nvis.HMD(51.2,38.1)

#### FOR SENSICS ####
	import sensics
	sensics.zSight_60() # Q or 70()?
	#viz.window.setFullscreenMonitor([2,3]) #Q test using this instead of setting in NVIDIA?
#######################

#### FOR SONY ####
#	import sony
#	sony.HMZT1()
###########################	
	
	if not OPTICAL_HEADING:
		headTracker = viz.mergeLinkable( headPos, headOri )
	else:
		headTracker = headPos
	composite.storeTracker (composite.HEAD, headTracker )
	viz.setOption('viz.fullscreen', 1 ) #Q does this both control monitor and displays?
	
	# ---- Input ----
	wandpos = vrpn.addTracker('PPT0@' + PPT_MACHINE, PPT_WAND_ID)
	wandori = iLabs.addSensorBus(port=INERTIALLABS_HAND_PORT)[0]
	wandtracker = viz.mergeLinkable( wandpos, wandori )
#	wandjoy = VU.VUJoystickPPTWandVRPN(hostname=PPT_MACHINE, markerid=PPT_WAND_ID+1)
#	wandflyer = VU.VUTrackerWandFlyerSmooth(wandjoy, wandtracker,accelerationSteps=Config.WAND_ACCELERATION_STEPS, decelerationSteps=Config.WAND_DECELERATION_STEPS, speed=Config.WAND_SPEED_SCALE, keystrokes=[Config.WAND_BUTTON1,Config.WAND_BUTTON2,Config.WAND_BUTTON3,Config.WAND_BUTTON4,Config.WAND_BUTTON5,Config.WAND_BUTTON6],buttonReset=None, buttonForward=None, buttonFist=None, oriSteer=False )
#	wandflyer.getHandSensor().joystick = wandjoy
#	composite.addDriverNode(wandflyer)
	composite.storeTracker( composite.RHAND, wandtracker )
	composite.createRightHand(wandori)
	VU.onkeydownspecial('r', resetHand, wandori, 90 )
	
	# ---- Avatar ----
	composite.createAvatarNone()
	
	# ---- Finalize Composite ----
	composite.finishTrackers() # Build up internal links for all the tracking devices
	composite.defineViewpoint() # Attach viewpoint to default location on the user
	mainUser = composite
	manager.addComposite(mainUser, 'Main-User')
	
manager = None
def addManager():
	global manager
	# Create a default manager and keyboard controller which are always used
	manager = VU.VUManager()
	
def go():
	addManager()
	addUser()
	# Set up an external viewpoint so we can hit right shift to see different outside views
	ev = VU.VUExternalViewpoint(pos=[3,3,3], target=mainUser.getViewpointSource())
	manager.go()
	manager.changeHandListVisible(1)
	viz.mouse.setVisible(0)
	
def getManager():
	"""Interface for getting the manager variable"""
	return manager

def getHandList():
	"""Interface for getting a list of hands available"""
	return manager.getHandList()

def get(name):
	"""Use the composite manager dictionary to look up a reference in the global list"""
	return manager.get(name)

def resetHead(sensor, yawOffset=90):
	link = get('link0')
	link.reset(viz.RESET_OPERATORS )
	#Get yaw offset for intersense
	yaw = sensor.getEuler()[0]
	yaw -=yawOffset
	m = sensor.getMatrix()
	m.postEuler(-yaw,0,0)
	m.invert()
	quat = m.getQuat()
	#Apply offset to link
	link.postEuler([-yaw,0,0],target=viz.LINK_ORI_OP,priority=-20)
	link.preQuat(quat,target=viz.LINK_ORI_OP,priority=-20)
	
def resetHand(sensor, yawOffset=90):
	link = get('link2')
	link.reset(viz.RESET_OPERATORS )
	#Get yaw offset for intersense
	yaw = sensor.getEuler()[0]
	yaw -=yawOffset
	m = sensor.getMatrix()
	m.postEuler(-yaw,0,0)
	m.invert()
	quat = m.getQuat()
	#Apply offset to link
	link.postEuler([-yaw,0,0],target=viz.LINK_ORI_OP,priority=-20)
	link.preQuat(quat,target=viz.LINK_ORI_OP,priority=-20)

# This viztracker file is also able to run itself and show a simple demo when not imported directly
if __name__ == "__main__":
	# Load the 3D world in
	gal =viz.add('ground_grass.osgb')
	viz.setOption('viz.glFinish', 1 )
	go()
	
from viztrackerutils import *


