import viz
import vizconnect


#################################
# Parent configuration, if any
#################################

def getParentConfiguration():
	#VC: set the parent configuration
	_parent = ''
	
	#VC: return the parent configuration
	return _parent


#################################
# Pre viz.go() Code
#################################

def initPreGo():
	return True

#################################
# Pre-initialization Code
#################################

def preInit():
	"""Add any code here which should be called after viz.go but before any initializations happen.
	Returned values can be obtained by calling getPreInitResult for this file's vizconnect.Configuration instance."""
	return None

#################################
# Group Code
#################################

def initGroups():
	rawGroup = {}
	default = ''
	return rawGroup, default


#################################
# Display Code
#################################

def initDisplays():
	rawDisplay = vizconnect.getRawDisplayDict()
	default = ''

	# initialization code for zsight_60 which is a SensicszSight60
	Hofs=[0, 0]
	Vofs=[0, 0]
	Rofs=[0, 0]
	VerticalSpan=False
	import sensics
	sensics.zSight_60(stereo=[viz.STEREO_HORZ,viz.STEREO_VERT][VerticalSpan], leftHorizontalShift=Hofs[0], rightHorizontalShift=Hofs[1], leftVerticalShift=Vofs[0], rightVerticalShift=Vofs[1], leftRollShift=Rofs[0], rightRollShift=Rofs[1], window=viz.MainWindow)
	rawDisplay['zsight_60'] = viz.MainWindow
	# setup fullscreen, code
	viz.window.setFullscreenMonitor(0)# set the fullscreen monitor
	viz.window.setFullscreen(True)

	# setting default
	default = 'zsight_60'

	return rawDisplay, default


#################################
# Tracker Code
#################################

def initTrackers():
	rawTracker = vizconnect.getRawTrackerDict()
	default = ''

	# initialization code for ppt which is a WorldVizPPT
	pptHostname="localhost"
	vrpn7 = viz.add('vrpn7.dle')
	# initialization for sub object ppt_Rhead
	markerId=1
	rawTracker['ppt_Rhead'] = vrpn7.addTracker('PPT0@'+pptHostname, markerId-1)
	# initialization for sub object ppt_Lhead
	markerId=2
	rawTracker['ppt_Lhead'] = vrpn7.addTracker('PPT0@'+pptHostname, markerId-1)
	# initialization for sub object ppt_hand
	markerId=4
	rawTracker['ppt_hand'] = vrpn7.addTracker('PPT0@'+pptHostname, markerId-1)

	# initialization code for osv3_sensor_bus which is a InertialLabsOSv3SensorBus
	port=11
	sensorIndex=0
	InertialLabs = viz.add('InertialLabs.dle')
	sensors = InertialLabs.addSensorBus(port=port)
	try:
		sensor = sensors[sensorIndex]
	except:
		viz.logWarn("** WARNING: can't connect to InertialLabs OSv3 (Sensor Bus) on port {0} with index {1}. It's likely that not enough sensors are connected.".format(port, sensorIndex))
		sensor = viz.addGroup()
		sensor.invalidTracker = True
	rawTracker['osv3_sensor_bus'] = sensor

	# transformation offset code for osv3_sensor_bus
	link = viz.link(rawTracker['osv3_sensor_bus'], viz.NullLinkable)
	link.setSrcMaskOverride(viz.LINK_ORI|viz.LINK_POS)
	link.preEuler([90, 0, 180])
	rawTracker['osv3_sensor_bus'] = link

	# initialization code for optical_heading which is a VirtualOpticalHeading
	leftPosTracker=vizconnect.getRawTracker('ppt_Lhead')
	rightPosTracker=vizconnect.getRawTracker('ppt_Rhead')
	oriTracker=vizconnect.getRawTracker('osv3_sensor_bus')
	distance=0.37
	from vizconnect.virtual_trackers import OpticalHeading
	rawTracker['optical_heading'] = OpticalHeading(leftPosTracker, rightPosTracker, oriTracker, distance=distance)

	# setting default
	default = 'ppt_Rhead'

	return rawTracker, default


#################################
# Input Code
#################################

def initInputs():
	rawInput = {}
	default = ''
	return rawInput, default


#################################
# Event Code
#################################

def initEvents():
	rawEvent = {}
	default = ''
	return rawEvent, default


#################################
# Transport Code
#################################

def initTransports():
	rawTransport = {}
	default = ''
	return rawTransport, default


#################################
# Tool Code
#################################

def initTools():
	rawTool = {}
	default = ''
	return rawTool, default


#################################
# Avatar Code
#################################

def initAvatars():
	rawAvatar = {}
	rawAnimator = {}
	default = ''
	return rawAvatar, rawAnimator, default


#################################
# Wrapper Code
#################################

def initWrappers():

	# get all of the raw items from vizconnect
	rawGroup = vizconnect.getRawGroupDict()
	rawInput = vizconnect.getRawInputDict()
	rawDisplay = vizconnect.getRawDisplayDict()
	rawTracker = vizconnect.getRawTrackerDict()
	rawTransport = vizconnect.getRawTransportDict()
	rawEvent = vizconnect.getRawEventDict()
	rawTool = vizconnect.getRawToolDict()
	rawAvatar = vizconnect.getRawAvatarDict()
	rawAnimator = vizconnect.getRawAnimatorDict()

	# below are listed the wrapped group objects

	# below are listed the wrapped display objects
	vizconnect.addDisplay(rawDisplay['zsight_60'], 'zsight_60', '', 'Sensics', 'zSight 60')

	# below are listed the wrapped tracker objects
	vizconnect.addTracker(rawTracker['ppt_Rhead'], 'ppt_Rhead', 'ppt', 'WorldViz', 'PPT')
	vizconnect.addTracker(rawTracker['optical_heading'], 'optical_heading', '', 'Virtual', 'Optical Heading')
	vizconnect.addTracker(rawTracker['ppt_hand'], 'ppt_hand', 'ppt', 'WorldViz', 'PPT')
	vizconnect.addTracker(rawTracker['osv3_sensor_bus'], 'osv3_sensor_bus', '', 'Inertial Labs', 'OSv3 (Sensor Bus)')
	vizconnect.addTracker(rawTracker['ppt_Lhead'], 'ppt_Lhead', 'ppt', 'WorldViz', 'PPT')

	# below are listed the wrapped input objects

	# below are listed the wrapped event objects

	# below are listed the wrapped transport objects

	# below are listed the wrapped tool objects

	# below are listed the wrapped avatar objects


	return True


#################################
# Tree Code
#################################

def initTree():
	# get a handle to the wrapped/vizconnect items
	group = vizconnect.getGroupDict()
	input = vizconnect.getInputDict()
	display = vizconnect.getDisplayDict()
	tracker = vizconnect.getTrackerDict()
	transport = vizconnect.getTransportDict()
	tool = vizconnect.getToolDict()
	avatar = vizconnect.getAvatarDict()
	root = vizconnect.getRoot()

	# initialize the tree structure of the vizard nodes
	display['zsight_60'].getNode3d().setParent(tracker['optical_heading'].getNode3d())

	# initialize the tree structure of the wrapped elements
	tracker['optical_heading'].addChild(display['zsight_60'])

	# initialize any pivots settings


	return True


#################################
# Post-initialization Code
#################################

def postInit():
	"""Add any code here which should be called after all of the initialization of this configuration is complete.
	Returned values can be obtained by calling getPostInitResult for this file's vizconnect.Configuration instance."""
	return None


###############################################

if __name__ == "__main__":
	from vizconnect import control_interface
	control_interface.go(__file__, openBrowserWindow=True, openChromiumWindow=False, startingInterface=control_interface.INTERFACE_ADVANCED)
	viz.add('gallery.osgb')


