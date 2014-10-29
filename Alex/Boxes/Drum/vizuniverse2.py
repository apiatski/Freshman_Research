# Copyright (c) 2001-2013 WorldViz LLC.
# All rights reserved.

"""
WorldViz Super Universal Library

Keypress information:
	Alt-F5			Disables fly-through for all views
	Alt-F6			Enables fly-through for all views
	Alt-h			Toggles hand visibility and auto-hide mode
	Break			Used to quit out now (pause key on some keyboards)
	Alt-r			Reset the orientation heading if an IC2 is connected
	Alt-p			Reset the current position to be the origin
	Left-Shift		Activates debugging information for all composites in VUManager()
	Left-Control	Activates external viewpoint if VUExternalViewpoint() used
	Alt-`			0:1 XZ scaling (no movement possible)
	Alt-q			1:1 XZ scaling
	Alt-w			2:1 XZ scaling
	Alt-e			3:1 XZ scaling
"""

import viz
import vizinfo
import vizact
import vizmat
import __main__
import hand
import math


# This library uses many recent Vizard features, so this version check is important
viz.requireVersion ("3.16.0009")

# Define various constants that control how the GrabHand code works
HAND_FINGER_RADIUS    = 0.01  # (hand.configFingerRadius)    The size of the bounding spheres on the finger tips, if they touch this is considered a pinch
HAND_TOUCH_RADIUS     = 0.10  # (hand.configTouchRadius)     The maximum distance an object could be away from the hand selector to be considered grabbable
HAND_FIST_ANGLE       = 45.0  # (hand.configFistAngle)       The angle the fingers need to bend to be considered a fist gesture
HAND_PINCH_ENABLE     = True  # (hand.configPinchEnable)     By default gloves will support pinch detection
HAND_DEBUG_PRIMITIVES = False # (hand.configDebugPrimitives) Show physics primitives so we can debug the operation of the hands

# Define various constants that control the auto hand hiding algorithm
AUTOHAND_POS  = 0.01 # Distance to move a hand to make it active again (10 cm)
AUTOHAND_TIME = 10   # Number of seconds to wait with no movement before hiding a hand



def FatalError(str,exceptionClass=RuntimeError):
	""" Internal function used to terminate processing when something unexpected happens """
	# viz.message('Fatal error detected in vizuniverse script: ' + str) # Do not show a pop up, it is not always visible in some monitor configurations
	viz.quit() # Must exit Vizard before the assert stops Python execution
	raise exceptionClass(str)




def isSpecialModifierPressed():
	"""
	Internal function used to check if the modifier key is being held down. We use this so that vizuniverse
	keystrokes which are global and used for special configuration options do not get in the way of scripts
	and whatever keys they might want to use. Note that we use the ALT keys instead of CONTROL because if you
	do keystrokes like Control-R, you don't get 'r' as the event, but some different scan code from Windows
	"""
	return viz.key.isDown(viz.KEY_ALT_L, immediate=True) or viz.key.isDown(viz.KEY_ALT_R, immediate=True)

_onkeydownspecial = []
def onkeydownspecial(key, function, *args):
	"""
	Internal function code that can use instead of vizact.onkeydown when you want to test if the modifier key
	is pressed at the same time. That way vizuniverse and vizmultiscript code will only activate if the modifier
	key is active, allowing other scripts to use whatever keys they want internally
	"""
	handler = [key, function, args]
	_onkeydownspecial.append(handler)

class SpecialKeyHandler(viz.EventClass):
	"""Internal handler class designed to detect keypresses when a modifier key is down as well, should not be used by other scripts"""
	def __init__(self):
		viz.EventClass.__init__(self)
		self.callback(viz.KEYDOWN_EVENT, self.onkeydown, priority=viz.PRIORITY_DEFAULT_KEY-2) # Use -2 because we reserve -1 for eating up other keys

	def onkeydown(self,inkey):
		"""
		We check to see if the modifier key is down when a key is pressed. If one of the modifier keys are currently down,
		then we will handle the key here in vizuniverse.py, otherwise we pass the key on to whatever script that is running. That
		way special internal functions do not use keystrokes that other scripts might want to use.
		"""

		# If we get the break key, then quit Vizard
		if inkey == viz.KEY_BREAK:
			viz.logNotice("vizuniverse: Terminating Vizard due to break key being pressed")
			viz.quit()
			return True # Key handled, prevent other code from seeing this keypress

		if not isSpecialModifierPressed():
			return False # Modifier key not pressed, key is not meant for vizuniverse.py to process

		# Traverse the list of key mappings, we need to look through all of them, there might be more than one call mapped to a single key
		for each in _onkeydownspecial:
			[key,function,args] = each
			if inkey == key:
				function(*args)

		# It is important that we return True so that standard Vizard code never sees this keystroke, since the modifier key was detected above
		return True

class IgnoreKeyHandler(viz.EventClass):
	"""Internal handler class designed to detect keypresses when a modifier key is down as well, should not be used by other scripts"""
	def __init__(self,ignore):
		viz.EventClass.__init__(self)
		self.callback(viz.KEYDOWN_EVENT, self.onkeydown, priority=viz.PRIORITY_DEFAULT_KEY-1) # Run at a higher priority that the standard vizuniverse handler
		self.ignore = ignore

	def onkeydown(self,key):
		if key == self.ignore:
			viz.logNotice("IgnoreKeyHandler: Key press %s detected, but has been requested to be ignored" % key)
			return True
		else:
			return False




class VUTrackerGeneric(viz.VizNode):
	""" Base class used to provide a set of base functionality for all our tracker abstractions """
	def __init__(self, inTracker=None, pos=[0,0,0]):
		self.outtracker = viz.addGroup()
		self.trackerlink = None
		self.trackerlinkupdate = None
		viz.VizNode.__init__(self,self.outtracker.id)
		if inTracker is None:
			posTrk = viz.addGroup()
			posTrk.setPosition (pos)
			self.saveTracker(posTrk) # Add the tracker so we have something in here
		else:
			self.saveTracker(inTracker) # Add the supplied tracker

	def getOutput(self):
		""" Method to access the tracker object stored internally, although this object is also a VizNode """
		return self.outtracker

	def getInput(self):
		""" Method to access the raw input tracker object before the link is applied """
		return self.intracker

	def saveTracker(self, trk, priority=viz.PRIORITY_PLUGINS+1): # Set the priority just after the inputs arrive
		"""
		This method links the input up against the internal output. All objects that inherit this class
		use the saveTracker method, so this takes care of everything to do with storing the input
		"""
		self.intracker = trk
		if self.trackerlink is not None:
			self.trackerlink.remove()
		self.trackerlink = viz.link (self.intracker, self.outtracker, enabled=False)
		self.trackerlinkupdate = vizact.onupdate (priority, self.trackerlink.update)

	def getLink(self):
		"""
		Method that gives access to the internal link used for the tracker. You can apply operators to this link to
		implement scaling, changes in coordinate systems, etc. These are needed when working with some trackers
		"""
		return self.trackerlink

	def getLinkUpdate(self):
		"""
		Method that gives you access to the link update function, so that you can disable it if desired
		"""
		return self.trackerlinkupdate

	def getTrackerLink(self):
		"""This is a deprecated interface to getting a tracker link, you should call getLink() instead"""
		return self.getLink()

	def _magneticOffset(self, input, magneticzero):
		""" This method is used with Intersense and Xsens trackers, apply a magnetic offset so no reset command is needed """
		if magneticzero is None or magneticzero == 0:
			return input
		else:
			viz.logNotice("Adjusting orientation sensor with magnetic zero at %.1f" % magneticzero)
			output = viz.addGroup()
			link = viz.link (input, output, enabled=False)
			vizact.onupdate(viz.PRIORITY_PLUGINS+1, link.update) # Perform offset just after all sensors are read in
			link.postEuler ([-magneticzero, 0, 0])
			return output

	def getSupplementDevice(self):
		"""If one of the following supplement* methods are called, this will store a handle to the raw device in case we need to get access to it"""
		if hasattr(self, "supplementdev"):
			return self.supplementdev
		else:
			return None

	def supplementIntersense (self, comport=0, station=0, magneticzero=None, multiply=False):
		"""
		Take an existing tracker and add an InterSense for orientation, useful with 3DOF position trackers
		If you set magneticzero, it is assumed that this angle is zero and will be subtracted from the output
		"""
		if comport is 0:
			viz.logNotice("Tracker is using supplemental local Intersense data, starting auto-detection")
		elif comport is None:
			viz.logNotice("Supplemental local Intersense data is specified as None, so skipping adding extra orientation data")
			return self
		else:
			viz.logNotice("Tracker is using supplemental local Intersense data on COM%d" % comport)
		isense = viz.add('intersense.dle')
		oriTrk = isense.addTracker(port=comport,station=station)

		if oriTrk.valid():
			# Now call the generic supplement interface to add the sensor to the tracker
			return self.supplementGeneric(oriTrk, magneticzero=magneticzero, multiply=multiply)
		else:
			viz.logError("Failed to open up Intersense device on COM%d" % comport)
			return self

	def supplementXsens (self, comport=0, magneticzero=None, multiply=False):
		""" Take an existing tracker and add an Xsens for orientation, useful with 3DOF position trackers """
		if comport is 0:
			viz.logNotice("Tracker is using supplemental local Xsens data, starting auto-detection")
		elif comport is None:
			viz.logNotice("Supplemental local Xsens data is specified as None, so skipping adding extra orientation data")
			return self
		else:
			viz.logNotice("Tracker is using supplemental local Xsens data on COM%d" % comport)

		xsens = viz.add('xsens.dle')
		oriTrk = xsens.addMT(port=comport)
		if oriTrk.valid():
			# Now call the generic supplement interface to add the sensor to the tracker
			return self.supplementGeneric(oriTrk, magneticzero=magneticzero, multiply=multiply)
		else:
			viz.logError("Failed to open up Xsens device on COM%d" % comport)
			return self

	def supplementAutoOrientation (self, comport=0, magneticzero=None, multiply=False):
		""" Similar to above, except we try to auto-detect for any InterSense or Xsens device we can find """
		# Fix up the comport value if needed
		if comport is True:
			comport = 0
		if comport is None:
			comport = 0

		# Initially seach for an Intersense device
		isense = viz.add('intersense.dle')
		sensor = isense.addTracker(port=comport)
		if not sensor.valid():
			xsens = viz.add('xsens.dle')
			sensor = xsens.addMT(port=comport)
			if not sensor.valid():
				viz.logError("Failed to detect any InterSense or Xsens device")
				return self
			else:
				viz.logNotice("Detected Xsens device automatically")
				oriTrk = sensor
		else:
			viz.logNotice("Detected InterSense device automatically")
			oriTrk = sensor

		# Now call the generic supplement interface to add the sensor to the tracker
		return self.supplementGeneric(oriTrk, magneticzero=magneticzero, multiply=multiply)

	def supplementGeneric (self, device, magneticzero=None, multiply=False):
		"""
		Take an existing tracker and add another tracker for orientation, useful with 3DOF position trackers
		If you set magneticzero, it is assumed that this angle is zero and will be subtracted from the output
		"""
		# The input device will be used directly, don't open up anything
		oriTrk = device
		# Store the supplemented tracker in case we need a reference to it later
		self.supplementdev = oriTrk
		# Apply magnetic offset
		ofsOriTrk = self._magneticOffset(oriTrk, magneticzero)
		# Combine existing pos with new ori
		if multiply:
			self.getLink().preMultLinkable(ofsOriTrk) # Multiply in the new orientation, preserve old orientation
		else:
			newTrk = viz.mergeLinkable (self.getInput(), ofsOriTrk) # Overwrite existing ori with new ori data
			self.saveTracker (newTrk) # Need to resave this as a new tracker
		# Add a handler to reset the heading of the cube
		if magneticzero is None or magneticzero == 0:
			onkeydownspecial ('r', oriTrk.reset)
		return self # Do this so we can add this as a method with the constructor VUTrackerGeneric().supplementIntersense()

	def supplementOrientation (self, intersense=None, xsens=None, auto=None, generic=None, magneticzero=None):
		""" Wrapper for the above functions, supply three variables and if any are non-None then we supplement using that """
		if intersense is not None:
			return self.supplementIntersense (comport=intersense, magneticzero=magneticzero)
		elif xsens is not None:
			return self.supplementXsens (comport=xsens, magneticzero=magneticzero)
		elif generic is not None:
			return self.supplementGeneric (generic, magneticzero=magneticzero)
		elif auto is not None:
			return self.supplementAutoOrientation (comport=auto, magneticzero=magneticzero)
		else:
			return self # Do nothing and just return back the object unmodified




class VUTrackerIntersense(VUTrackerGeneric):
	"""
	This class is a wrapper around Intersense DLL trackers. It is meant to be used directly
	with 6DOF devices such as the IS-900. If you want to connect an IC2 with a position tracker,
	or just use an IC2 by itself, then use the provided supplementIntersense methods provided in VUTrackerGeneric
	"""
	def __init__(self, comport=0, station=0, type="Intersense"):
		VUTrackerGeneric.__init__(self)

		if comport is 0:
			viz.logNotice("Starting auto-detect for %s tracker" % type)
		else:
			viz.logNotice("Opening %s tracker on COM%d" % (type, comport))

		# Add the tracker and deal with any failures
		isense = viz.add('intersense.dle')
		posTrk = isense.addTracker(port=comport,station=station)
		if not posTrk.valid():
			viz.logNotice("%s tracker could not be connected, adding dummy node instead" % type)
			posTrk = viz.addGroup()
			posTrk.setPosition (0, 1.8, 0)

		# Store the tracker device
		self.saveTracker (posTrk)


class VUTrackerPPTWand(VUTrackerIntersense):
	"""Use the same interface as the above class"""
	def __init__(self, comport=0, type="PPTWand"):
		VUTrackerIntersense.__init__(self, comport=comport, type=type)



invalidHostnames = []
def getResolvedHostnameVRPN(vrpnhost):
	"""
	VRPN does not deal well with hostnames that do not resolve, it will block Vizard each time it retries the lookup
	So if the hostname is not valid, we turn it into an empty string so that VRPN will not keep retrying all the time
	"""

	# Split the VRPN string into the name and host parts
	delim = vrpnhost.find('@')
	if delim < 0:
		viz.logError("ERROR! VRPN string supplied [%s] is not valid, missing @ separator, a connection is not possible" % vrpnhost)
		return None
	else:
		trackname = vrpnhost[:delim]
		hostname = vrpnhost[delim+1:]

	# If the hostname or tracker name is empty then it is invalid
	if hostname == "":
		viz.logError("ERROR! VRPN string [%s] contains an empty hostname, a connection is not possible" % vrpnhost)
		return None
	if trackname == "":
		viz.logError("ERROR! VRPN string [%s] contains an empty tracker name, a connection is not possible" % vrpnhost)
		return None

	# Check that the hostname and tracker name do not contain any other @ symbols, which should not happen
	if hostname.find('@') >= 0 or trackname.find('@') >= 0:
		viz.logError("ERROR! VRPN string [%s] contains more than one @ separator, a connection is not possible" % vrpnhost)
		return None

	# If the hostname already failed, then reject it straight away, doing a real lookup can take a few seconds to timeout
	if hostname in invalidHostnames:
		viz.logError("ERROR! VRPN string supplied [%s] previously failed to resolve a hostname [%s], a connection is not possible" % (vrpnhost, hostname))
		return None

	# Test the hostname to see if it is valid by looking it up
	import socket
	try:
		ipaddr = socket.gethostbyname (hostname)
	except socket.gaierror, e:
		viz.logError("ERROR! VRPN string supplied [%s] could not resolve hostname [%s], a connection is not possible - %s" % (vrpnhost, hostname, e))
		invalidHostnames.append (hostname)
		return None

	# If we make it here, then we have a valid hostname and we can continue
	return vrpnhost


def getResolvedHostnameGeneric(hostname):
	""" Same as getResolvedHostnameVRPN, but supports generic hostnames for anything else that needs it """

	# If the hostname is empty then it is invalid
	if hostname == "":
		viz.logError("ERROR! Hostname supplied is empty, a connection is not possible")

	# If the hostname already failed, then reject it straight away, doing a real lookup can take a few seconds to timeout
	if hostname in invalidHostnames:
		viz.logError("ERROR! Hostname supplied [%s] previously failed to resolve hostname [%s], a connection is not possible" % (hostname, hostname))
		return None

	# Test the hostname to see if it is valid by looking it up
	import socket
	try:
		ipaddr = socket.gethostbyname (hostname)
	except socket.gaierror, e:
		viz.logError("ERROR! Hostname supplied [%s] could not be resolved, a connection is not possible - %s" % (hostname, e))
		invalidHostnames.append (hostname)
		return None

	# If we make it here, then we have a valid hostname and we can continue
	return hostname




class VUTrackerVRPN(VUTrackerGeneric):
	""" Provides a simple abstraction for dealing with VRPN-based devices. This is used by VUCompositeTrackersVRPN for trackers like PPT. """
	def __init__(self, vrpnhost, sensorid=0, swapPos=None, swapQuat=None):
		VUTrackerGeneric.__init__(self)
		vrpn = viz.add ('vrpn7.dle')

		# Test the VRPN path to make sure it is valid
		if getResolvedHostnameVRPN (vrpnhost) is None:
			viz.logWarn("Warning! No valid hostname available, so skipping VRPN connection to [%s], sensor %d" % (vrpnhost, sensorid))
			posTrk = viz.addGroup()
		else:
			viz.logNotice("Opening VRPN connection to %s, sensor %d" % (vrpnhost, sensorid))
			posTrk = vrpn.addTracker(vrpnhost, sensorid)
			# Note you cannot check VRPN for errors, since they never fail and just sit there retrying forever

		# Some tracker systems need coordinate inversions, so do this all here
		if swapPos is not None:
			viz.logNotice('Performing swapPos %s for VRPN source' % swapPos)
			posTrk.swapPos(swapPos)
		if swapQuat is not None:
			viz.logNotice('Performing swapQuat %s for VRPN source' % swapQuat)
			posTrk.swapQuat(swapQuat)
		import re
		dt = re.compile ('^DTrack@')
		if dt.search (vrpnhost):
			viz.logNotice('Performing automatic adjustment of coordinates for ART DTrack with extra operators')
			posTrk.swapPos([1,2,-3]) # Negate Z value of position
			posTrk.swapQuat([-1,-2,3,4]) # Negate X,Y value of quaternion
		dt = re.compile ('^iotracker@')
		if dt.search (vrpnhost):
			viz.logNotice('Performing automatic adjustment of coordinates for IO-Tracker with extra operators')
			posTrk.swapPos([1,3,2]) # Flip around components
			posTrk.swapQuat([1,3,2,-4])

		# Store the tracker device
		self.saveTracker (posTrk)




class VUJoystickGeneric(object):
	"""This generic class is a standard interface for talking with most joysticks of various types, this class may need extending for anything that is not a VizSensor"""
	def __init__(self, device=None, zeroRound=0.1, xInvert=False, yInvert=False):
		"""
		@param zeroRound: The area where the joystick does nothing, 1.0 will cause the device to not do anything, should be close to 0.0
		@param device: Can supply a vizjoy object to use, otherwise defaults to opening a new one if None used
		@param xInvert: Flip the X axis. By default left=-1 and right=+1
		@param yInvert: Flip the Y axis. By default up=-1 and down=+1, but some hardware may do this differently
		"""
		self.initDevice(device)
		self.zeroRound = zeroRound
		self.xInvert = xInvert
		self.yInvert = yInvert

	def initDevice(self, device):
		"""Save the supplied joystick device internally"""
		self.joydev = device

	def getRawDevice(self):
		"""Return a direct reference to the joystick input"""
		return self.joydev

	def roundZero(self, val):
		"""Take an input value and round it to zero if it is close"""
		if abs(val) < self.zeroRound:
			return 0.0
		else:
			return val

	def getX(self):
		x = self.getRawX()
		if self.xInvert:
			x = -x
		return self.roundZero(x)

	def getY(self):
		y = self.getRawY()
		if self.yInvert:
			y = -y
		return self.roundZero(y)

	def getRawX(self):
		"""Return the X value of the joystick"""
		data = self.joydev.getData()
		if len(data) >= 2:
			return data[0]
		else:
			return 0

	def getRawY(self):
		"""Return the Y value of the joystick"""
		data = self.joydev.getData()
		if len(data) >= 2:
			return data[1]
		else:
			return 0

	def getAnalog(self, num):
		"""Return the current state of an analog input value"""
		data = self.joydev.getData()
		if num > len(data) or num < 1:
			return 0
		else:
			return data[num-1]

	def isButtonDown(self, num):
		"""Return button information from the sensor, most devices number their buttons from 0 upwards"""
		if num < 0:
			return 0
		else:
			return self.joydev.isButtonDown(num)




class VUJoystickStandard(VUJoystickGeneric):
	"""This generic class is a wrapper around a standard vizjoy joystick, and other types of input devices can also implement a similar interface"""
	def __init__(self, device=None, **kw):
		"""
		@param device: Can supply a vizjoy object to use, otherwise defaults to opening a new one if None used
		"""
		if device is None:
			import vizjoy
			device = vizjoy.add()
		VUJoystickGeneric.__init__(self, device=device, **kw)

	def getRawX(self):
		"""Return the X value of the joystick"""
		return self.joydev.getPosition()[0]

	def getRawY(self):
		"""Return the Y value of the joystick"""
		return self.joydev.getPosition()[1]

	def getTwist(self):
		"""Returns the twist value if that is available on the joystick"""
		return self.roundZero(self.joydev.getTwist())

	def getSlider(self):
		"""Returns the slider value if that is available on the joystick"""
		return self.roundZero(self.joydev.getSlider())

	def getHatX(self):
		"""Returns the X value of a hat switch that might be available on the joystick"""
		hat = math.ceil(self.joydev.getHat())
		if hat == -1:
			return 0
		elif hat > 180 or hat < 0:
			return -1
		elif hat > 0 and hat < 180:
			return +1
		else:
			return 0

	def getHatY(self):
		"""Returns the Y value of a hat switch that might be available on the joystick"""
		hat = math.ceil(self.joydev.getHat())
		if hat == -1:
			return 0
		elif hat > 270 or hat < 90:
			return +1
		elif hat > 90 and hat < 270:
			return -1
		else:
			return 0

	def getAnalog(self, num):
		"""Return the current state of an analog input value. We map up the slider and twist values to some of these channels."""
		import vizjoy
		if num == vizjoy.SLIDER_EVENT:
			return self.getSlider()
		elif num == vizjoy.TWIST_EVENT:
			return self.getTwist()
		else:
			return 0

	def isButtonDown(self, num):
		"""Return button information from the joystick, note that to be consistent we number from 0 although vizjoy starts from 1"""
		if num < 0:
			return 0
		else:
			return self.joydev.isButtonDown(num+1)




class VUJoystickTrackD(VUJoystickGeneric):
	"""This generic class is a wrapper around a trackd input device, it is the same as VUJoystickGeneric except we invert the Y axis"""
	def getRawX(self):
		"""Return the X value of the joystick"""
		data = self.joydev.getData()
		if len(data) >= 2:
			return data[0]
		else:
			return 0

	def getRawY(self):
		"""Return the Y value of the joystick"""
		data = self.joydev.getData()
		if len(data) >= 2:
			return -data[1] # TrackD uses up=+1 whereas we use up=-1, so perform the conversion here
		else:
			return 0




class VUJoystickIntersense(VUJoystickGeneric):
	"""This generic class is a wrapper around a generic joystick input device"""
	def __init__(self, device=None, **kw):
		"""
		@param device: Supply an Intersense controller object to use for the input values
		"""
		# Convert VUTracker* class to a raw tracker type
		if isinstance(device, VUTrackerIntersense):
			rawtracker = device.getInput() # Grab the InterSense raw tracker
		elif isinstance(device, VUTrackerGeneric):
			rawtracker = device.getInput() # This is also legal as well
		else:
			rawtracker = device # Use the device directly

		# Is the raw tracker a valid input or not?
		if isinstance(rawtracker, viz.VizGroup):
			viz.logWarn("Warning! Input tracker for VUJoystickIntersense was not valid, so no incoming data can be processed")
			VUJoystickGeneric.__init__(self, None) # The Intersense failed to load, so we don't actually have real data incoming
		else:
			VUJoystickGeneric.__init__(self, rawtracker, **kw)

	def getRawX(self):
		"""Return the X value of the joystick"""
		if self.joydev is not None:
			return self.joydev.getJoystickPosition()[0]
		else:
			return 0

	def getRawY(self):
		"""Return the Y value of the joystick"""
		if self.joydev is not None:
			return self.joydev.getJoystickPosition()[1] # Note that intersense.dle returns up=-1, down=+1
		else:
			return 0

	def getAnalog(self, num):
		"""Analog inputs are not supported on this device"""
		return 0

	def isButtonDown(self, num):
		"""Interface to the device extension to get the button information"""
		if self.joydev is None:
			return 0
		if num < 0:
			return 0
		if num >= 6:
			return 0
		return self.joydev.isButtonDown(num)




class VUJoystickPPTWand(VUJoystickIntersense):
	"""This generic class is a wrapper around the Intersense input device, which uses similar inputs"""




class VUJoystickKeyboard(VUJoystickGeneric):
	"""This generic class is a wrapper around a generic joystick input device"""
	def __init__(self, **kw):
		"""
		@param device: No input device needed, keyboard arrow keys are assumed
		"""
		VUJoystickGeneric.__init__(self, **kw)

	def getRawX(self):
		"""Return the X value of the joystick"""
		if viz.key.isDown(viz.KEY_LEFT):
			return -1
		elif viz.key.isDown(viz.KEY_RIGHT):
			return +1
		else:
			return 0

	def getRawY(self):
		"""Return the Y value of the joystick"""
		if viz.key.isDown(viz.KEY_UP):
			return -1
		elif viz.key.isDown(viz.KEY_DOWN):
			return +1
		else:
			return 0

	def getAnalog(self, num):
		"""Analog inputs are not supported on this device"""
		return 0

	def isButtonDown(self, num):
		"""Map buttons to the number keys"""
		if viz.key.isDown(num):
			return True
		else:
			return False




class VUJoystickVRPN(VUJoystickGeneric):
	"""Joystick interface around VRPN7 button and analog server devices"""
	def __init__(self, buttondev=None, analogdev=None, device=None, **kw):
		"""
		@param buttondev: Device that provides button press information
		@param analogdev: Device that provides analog joystick information
		@param device: If this is supplied then use this for buttondev and analogdev
		"""

		# Work out what to do with the input arguments, store them internally
		self.analogdev = None
		self.buttondev = None
		if device is not None:
			self.analogdev = device
			self.buttondev = device
		if buttondev is not None:
			self.buttondev = buttondev
		if analogdev is not None:
			self.analogdev = analogdev
		if self.analogdev is None:
			FatalError ("VUJoystickVRPN object requires an analog device either directly or via the device argument")
		if self.buttondev is None:
			FatalError ("VUJoystickVRPN object requires a button device either directly or via the device argument")

		# Call the default joystick constructor to pass on a few arguments, we also need to send some kind of device value as well
		VUJoystickGeneric.__init__(self, device=self.analogdev, **kw)

	def getRawX(self):
		"""Return the X value of the joystick"""
		return self.analogdev.getData()[0]

	def getRawY(self):
		"""Return the Y value of the joystick"""
		return self.analogdev.getData()[1]

	def getAnalog(self, num):
		"""Return the current state of an analog input value"""
		data = self.analogdev.getData()
		if num > len(data) or num < 1:
			return 0
		else:
			return data[num-1]

	def isButtonDown(self, num):
		"""Return the current state of a button input value"""
		if num < 0:
			return 0
		else:
			return self.buttondev.isButtonDown(num)




class VUJoystickPPTWandVRPN(VUJoystickGeneric):
	"""Joystick interface around VRPN7 button and analog server devices"""
	def __init__(self, hostname=None, markerid=1, **kw):
		"""
		@param hostname: Host that the PPT is running on, which is processing the wand device
		@param markerid: Marker ID in PPT that the wand is mapped to (1..N)
		"""

		# Work out what to do with the input arguments, store them internally
		self.hostname = hostname
		vrpn = viz.add('vrpn7.dle')
		if getResolvedHostnameGeneric(hostname) is None:
			viz.logWarn("Warning! No valid hostname available, so skipping connection to PPTWand at [%s]" % hostname)
			self.analogdev = None
			self.analogdev = None
		else:
			self.analogdev = vrpn.addAnalog('PPT_WAND%d@%s:%d' % (markerid, hostname, 8945))
			self.buttondev = vrpn.addButton('PPT_WAND%d@%s:%d' % (markerid, hostname, 8945))

		# Call the default joystick constructor to pass on a few arguments, we also need to send some kind of device value as well
		VUJoystickGeneric.__init__(self, device=self.analogdev, **kw)

	def getRawX(self):
		"""Return the X value of the joystick"""
		if self.analogdev.getSampleNumber() <= 0:
			return 0.0
		else:
			return self.analogdev.getData()[0]

	def getRawY(self):
		"""Return the Y value of the joystick"""
		if self.analogdev.getSampleNumber() <= 0:
			return 0.0
		else:
			return self.analogdev.getData()[1] # PPT returns up=-1 and down=+1

	def getAnalog(self, num):
		"""Return the current state of an analog input value"""
		data = self.analogdev.getData()
		if num > len(data) or num < 1:
			return 0
		else:
			return data[num-1]

	def isButtonDown(self, num):
		"""Return the current state of a button input value"""
		if num < 0:
			return 0
		else:
			return self.buttondev.isButtonDown(num)




class VUTrackerJoystick(VUTrackerGeneric, viz.EventClass):
	""" This class opens up a joystick, we use the first stick for position, and the second for orientation """
	def __init__(self, startpos=[0,0,0], starteuler=[0,0,0], mode="World", zeroRound=0.1, posScale=0.1, oriScale=5.0, device=None):
		"""
		@param startpos: The default starting position for the tracker
		@param starteuler: The default starting orientation for the tracker
		@param mode: Mode can be "World", "Local", "Driver", or "Flight"
		@param zeroRound: The area where the joystick does nothing, 1.0 will cause the device to not do anything
		@param posScale: Scaling factor to apply to joystick -1.0..+1.0 values
		@param oriScale: Scaling factor to apply to orientation values
		@param device: Can supply a vizjoy object to use, otherwise defaults to opening a new one if None used
		"""

		# Initialize the base classes
		VUTrackerGeneric.__init__(self)
		viz.EventClass.__init__(self)

		# Decide on how this class will be used
		if mode is None or mode.lower() in [ "world", "" ]:
			self.refresh = self.refreshWorld		# Drive around in world coordinates (the default)
		elif mode.lower() in [ "local" ]:
			self.refresh = self.refreshLocal		# Drive around in local coordinates
		elif mode.lower() in [ "driving", "driver", "car" ]:
			self.refresh = self.refreshDriver		# Drive around like a car would, from the car perspective
		elif mode.lower() in [ "flying", "flight", "airplane" ]:
			self.refresh = self.refreshFlight		# Drive around like an airplane, with velocity controlled by joystick
		else:
			FatalError("The mode flag [%s] does not match any of the defined driving modes" % mode)

		# Set up a callback to be called each time the display refreshes
		viz.EventClass.callback(self,viz.UPDATE_EVENT,self.refreshDevice)
		self.starttimer(0,0,viz.PERPETUAL)

		# Store all the things we need for the refresh later
		self.posTrk = viz.addGroup()				# Generate a tracker object to return back
		self.posTrk.setPosition (startpos)
		self.posTrk.setEuler (starteuler)
		self.saveTracker (self.posTrk)
		self.startPos = startpos
		self.startEuler = starteuler
		self.posScale = posScale
		self.oriScale = oriScale

		# Initialize the joystick hardware, if device is None then VUJoystickStandard takes care of this
		self.joy = VUJoystickStandard(device=device, zeroRound=zeroRound)

	def refreshDevice(self, num):
		# Read all the joystick values, and clean them up, everything is from -1..+1
		x = self.joy.getX()
		y = self.joy.getY()
		if hasattr(self.joy, "getSlider"):
			slide  = self.joy.getSlider()
			twist  = self.joy.getTwist()
			updown = self.joy.getHatY()
		else:
			slide  = 0
			twist  = 0
			updown = 0

		if self.joy.isButtonDown(0):
			self.posTrk.setPosition (self.startPos)
			self.posTrk.setEuler (self.startEuler)

		# Now do the work depending on which interface we've selected
		self.refresh(x, y, updown, twist, slide)


	def refreshWorld(self, X, Y, Z, H, P):
		pos = self.posTrk.getPosition()
		pos[0] = pos[0] + X * self.posScale
		pos[1] = pos[1] + Z * self.posScale
		pos[2] = pos[2] - Y * self.posScale
		self.posTrk.setPosition (pos)

		eul = self.posTrk.getEuler()
		eul[0] = eul[0] + H * self.oriScale
		eul[1] = P * 80.0 # Don't go all the way or the heading could flip around
		self.posTrk.setEuler (eul)

	def refreshLocal(self, X, Y, Z, H, P):
		self.posTrk.setPosition (X * self.posScale, 0, -Y * self.posScale, mode=viz.REL_LOCAL)

		eul = self.posTrk.getEuler()
		eul[0] = eul[0] + H * self.oriScale
		eul[1] = eul[1] + P * self.oriScale
		if eul[1] < -80:
			eul[1] = -80
		if eul[1] > 80:
			eul[1] = 80
		self.posTrk.setEuler (eul)

	def refreshDriver(self, X, Y, Z, H, P):
		self.posTrk.setPosition (0, 0, -Y * self.posScale, mode=viz.REL_LOCAL)

		eul = self.posTrk.getEuler()
		eul[0] = eul[0] + X * self.oriScale
		self.posTrk.setEuler (eul)

	def refreshFlight(self, X, Y, Z, H, P):
		newP = -P / 2.0 + 0.5 # Change from -1..+1 to 0..+1
		speed = newP * self.posScale
		self.posTrk.setPosition (0, 0, speed, mode=viz.REL_LOCAL)

		eul = [ 0, 0, 0 ]
		eul[1] = -Y * self.oriScale
		eul[2] = -X * self.oriScale
		self.posTrk.setEuler (eul, viz.REL_LOCAL)




# This is a class which can use an IS-900 wand for orientation, and by using the joystick the user can fly around
class VUTrackerWandFlyer(viz.EventClass, VUTrackerGeneric):
	"""
	This class is similar to VUTrackerJoystick, but it is designed for flying around in a CAVE environment
	@param controller: VUJoystickGeneric device which supplies joystick and button inputs
	@param tracker: Tracking device that supplies orientation data, if supplied then will fly in the direction pointed
	@param xscale: Adjust the speed of position movements in X axis (left and right)
	@param yscale: Adjust the speed of position movements in Y axis (forwards and backwards)
	@param zscale: Adjust the speed of position movements in Z axis (going up and down)
	@param buttons: Rearrange the button mappings used internally, default is 0,1,2,3,4,5
	@param keystrokes: Generate keyboard events if the buttons are pressed, None means to do nothing
	@param oriscale: Adjust the speed of orientation movements
	@param oriSteer: Makes left and right joystick movements rotate the orientation left and right
	@param walkingMode: Fixes the user to ground level
	"""
	def __init__(self, controller, tracker=None, speed=0.02, xscale=1.0, yscale=1.0, zscale=1.0, oriscale=1.0, oriSteer=True, walkingMode=True, keystrokes=[None,None,None,None,'r',None], buttonReset=4, buttonForward=1, buttonReverse=None, buttonFist=0, buttonUp=2, buttonDown=3, buttonPinch=5):

		# Initialize the base classes
		viz.EventClass.__init__(self)
		viz.EventClass.callback(self,viz.UPDATE_EVENT,self.refresh)
		VUTrackerGeneric.__init__(self)

		# Store all the inputs supplied
		self.controller = controller
		self.tracker = tracker
		self.xscale = xscale * speed
		self.yscale = yscale * speed
		self.zscale = zscale * speed
		self.speed  = speed
		self.oriSteer = oriSteer
		self.orimult = oriscale / self.xscale # Calculate rotation rate relative to position rate
		self.walkingMode = walkingMode
		self.lastTime = -1 # Keep track of how long ago the last update was
		self.keystrokes = keystrokes
		self.buttonReset = buttonReset
		self.buttonForward = buttonForward
		self.buttonReverse = buttonReverse
		self.buttonFist = buttonFist
		self.buttonUp = buttonUp
		self.buttonDown = buttonDown
		self.buttonPinch = buttonPinch
		self.keystrokes_last = []
		for each in self.keystrokes:
			self.keystrokes_last.append(False)

		# State tracking for the hands
		self.handsensor = hand.MultiInputSensor()
		self.lastPinch = False
		self.lastFist = False

		# Store a tracking device that is emitted by this object
		self.posTrk = viz.addGroup()
		self.saveTracker (self.posTrk)
		self.enabled = True

	def setActive(self, state):
		"""Set the state of the flying code"""
		self.enabled = state

	def enable(self):
		"""Enable the flying code, allowing new movements"""
		self.enabled = True

	def disable(self):
		"""Disable the flying code, preventing new movements"""
		self.enabled = False

	def toggleActive(self):
		"""Toggles the active state of the flyer, to disable/enable it"""
		if self.enabled:
			self.enabled = False
		else:
			self.enabled = True

	def getController(self):
		"""Returns back a handle to the joystick controlling this object"""
		return self.controller

	def getOrientation(self):
		"""Returns back a handle to the orientation input controlling this object"""
		return self.tracker

	def getHandSensor(self):
		"""Returns back a handle to the hand sensor which this object generates"""
		return self.handsensor

	def reset(self):
		"""Reset the tracker contained within the object"""
		self.posTrk.setPosition(0,0,0)
		self.posTrk.setEuler(0,0,0)

	def refresh(self,e):
		# We need to calculate how much to scale everything by. Typically the software
		# should run at 60 fps, and so if this is the case, the tick will vary by 1/60,
		# and the scale will end up being self.xscale. If the frame rate drops to 30, then
		# the scale should increase to 2 to compensate for it. So flying should always run
		# at a constant speed no matter what the frame rate is.
		newtick = viz.tick()
		if self.lastTime < 0:
			self.lastTime = newtick
			xscale = self.xscale
			yscale = self.yscale
		else:
			diff = viz.tick() - self.lastTime
			xscale = diff * 60 * self.xscale
			yscale = diff * 60 * self.yscale
			self.lastTime = newtick

		# Now take the joystick data and calculate some initial values
		xjoy = self.controller.getX()
		yjoy = self.controller.getY()
		zjoy = 0.0
		nowFist = False
		nowPinch = False

		keynum = 0
		while keynum < len(self.keystrokes):
			if self.keystrokes[keynum] is not None:
				if self.controller.isButtonDown(keynum) and self.keystrokes_last[keynum] is False:
					viz.logNotice("Generating key press %s for button %d" % (self.keystrokes[keynum], keynum))
					viz.sendEvent(viz.KEYDOWN_EVENT, self.keystrokes[keynum])
					self.keystrokes_last[keynum] = True
				elif not self.controller.isButtonDown(keynum) and self.keystrokes_last[keynum] is True:
					viz.logNotice("Generating key release %s for button %d" % (self.keystrokes[keynum], keynum))
					viz.sendEvent(viz.KEYUP_EVENT, self.keystrokes[keynum])
					self.keystrokes_last[keynum] = False
			keynum += 1

		# If the object is disabled, do it now, if someone has written code to use the buttons or keyboard
		# to toggle the state on and off, it has been processed just above
		if not self.enabled:
			return

		if self.buttonReset is not None and self.controller.isButtonDown(self.buttonReset):
			self.reset()

		if self.buttonForward is not None and self.controller.isButtonDown(self.buttonForward):
			xjoy = 0.0
			yjoy = -1 # This might look strange, but all the joysticks emit -1 for forwards, +1 for backwards, so do the same here
		if self.buttonReverse is not None and self.controller.isButtonDown(self.buttonReverse):
			xjoy = 0.0
			yjoy = +1 # See above comment for forwards mode

		if self.buttonFist is not None and self.controller.isButtonDown(self.buttonFist):
			nowFist = True

		if self.buttonUp is not None and self.controller.isButtonDown(self.buttonUp):
			zjoy = +1.0
		if self.buttonDown is not None and self.controller.isButtonDown(self.buttonDown):
			zjoy = -1.0

		if self.buttonPinch is not None and self.controller.isButtonDown(self.buttonPinch):
			nowPinch = True

		# Change the position and orientation of the final output tracker based on the joystick movements
		if self.oriSteer:
			# In this code, left and right joystick movements cause left and right orientation changes
			mdir = vizmat.Transform()
			if self.tracker is not None:
				mdir.setEuler(self.tracker.getEuler())
			mdir.preTrans([0.0, 0.0, -yjoy * yscale]) # Note yjoy needs to be inverted since push forward is -1
			flydir = mdir.getPosition()
			if self.walkingMode:
				flydir[1] = 0.0 # This line forces the flying to never go up or down
			self.posTrk.setPosition(flydir, viz.REL_LOCAL)
			self.posTrk.setEuler([xjoy * xscale * self.orimult,0,0], viz.REL_LOCAL)
		else:
			# In this code, we move around in world coordinates and do not change orientation
			mdir = vizmat.Transform()
			if self.tracker is not None:
				mdir.setEuler(self.tracker.getEuler())
			mdir.preTrans([xjoy * xscale, 0.0, -yjoy * yscale]) # Note yjoy needs to be inverted since push forward is -1
			flydir = mdir.getPosition()
			if self.walkingMode:
				flydir[1] = 0.0 # This line forces the flying to never go up or down
			self.posTrk.setPosition(flydir, viz.REL_LOCAL)

		# Now apply Z offsets in world coordinates, not the direction of the wand or the user
		self.posTrk.setPosition([0,zjoy*self.zscale,0], viz.REL_LOCAL)

		# Now deal with pinch and fist gestures, need to track state and execute callbacks
		if nowFist is not self.lastFist:
			if nowFist:
				self.handsensor.startFist()
			else:
				self.handsensor.endFist()
			self.lastFist = nowFist
		if nowPinch is not self.lastPinch:
			if nowPinch:
				self.handsensor.startPinch()
			else:
				self.handsensor.endPinch()
			self.lastPinch = nowPinch




class VUTrackerNumericKeypad(VUTrackerGeneric, viz.EventClass):
	""" NumericKeypad tracker class, which can be enabled on demand, and brings up a 2D window with its current status"""
	def __init__(self, startpos=[0,0,0], starteuler=[0,0,0], activekey=viz.KEY_SCROLL_LOCK):
		VUTrackerGeneric.__init__(self)
		viz.EventClass.__init__(self)
		self.kbtrk_state = 1						   # Set up the pop up dialog for when the tracker is enabled
		self.kbtrk_msg = vizinfo.add('')
		self.kbtrk_msg.title ('Keyboard Tracker')
		self.kbtrk_msg.drag (1)
		self.kbtrk_msg.visible (0)
		self.kbtrk_msg.translate (0.01, 0.02)
		self.kbtrk_msg.scale (0.75, 0.75)
		self.kbtrk_msg.alignment (vizinfo.LOWER_LEFT)
		self.kbtrk_msg.bgcolor     (0, 0.75, 0, 0.4)
		self.kbtrk_msg.titlebgcolor(0,  0.5, 0, 0.4)
		self.kbtrk_msg.bordercolor (0,  0.5, 0, 0.4)
		viz.EventClass.callback(self, viz.KEYDOWN_EVENT, self.onkeydown, priority=viz.PRIORITY_CAMERA_HANDLER-1) # Need to be at a higher priority than other vizcam code
		viz.EventClass.callback(self, viz.KEYUP_EVENT,   self.onkeyup,   priority=viz.PRIORITY_CAMERA_HANDLER-1)
		viz.EventClass.callback(self, viz.UPDATE_EVENT,  self.refreshGUI)
		self.keylist = [ viz.KEY_UP, viz.KEY_DOWN, viz.KEY_LEFT, viz.KEY_RIGHT, viz.KEY_PAGE_UP, viz.KEY_PAGE_DOWN, viz.KEY_INSERT, viz.KEY_DELETE, viz.KEY_HOME, viz.KEY_END ]

		# Create the vizcam KeyboardCamera handler
		import vizcam
		vizcam.AUTO_REGISTER = 0
		self.cam = vizcam.KeyboardCamera(forward=viz.KEY_UP, backward=viz.KEY_DOWN, left=viz.KEY_LEFT, right=viz.KEY_RIGHT, up=viz.KEY_PAGE_UP, down=viz.KEY_PAGE_DOWN, turnLeft=viz.KEY_INSERT, turnRight=viz.KEY_DELETE, pitchDown=viz.KEY_HOME, pitchUp=viz.KEY_END, rollRight=None, rollLeft=None)
		self.cam.setTurnMode(turnLeft=viz.REL_PARENT, turnRight=viz.REL_PARENT) # Left and right turns are done in world coordinates so it makes sense to the user

		# Now turn it into a real tracker
		self.rawTrk = VUTrackerVirtual._CameraTracker(self.cam)
		self.defaultpos = startpos
		self.defaulteuler = starteuler

		# There is a bug in vizcam where getMatrix, getQuat, and getEuler will not return anything, but this fixes it
		posTrk = viz.addGroup()
		viz.link (self.rawTrk, posTrk)
		self.saveTracker (posTrk)

		# Reset the tracker now
		self.resetDefaults ()

		# Set callbacks so it is only active when the control key toggles it on/off
		self.toggleKeyboardTracker()
		vizact.onkeydown (activekey, self.toggleKeyboardTracker)


	def toggleKeyboardTracker(self):
		"""Toggle whether the tracker is actively listening for key press events"""
		if self.kbtrk_state == 0:
			self.kbtrk_state = 1
		else:
			self.kbtrk_state = 0
		# print 'Setting keyboard offset tracker to %d' % self.kbtrk_state
		self.kbtrk_msg.visible (self.kbtrk_state)
		self.rawTrk.manager.getHandler().sensitivity (self.kbtrk_state,self.kbtrk_state)

	def getActive(self):
		"""Returns back if this object is active or idling in the background"""
		return self.kbtrk_state

	def refreshGUI(self, num):
		kb_pos_str = 'XYZ(%.2f,%.2f,%.2f)' % tuple(self.getPosition())
		kb_ori_str = 'HPR(%.0f,%.0f,%.0f)' % tuple(self.getEuler())
		self.kbtrk_msg.message ('Status: Active\nKbPos: %s\nKbOri: %s\n' % (kb_pos_str, kb_ori_str))

	def onkeyup(self, key):
		# Create a fake event
		ev = viz.Event()
		ev.key = key

		# Always process the release of a key so the state is maintained properly
		if key in self.keylist:
			self.cam._camKeyUp(ev)
			if self.kbtrk_state:
				return True # Tracker active, eat up the key
			else:
				return False # Tracker not active, so pass the key on
		if key == viz.KEY_KP_5 and self.kbtrk_state:
			return True # Tracker active, eat up the key

		# If we made it here, the key was not used, so pass it on
		return False

	def onkeydown(self, key):
		# Create a fake event
		ev = viz.Event()
		ev.key = key

		# If we are not active, then pass the key onto other code for processing
		if not self.kbtrk_state:
			return False

		# Look for keys we are interested in, eat them up, and then pass them on to the KeyboardCamera
		if key == viz.KEY_KP_5:
			self.resetDefaults() # When numeric keypad 5 is pressed, reset the tracker to all zeros
			return True
		if key in self.keylist:
			self.cam._camKeyDown(ev)
			return True

		# If we made it here, the key was not used, so pass it on
		return False

	def resetDefaults (self):
		"""Reset the tracker back to the default position and orientation"""
		self.rawTrk.setPosition (self.defaultpos)
		self.rawTrk.setEuler (self.defaulteuler)

	def getCamera (self):
		"""Return back the raw camera object, similar to how VUTrackerVirtual works"""
		return self.cam



import math
class VUTrackerPath(VUTrackerGeneric, viz.EventClass):
	"""
	Tracker abstraction that implements the ability to follow paths
	@param type: "circle" follows a circle path, "updown" goes up and down
	@param startpos: Default starting position
	@param starteuler: Default starting orientation
	@param timeoffset: Extra offset to apply to the time used
	"""
	def __init__(self, type="circle", startpos=[0,0,0], starteuler=[0,0,0], timeoffset=0):
		VUTrackerGeneric.__init__(self)
		viz.EventClass.__init__(self)
		self.timeoffset = timeoffset
		self.type = type

		self.posTrk = viz.addGroup()
		self.posTrk.setPosition (startpos)
		self.posTrk.setEuler (starteuler)
		self.startTrk = self.posTrk
		self.saveTracker (self.posTrk)

		viz.EventClass.callback(self,viz.TIMER_EVENT,self.refresh)  # Create a callback to our own event class function
		self.starttimer(0,0,viz.PERPETUAL)           # Refresh this class every frame

	def refresh(self, num):
		if self.type == "circle":
			SPEED = 0.5
			RADIUS = 1
			t = (viz.tick() + self.timeoffset) * SPEED
			newX = -math.cos(t) * RADIUS
			newZ = math.sin(t) * RADIUS
			self.posTrk.translate(newX, 0, newZ)
			self.posTrk.setAxisAngle(0,1,0, viz.degrees(t))
		elif self.type == "updown":
			SCALE = 1.0
			SPEED = 0.5
			pos = self.startTrk.getPosition()
			value = viz.tick() * SPEED
			value = value - math.floor (value) # Value is from 0..1
			if value > 0.5:
				value = 1.0 - value # If above 0.5 then go down instead
			value = value * 2 # Rescale so it is between 0..1
			pos[1] = value * SCALE
			self.posTrk.setPosition (pos)




class VUTrackerMouse2D(viz.EventClass, VUTrackerGeneric):
	"""
	Tracker interface that turns a 2D mouse into a 3D tracking device. Note that this object can only be
	used as an output tracker, you do not want to transform it using any of the offsets that can be applied.
	@param window: The window to use to get 2D coordinates for the mouse
	@param handDistance: The default distance to place the hand away from the user
	@param scrollDistance: The distance to move when the scroll wheel is adjusted
	@param ofs2D: Apply an offset to the 2D value of the cursor in the window, useful when using two hands on the same mouse cursor
	@param fixed2D: Supply a 2D value to return instead of using the mouse, set to None to actually poll the mouse
	"""
	def __init__(self, window=viz.MainWindow, handDistance=1.0, scrollDistance=0.25, ofs2D=[0,0], fixed2D=None):
		# Initialise the class to refresh for each frame, note that the mouse is only calculated after
		# the frame is rendered, so the hand is always one frame behind
		viz.EventClass.__init__(self)
		viz.EventClass.callback(self,viz.UPDATE_EVENT,self.onUpdate,priority=viz.PRIORITY_FIRST_UPDATE)

		# Configure the distance that the hand is away from the viewpoint
		self.handDistance = handDistance
		vizact.onwheeldown(self.scroll,-scrollDistance)
		vizact.onwheelup(self.scroll,scrollDistance)

		# Initialize a tracking device so that this object is vizuniverse compatible
		VUTrackerGeneric.__init__(self)
		self.posTrk = viz.addGroup()
		self.saveTracker (self.posTrk)
		self.window = window
		self.ofs2D = ofs2D
		self.fixed2D = fixed2D

	def scroll(self,num):
		self.handDistance += num

	def onUpdate(self,e):
		if self.fixed2D is None:
			sPos = viz.Mouse.getPosition()
		else:
			sPos = self.fixed2D
		sPos[0] += self.ofs2D[0]
		sPos[1] += self.ofs2D[1]
		line = self.window.screentoworld(sPos)
		line.length = self.handDistance
		self.posTrk.setPosition (line.end)
		# print "2D(%.2f,%.2f) -> 3D(%.2f,%.2f,%.2f)" % (sPos[0], sPos[1], line.end[0], line.end[1], line.end[2])



def _VUTrackerVirtual_move(self, x, y, z, mask = None):
	"""Helper function that we use inside VizView to force it to not allow the camera driver to change the height"""
	T = vizmat.Transform()
	T.makeQuat(self.getQuat())
	T.preTrans(x, y, z)
	pos = T.getTrans() # Find position shift in world coordinates
	pos[1] = 0.0 # Suppress Y change and update the view position
	self.oldSetPosition(pos, viz.REL_GLOBAL)

def _VUTrackerVirtual_setPosition(self, vec, mode):
	"""Helper function that we use inside VizView to force it to not allow the camera driver to change the height"""
	if mode == viz.REL_PARENT:
		pos = vec[:]
		pos[1] = 0.0 # Suppress Y change and update the view position
		self.oldSetPosition(pos, viz.REL_GLOBAL)
	elif mode == viz.REL_LOCAL:
		T = vizmat.Transform()
		T.makeQuat(self.getQuat())
		T.preTrans(vec)
		pos = T.getTrans() # Find position shift in world coordinates
		pos[1] = 0.0
		self.oldSetPosition(pos, viz.REL_GLOBAL)
	else:
		FatalError("This code does not support mode %d, only viz.REL_PARENT and viz.REL_LOCAL")


class VUTrackerVirtual(VUTrackerGeneric, viz.EventClass):
	"""
	Tracker abstraction for various combinations of keyboard and mouse inputs
	@parem type: MouseKeyboard, KeyboardMouse, Mouse, Keyboard, None
	@param startpos: Default starting position
	@param starteuler: Default starting orientation
	"""
	def __init__(self, type = "None", startpos=[0,0,0], starteuler=[0,0,0], fixedHeight=False, priority=viz.PRIORITY_CAMERA_HANDLER+1):
		VUTrackerGeneric.__init__(self)
		self.type = type

		import vizcam
		vizcam.AUTO_REGISTER = 0

		if type == "MouseKeyboard" or type == "KeyboardMouse":
			viz.logNotice('Using mouse/keyboard input device for tracking')
			self.cam = vizcam.FlyNavigate()
			posTrk = self._CameraTracker(self.cam)
		elif type == "Mouse":
			viz.logNotice('Using mouse input device for tracking')
			self.cam = vizcam.PanoramaNavigate()
			posTrk = self._CameraTracker(self.cam)
		elif type == "Keyboard":
			viz.logNotice('Using keyboard input device for tracking')
			self.cam = vizcam.KeyboardCamera(forward=viz.KEY_UP, backward=viz.KEY_DOWN, turnLeft=viz.KEY_LEFT, turnRight=viz.KEY_RIGHT, up=viz.KEY_PAGE_UP, down=viz.KEY_PAGE_DOWN, left=viz.KEY_INSERT, right=viz.KEY_DELETE, pitchDown=viz.KEY_HOME, pitchUp=viz.KEY_END, rollLeft=None, rollRight=None)
			posTrk = self._CameraTracker(self.cam)
			self.cam.setTurnMode(turnLeft=viz.REL_PARENT, turnRight=viz.REL_PARENT) # Left and right turns are done in world coordinates so it makes sense to the user
		elif type == "MousePivot":
			viz.logNotice('Using mouse input device with pivot navigation')
			self.cam = vizcam.PivotNavigate() # Currently this does not seem to look at the origin, needs to be fixed
			posTrk = self._CameraTracker(self.cam)
		elif type == "Default":
			viz.logNotice('Using Vizard default navigation')
			self.cam = vizcam.DefaultNavigate()
			posTrk = self._CameraTracker(self.cam)
		elif type == "None":
			# print 'Using empty tracking node'
			posTrk = viz.addGroup()
			self.cam = None
		else:
			viz.logNotice('Using fixed group node for tracking with unknown type %s' % type)
			posTrk = viz.addGroup()
			self.cam = None

		posTrk.setPosition (startpos)
		posTrk.setEuler (starteuler)

		# There is a bug in vizcam where getMatrix, getQuat, and getEuler will not return anything, but this fixes it
		fixPosTrk = viz.addGroup()
		viz.link (posTrk, fixPosTrk)
		self.saveTracker (fixPosTrk)

		# If fixedHeight mode is on then we need to fix the height to the supplied startpos Y value
		if fixedHeight:
			posTrk.oldmove = posTrk.move
			posTrk.oldSetPosition = posTrk.setPosition
			viz.upgradeInstance(posTrk, "move", _VUTrackerVirtual_move, override=1)
			viz.upgradeInstance(posTrk, "setPosition", _VUTrackerVirtual_setPosition, override=1)

		self.collide_view_ptr = posTrk # Save a reference to the raw viewpoint so we can use it for collision detection hacks
		self.collide_startpos = startpos # Save the height of the tracker so we can use it for the eye height later on
		self.collide_state = False

	def _CameraTracker(handler):
		"""Function needed to take a Vizard camera driver and make it a valid tracker"""
		import vizcam
		view = viz.addView() # Needed internally here, but not exposed to other code
		view.eyeheight(0)
		view.collision(viz.OFF)
		man = vizcam.Manager(view=view,handler=handler,priority=viz.PRIORITY_PLUGINS)
		view.manager = man
		return view
	_CameraTracker = staticmethod(_CameraTracker)

	def getCamera(self):
		"""Returns back a handle to the vizcam object if one was created in here, otherwise returns None"""
		return self.cam

	def getInputType(self):
		return self.type

	def setCollision(self, state=True, stepsize=0.5):
		"""Special method that allows these kinds of trackers to perform proper collision detection so you can climb up steps and stop at walls"""
		if self.collide_state == state:
			# Do nothing because we are already in the desired state
			return
		self.collide_state = state

		if state == True:
			# Set the eyeheight of the tracker so it is above ground level, allows the step climbing to work properly
			self.collide_view_ptr.eyeheight (self.collide_startpos[1])

			# Note that you cannot do getPosition() on a view, it just doesn't do anything, so we reset back to the startpos for this
			newpos = self.collide_startpos[:]
			newpos[1] = 0
			self.getInput().setPosition(newpos)

			# Now enable collision detection
			self.collide_view_ptr.collision(viz.ON)
			self.collide_view_ptr.stepsize(stepsize)

			viz.logNotice("Enabling collision detection for VUTrackerVirtual, stepsize=%f, eyeheight=%f, newpos=%s" % (stepsize, self.collide_startpos[1], newpos))
		else:
			# Set the eyeheight of the tracker so it is back at zero, where is is by default
			self.collide_view_ptr.eyeheight (0)

			# Note that you cannot do getPosition() on a view, it just doesn't do anything, so we reset back to the startpos for this
			self.getInput().setPosition(self.collide_startpos)

			# Now disable collision detection
			self.collide_view_ptr.collision(viz.OFF)

			viz.logNotice("Disabling collision detection for VUTrackerVirtual, stepsize=%f, eyeheight=%f, newpos=%s" % (stepsize, 0.0, self.collide_startpos))




class VUWatchdog(viz.EventClass):
	"""
	This class prints out a message every few minutes with a timestamp so we can log how the process is running.
	It helps us to determine when a crash was and how long an application was running for
	"""
	def __init__(self, timeout):
		viz.EventClass.__init__(self)
		self.callback (viz.TIMER_EVENT, self.refresh)
		self.starttimer(0,timeout,viz.PERPETUAL)

	def refresh(self, num):
		import time
		sec = viz.getFrameTime()
		h = sec / 3600
		sec -= int(h) * 3600
		m = sec / 60
		sec -= int(m) * 60
		viz.logNotice("Watchdog Timer: %s - %.2dh%.2dm%.2ds since startup" % (time.ctime(time.time()), h, m, sec))




class VUDetectMotion(viz.EventClass):
	"""
	This class can be used to take in a node3d object, and determine if it is moving or not
	If it detects movement, it will call destcallback.visible(viz.ON), and if it detects no movement for
	a certain timeout period then it will call destcallback.visible(viz.OFF). It can also call methods
	that you can override by extending the class as another option, override the state method for this.
	@param node: The 3D object to monitor the motion of
	@param timeout: Amount of time in seconds before a timeout can occur
	@param posthresh: Minimum movement change required to count as a movement
	@param orithresh: Minimum angle change required to count as a movement
	@param cb: Callback to execute with viz.ON when movement is detected, making the object visible
	@param invcb: Callback to execute with viz.OFF when movement is not detected, hiding the object
	"""
	def __init__(self, node, timeout, posthresh=0, orithresh=0, cb=None, invcb=None):
		viz.EventClass.__init__(self) # Initialize the base class
		self.cb = cb
		self.invcb = invcb
		self.posthresh = posthresh
		self.orithresh = orithresh
		self.timeout = timeout
		self.node = node
		self.resetOn() # Reset the object internals
		self.callback(viz.TIMER_EVENT, self.refresh) # Create a callback to our own event class function
		self.starttimer(0,0,viz.PERPETUAL) # Start a perpetual timer for this event class every 0 seconds = refresh rate

	def reset(self):
		self.resetOn()

	def enable(self):
		self.enabled = True

	def disable(self):
		self.enabled = False

	def resetOn(self):
		"""Call this method to reset this class to the current time and position"""
		self.lastPos = viz.Vector (self.node.getPosition(viz.ABS_GLOBAL)) # Get the position and orientation of the object
		self.lastOri = viz.Vector (self.node.getEuler(viz.ABS_GLOBAL))
		self.lastTime = viz.getFrameTime() # Get the current time
		self.state(viz.ON) # By default we are on
		self.stateval = viz.ON
		self.enabled = True # Flag indicating if we should allow state changes

	def resetOff(self):
		"""Call this method to reset the class so that the timeout occured a long time ago, forcing it to activate immediately"""
		self.lastPos = viz.Vector (self.node.getPosition(viz.ABS_GLOBAL))
		self.lastOri = viz.Vector (self.node.getEuler(viz.ABS_GLOBAL))
		self.lastTime = -self.timeout # Set a time a long time ago to force this to immediately activate
		self.state(viz.OFF)
		self.stateval = viz.OFF

	def state(self, set):
		if self.cb is not None:
			self.cb.visible(set)
		if self.invcb is not None:
			invset = set
			invset ^= 1
			self.invcb.visible(invset)

	def refresh(self, num):
		# Have we moved position since last time?
		posdist = (self.lastPos - self.node.getPosition(viz.ABS_GLOBAL)).length()
		oridist = (self.lastOri - self.node.getEuler(viz.ABS_GLOBAL)).length()
		if self.posthresh > 0 and posdist > self.posthresh:
			# Yes, we moved, so lets update our stats
			self.lastPos = viz.Vector(self.node.getPosition(viz.ABS_GLOBAL))
			self.lastTime = viz.getFrameTime()
			# Activate ON if necessary
			if self.stateval == viz.OFF and self.enabled:
				self.state (viz.ON)
				self.stateval = viz.ON
		elif self.orithresh > 0 and oridist > self.orithresh:
			self.lastOri = viz.Vector(self.node.getEuler(viz.ABS_GLOBAL))
			self.lastTime = viz.getFrameTime()
			if self.stateval == viz.OFF and self.enabled:
				self.state (viz.ON)
				self.stateval = viz.ON
		else:
			# No we did not move, have we exceeded the timeout?
			if (viz.getFrameTime() - self.timeout) > self.lastTime:
				# Timeout has been exceeded, send an OFF message
				if self.enabled:
					self.state (viz.OFF)
					self.stateval = viz.OFF
				self.lastTime = viz.getFrameTime()




# There are two types of priority values within Vizard. If you do viz.link(priority=X), then the event
# will be scheduled with vizact.onupdate(viz.PRIORITY_LINKS). The priority=X value is only useful for
# organizing the priorities of all links that are executed at PRIORITY_LINKS. If you do an onupdate()
# then you can specify exactly when the link will execute relative to all other Vizard events.
# So we do all of our viz.link's manually, and we do them early, so that if user code uses viz.link
# to attach to our trackers or objects, everything should work properly

PRIORITY_LINKS_BASE              = viz.PRIORITY_LINKS - 15	# Enough room to fit two trackers in that depend on each other

PRIORITY_LINKS_TRACKER           = PRIORITY_LINKS_BASE+0	# Priority for processing tracking data to internal link node
PRIORITY_LINKS_TRACKER_SECOND    = PRIORITY_LINKS_BASE+1	# Priority for second stage processing to generate final tracker position

# These define the various stages that we perform to move avatars and so forth around
PRIORITY_LINKS_POST_AVATAR       = PRIORITY_LINKS_BASE+2	# Priority to move the avatar into position
PRIORITY_LINKS_POST_LOOKAT       = PRIORITY_LINKS_BASE+3	# Priority to adjust any lookat parameters for the head
PRIORITY_LINKS_POST_VIEWPOINT    = PRIORITY_LINKS_BASE+4	# Priority to adjust the viewpoint to match the tracker/avatar
PRIORITY_LINKS_POST_VIEWOVERRIDE = PRIORITY_LINKS_BASE+5	# Priority to override the viewpoint for auto-fly mode

PRIORITY_LINKS_POST_SKIP         = 6						# Priority you need to add if you want to make one composite dependent on another, like with a CAVE




class VUAvatarGeneric(object):
	"""
	This is a generic base class for representing an avatar in vizuniverse. All avatars and composites use this base class.
	@param obj3d: object to use as the avatar
	@param seeself: controls if the viewer can see the avatar as their own body
	"""
	def __init__(self, obj3d, seeself):
		self.obj3d = obj3d
		self.seeself = seeself

	def visible(self, set):
		"""Change the visibility of the avatar"""
		self.obj3d.visible(set)

	def getSeeSelf(self):
		"""Return back the flag that determines if the avatar should be able to see its own body if it looks down"""
		return self.seeself

	def getHeadBone(self):
		"""Return a reference to the head bone of the object, in this case it is the same as the object itself"""
		return self.obj3d

	def getBodyBone(self):
		"""Return a reference to the body bone of the object, in some cases it is the same as the object itself"""
		return self.obj3d

	def getBone(self, name):
		"""Look up bone names from the avatar, but by default just return back the object if this is not available"""
		return self.obj3d

	def getRawAvatar(self):
		"""Get a reference to the raw avatar object we are storing, this is what was originally passed in during object initialization"""
		return self.obj3d



class VUAvatarSimple(VUAvatarGeneric):
	"""
	Attach a simple object to a tracker node, the object will be slaved directly 1:1, useful for heads, eyeballs, etc
	@param tracker:  input which controls how the avatar moves around
	@param obj3d:    simple object to use as the avatar
	@param seeself:  controls if the viewer can see the avatar as their own body
	@param priority: controls the priority of when the internal link is updated (defaults to PRIORITY_LINKS_POST_AVATAR)
	"""
	def __init__(self, tracker, obj3d, seeself=True, priority=PRIORITY_LINKS_POST_AVATAR):
		VUAvatarGeneric.__init__(self, obj3d, seeself=seeself)
		self.link = viz.link (tracker, obj3d, enabled=False)
		vizact.onupdate (priority, self.link.update)
		self.link.preTrans ([0,0,-0.1]) # Try to move the object back just a little in case the object exactly intersects the origin, makes the viewpoint work properly


import steve
class VUAvatarSteve(VUAvatarGeneric):
	"""
	Create and attach a STEVE object to a tracker node. This code deals with moving him around properly, which is important since it is a multi-part object

	@param tracker:  input which controls how the avatar moves around
	@param offset:   controls how much the Steve avatar is shifted relative to the tracker, if this is zero then it is inside the neck
	@param priority: controls the priority of when the internal link is updated (defaults to PRIORITY_LINKS_POST_AVATAR)
	@param seeself:  controls if the viewer can see the avatar as their own body
	@param bodycolor:    set the Steve body color
	@param eyecolor:     set the Steve eye color
	@param outlinecolor: set the Steve outline color
	@param shadecolor:   set the Steve shade color
	"""
	def __init__(self, tracker, offset=[0,-0.2,-0.2], priority=PRIORITY_LINKS_POST_AVATAR, seeself=True, bodycolor=None, eyecolor=None, outlinecolor=None, shadecolor=None):
		# Create the Steve avatar
		self.steve = steve.Steve()

		# Now pass in self.steve, note that this does not emit a usable linkable to find the location, just like an avatar, so you need to call getHeadBone()
		VUAvatarGeneric.__init__(self, self.steve, seeself=seeself)

		# Create a temporary node where we can apply an offset to, the Steve object has the viewpoint in the neck, which is not what I want
		self.shifted = viz.addGroup()
		self.link = viz.link (tracker, self.shifted, enabled=False)
		vizact.onupdate (priority, self.link.update)
		self.link.preTrans (offset) # Put the view in a place so we can't see our own head

		# Now add the Steve avatar, which uses the shifted tracker so we can't see the head
		self.steve.setTracker (self.shifted, priority=priority+1) # One higher than the link, so that way the avatar gets the latest updates
		if bodycolor is not None:
			self.steve.setBodyColor (bodycolor)
		if eyecolor is not None:
			self.steve.setEyeColor (eyecolor)
		if outlinecolor is not None:
			self.steve.setOutlineColor (outlinecolor)
		if shadecolor is not None:
			self.steve.setShadeColor (shadecolor)

	def getHeadBone(self):
		"""
		The steve object cannot be used to get the location, and does not move with setTracker updates
		So we need to use steve.head or steve.body if we want to get the location of these parts
		"""
		return self.steve.head

	def getBodyBone(self):
		""" Return a reference to the body component of the Steve avatar """
		return self.steve.body


class VUAvatarFixedBody(VUAvatarGeneric, viz.EventClass):
	"""
	Attach an avatar to the tracker node, but do not allow the avatar to go below ground level because that would be weird, also
	we can force the rotations to look nice in case the tracker does something unexpected

	@param tracker:     input which controls how the avatar moves around
	@param avatar:      existing avatar object which this code will work with
	@param groundlevel: if this is True, the avatar will always be forced so the feet are on the ground, height of the tracker is ignored
	@param seeself:     controls if the viewer can see the avatar as their own body
	@param nicerotate:  fix up the head rotation so it looks sane no matter what the tracker orientation is
	@param priority:    controls the priority of when the internal link is updated (defaults to PRIORITY_LINKS_POST_AVATAR)
	"""
	def __init__(self, tracker, avatar, groundlevel=False, seeself=True, nicerotate=True, priority=PRIORITY_LINKS_POST_AVATAR):
		VUAvatarGeneric.__init__(self, avatar, seeself=seeself)
		viz.EventClass.__init__(self)
		self.callback(viz.UPDATE_EVENT,self.refresh,priority=priority)

		self.groundlevel = groundlevel
		self.nicerotate = nicerotate
		self.tracker = tracker
		self.avatar = avatar
		self.bodybone = self.avatar.getBone('Bip01')
		self.bodybone.lock(recurse=1) # Lock all bones so we can control everything
		self.headbone = avatar.getBone('Bip01 Head')
		self.yofs = self.headbone.getPosition(viz.AVATAR_WORLD)[1]
		# We cannot set animations since they move the viewpoint, so we must do this all manually
		# Move the arms and hands so they are nicely lowered

		self.avatar.getBone('Bip01 R UpperArm').setEuler(0,0,-35,viz.AVATAR_WORLD)
		self.avatar.getBone('Bip01 L UpperArm').setEuler(0,0,35,viz.AVATAR_WORLD)

		# This is a different way of configuring the avatar, but we don't like the look of it
#		self.avatar.getBone('Bip01 R UpperArm').setEuler(-30,-10,-30,viz.AVATAR_WORLD)
#		self.avatar.getBone('Bip01 R Forearm').setEuler(-30,-10,-40,viz.AVATAR_WORLD)
#		#self.avatar.getBone('Bip01 R Hand').setEuler(-90,-10,-60,viz.AVATAR_WORLD)
#		self.avatar.getBone('Bip01 L UpperArm').setEuler(30,-10,30,viz.AVATAR_WORLD)
#		self.avatar.getBone('Bip01 L Forearm').setEuler(30,-10,40,viz.AVATAR_WORLD)
#		#self.avatar.getBone('Bip01 L Hand').setEuler(90,-10,60,viz.AVATAR_WORLD)


	def refresh(self, num):
		# We move the avatar to where the tracker is, but we play with the Y value to get the avatar where we want
		# If groundlevel is on, we force the avatar to the ground
		# Otherwise, we move the avatar but subtract the height of it so the head is at the right location
		pos = self.tracker.getPosition(viz.ABS_GLOBAL)
		if self.groundlevel is True:
			pos[1] = 0.0
		else:
			pos[1] = pos[1] - self.yofs
		[yaw,pitch,roll] = self.tracker.getEuler(viz.ABS_GLOBAL)
		self.avatar.setPosition (pos, viz.ABS_GLOBAL)
		self.avatar.setEuler (yaw, 0, 0, viz.ABS_GLOBAL)

		# Now make sure the orientation of the head is correct
		if self.nicerotate:
			# This version takes the avatar and prevents the head going into the chest, flipping back, or rolling too far
			[yaw,pitch,roll] = self.tracker.getEuler(viz.ABS_GLOBAL)
			if pitch > 30: # Limit the amount the user can look down
				pitch = 30
			elif pitch < -45: # Limit the amount the user can look up
				pitch = -45
			if roll > 30:
				roll = 30
			elif roll < -30:
				roll = -30
			self.headbone.setEuler ([yaw,pitch,roll], viz.AVATAR_WORLD)
		else:
			self.headbone.setEuler (self.tracker.getEuler(viz.ABS_GLOBAL), viz.AVATAR_WORLD)

	def getHeadBone(self):
		"""Return a reference to the avatar head bone"""
		return self.getBone('Bip01 Head')

	def getBodyBone(self):
		"""Return a reference to the avatar main body body"""
		return self.getBone('Bip01')

	def getBone(self, name):
		"""Return a named bone in the skeleton"""
		return self.avatar.getBone(name)

	def getRawAvatar(self):
		"""Return back the raw internal avatar object"""
		return self.avatar


class VUAvatarLiveCharacters(VUAvatarGeneric):
	"""
	This code is basically just a wrapper around a real avatar, which provides everything needed already
	@param avatar:  existing avatar object which this code will work with
	@param seeself: controls if the viewer can see the avatar as their own body
	"""
	def __init__(self, avatar, seeself=True):
		VUAvatarGeneric.__init__(self, avatar, seeself=seeself)
		self.avatar = avatar

	def getHeadBone(self):
		"""Return a reference to the avatar head bone"""
		return self.getBone('Bip01 Head')

	def getBodyBone(self):
		"""Return a reference to the avatar main body body"""
		return self.getBone('Bip01')

	def getBone(self, name):
		"""Return a named bone in the skeleton"""
		return self.avatar.getBone(name)

	def getRawAvatar(self):
		"""Return back the raw internal avatar object"""
		return self.avatar




class VUControlObjectFollowLookAt (viz.EventClass):
	"""
	This class takes an object, and makes it maintain a constant offset, and always "looking" at the target
	@param object: The object to work with
	@param target: The target that the object will be pointed at
	@param offset: The position offset for the object from the target
	@param priority: The priority that the lookat will be performed at, by default it is PRIORITY_LINKS_POST_LOOKAT
	"""
	def __init__(self, object, target, offset, priority=PRIORITY_LINKS_POST_LOOKAT):
		viz.EventClass.__init__(self)
		self.callback(viz.UPDATE_EVENT,self.refresh,priority=priority)
		self.object = object
		self.target = target
		self.offset = offset

	def refresh(self, num):
		"""Internal refresh function that implements the lookat"""
		self.object.setEuler (0,0,0)
		self.object.setPosition (self.target.getPosition(viz.ABS_GLOBAL))
		self.object.setPosition (self.offset, viz.REL_LOCAL)
		self.object.lookat (self.target.getPosition(viz.ABS_GLOBAL))




class VUControlObjectLookAt (viz.EventClass):
	"""
	This class takes an object, and changes the orientation so that it is always "looking" at the target
	@param object: The object to work with
	@param target: The target that the object will be pointed at
	@param priority: The priority that the lookat will be performed at, by default it is PRIORITY_LINKS_POST_LOOKAT
	"""
	def __init__(self, object, target, priority=PRIORITY_LINKS_POST_LOOKAT):
		viz.EventClass.__init__(self)
		self.callback(viz.UPDATE_EVENT,self.refresh,priority=priority)
		self.object = object
		self.target = target

	def refresh(self, num):
		"""Internal refresh function that implements the lookat"""
		# print "SIMPLE: OBJ = ", self.object.getPosition(viz.ABS_GLOBAL), " TGT = ", self.target.getPosition(viz.ABS_GLOBAL)
		self.object.lookat (self.target.getPosition(viz.ABS_GLOBAL))
		# print "EULER = ", self.object.getEuler()


class VUControlAvatarLookAt (VUControlObjectLookAt):
	"""
	This class takes an avatar, and changes the body and head orientation so that it "looks at" a target
	@param avatar: The avatar to work with
	@param target: The target that the head will look at, and the body will be steered at
	@param priority: The priority that the lookat will be performed at, by default it is PRIORITY_LINKS_POST_LOOKAT
	"""
	def __init__(self, avatar, target, priority=PRIORITY_LINKS_POST_LOOKAT):
		VUControlObjectLookAt.__init__ (self, object=avatar, target=target, priority=priority)
		self.target = target
		self.avatar = avatar
		self.head = self.avatar.getHeadBone()
		self.body = self.avatar.getBodyBone()
		# Avatars need different coordinate systems than normal objects, so detect what we are dealing with
		if isinstance(self.avatar.getRawAvatar(), viz.VizAvatar):
			self.body.lock(recurse=1) # Lock all bones so we can control everything, needed for avatar objects
			self.avmode = viz.AVATAR_WORLD # Use avatar world coordinates for all rotations
		else:
			self.avmode = viz.ABS_GLOBAL # Use standard global coordinates for normal objects and Steve objects
		self.temp = viz.addGroup()

	def refresh(self, num):
		"""Internal refresh function that implements the lookat for the necessary bones"""

		# The following technique may look strange, but is needed to make the lookat command work with viz.ABS_GLOBAL
		# Due to the complicated arrangement of the avatar bones and transforms, the lookat does not do what you expect
		self.temp.setPosition (self.head.getPosition(viz.ABS_GLOBAL))
		self.temp.lookat (self.target.getPosition(viz.ABS_GLOBAL))
		euler = self.temp.getEuler()
		self.head.setEuler(euler, self.avmode)
		if self.body is not self.head: # Apply separate body rotation if the head and body are not the same
			euler[1] = 0
			euler[2] = 0
			self.body.setEuler(euler, self.avmode)




class VUHandSensorMultiComposite(hand.MultiInputSensor):
	"""This code is now located in the MultiInputSensor class in hand.py"""




__addwincount = 0
def addVUVizWindow(**kw):
	"""
	Wrapper that looks similar to addWindow(), but we generate a VUVizWindow instead.
	We also set the default size and position so that it uses the entire display.
	Note that we reuse viz.MainWindow as the first window returned from this code.
	"""
	global __addwincount
	if __addwincount == 0:
		# If this is the first window created, we should use the existing viz.MainWindow so that
		# code written to use viz.MainWindow will still work, but other newer code gets a VUVizWindow
		win = VUVizWindow(0,**kw)
		__addwincount += 1
	else:
		# Allocate a new window similar to how the viz.addWindow() function works
		win = VUVizWindow(viz._ipcSend(viz._VIZ_ADDWINDOW,0,0,'',0.0,0.0,0.0,0.0),**kw)
		win.setSize(1,1) # Make sure new window uses the full display area
		win.setPosition(0,1)
		win.drawOrder(-1) # Make sure our windows are always in the background, new windows will therefore appear above
	return win

class VUVizWindow (viz.VizWindow):
	"""
	This is a wrapper around the VizWindow object. The standard object is write-only, and not all variables are retrievable.
	So we use this class for all our VizWindow objects, it is able to copy values to other objects as the values arrive, meaning
	there is no need for a timer refresh, and we only make changes when necessary.
	"""
	def __init__(self,id,*args,**kw):
		viz.VizWindow.__init__(self,id,*args,**kw)
		self.targets = []
		self.vo_matrix = None

	def copyVUVizWindow(self, win):
		"""Copy as much as possible of a VizWindow object, there is a lot of detail captured in this class"""
		self.position(win.getPosition())
		self.size(win.getSize())
		self.clip([win.getNearClip(),win.getFarClip()])
		self.fov(win.getVerticalFOV())
		self.viewpoint(win.getView())
		self.setClearMask(win.getClearMask())
		self.setCullMask(win.getCullMask())
		# clearcolor, order: Unsupported

		# We always copy VUVizWindow and not plain VizWindow objects, so we can always assume our custom variables will be there
		if win.vo_matrix is not None:
			self.setViewOffset(win.vo_matrix, win.vo_eye, win.vo_mode)

	def addTarget(self, targetwin):
		"""Attach other windows that we want to copy changes to"""
		self.targets.append(targetwin)


	# -- Methods we want to propagate to target windows --

	def setProjectionMatrix(self,*args,**kw):
		"""Wrapper function that copies over values that will be possibly updated in real-time"""
		viz.VizWindow.setProjectionMatrix(self,*args,**kw)
		for each in self.targets:
			each.setProjectionMatrix(*args,**kw)

	def fov(self,*args,**kw):
		"""Wrapper function that copies over values that will be possibly updated in real-time"""
		viz.VizWindow.fov(self,*args,**kw)
		for each in self.targets:
			each.fov(*args,**kw)

	def frustum(self,*args,**kw):
		"""
		Wrapper function that copies over values that will be possibly updated in real-time
		This function is called each frame by the vizcave script to update the CAVE walls based on the tracking device.
		"""
		viz.VizWindow.frustum(self,*args,**kw) # Pass all the arguments as supplied
		for each in self.targets:
			each.frustum(eye=viz.BOTH_EYE,*args) # Force viz.BOTH_EYE, because CAVEs are stereo and our target windows are mono

	def setViewOffset(self, matrix, eye=viz.BOTH_EYE, mode=viz.PRE_MULT):
		"""Wrapper function that copies over values that will be possibly updated in real-time"""
		viz.VizWindow.setViewOffset(self, matrix, eye=eye, mode=mode)
		# We store a local copy because we only see this once with vizcave, need it when we make clones
		self.vo_matrix = matrix
		self.vo_eye = eye
		self.vo_mode = mode
		for each in self.targets:
			each.setViewOffset(matrix, eye=eye, mode=mode)

	def ipdVector(self,*args,**kw):
		"""Wrapper function that copies over values that will be possibly updated in real-time"""
		viz.VizWindow.ipdVector(self,*args,**kw)
		for each in self.targets:
			each.ipdVector(*args,**kw)

	def setView(self,*args,**kw):
		"""Wrapper function that copies over values that will be possibly updated in real-time"""
		viz.VizWindow.setView(self,*args,**kw)
		for each in self.targets:
			each.setView(*args,**kw)


__addviewcount = 0
def addVUVizView(): # Do not support **kw because viz.MainView already exists
	"""
	Wrapper that looks similar to addVUVizWindow(), but for viewpoints instead.
	We don't use any wrapper classes here, but we do reuse viz.MainView so that the
	first viewpoint generated here will be the original viz.MainView object, this
	way any original Vizard code that uses viz.MainView will still work properly.
	"""
	global __addviewcount
	if __addviewcount == 0:
		# If this is the first view created, we should use the existing viz.MainView so that
		# code written to use viz.MainView will still work
		view = viz.MainView
		__addviewcount += 1
	else:
		# Allocate a new view
		view = viz.addView()
	# Always remove any height offsets and collision modes!
	view.eyeheight(0.0)
	view.collision(viz.OFF)
	return view




def VUFlip(xflip, yflip, window=None):
	"""
	Takes a window and applies a 2D flip in the X and/or Y directions. There are some projectors and displays
	that require an inverted image and the flip cannot be done in hardware. You cannot just flip the frustum
	or use the addWall() flip options because it will affect backface culling and not just the 2D output

	There are two ways of applying the flip. If you are using the seeself=False flag as is typical in a multi-user
	setup, you should NOT use the window option because shaders and seeself both use cull masks in an incompatible
	way. If you are in this scenario, you need to set window to None and flip the entire display output, and you
	cannot just flip a single image.

	@param xflip: boolean controlling flip in the X axis
	@param yflip: boolean controlling flip in the Y axis
	@param window: the window to affect with this operation, if None then do the whole display with an overlay window
	"""
	import vizpp
	if xflip:
		x = "1.0-"
	else:
		x = ""
	if yflip:
		y = "1.0-"
	else:
		y = ""
	flipShader = """
	uniform sampler2D vizpp_InputTex;
	void main()
	{
		vec2 texCoord = gl_TexCoord[0].st;
		gl_FragColor = texture2D(vizpp_InputTex, vec2(%sgl_TexCoord[0].s,%sgl_TexCoord[0].t));
	}
	""" % (x, y)
	if window is None:
		newwin = viz.addWindow(size=[1,1], pos=[0,1], view=viz.addView(scene=viz.addScene()))
		newwin.setClearMask(0)
		flipEffect = vizpp.ShaderEffect(frag=flipShader)
		vizpp.getEffectManager(window=newwin).setRenderBufferMode(vizpp.READ_FRAME_BUFFER)
		vizpp.addEffect(flipEffect,window=newwin)
		print "Implemented direct flip shader for (x=%s,y=%s) on entire display with new window %s" % (xflip, yflip, newwin)
	else:
		if window.getCullMask() != 8: # 8 is the default value, if different it means the user is probably using the seeself=True feature, which is incompatible
			FatalError("Cannot apply shader to window %s which already has non-default cull mask %d (not 8) applied, check if seeself is False" % (window, window.getCullMask()))
		flipEffect = vizpp.ShaderEffect(frag=flipShader)
		vizpp.addEffect(flipEffect, window=window)
		print "Implemented direct flip shader for (x=%s,y=%s) on window %s (note that this is not compatible with seeself=False avatars)" % (xflip, yflip, window)




class VUCompositeGeneric (object):
	"""
	This class takes in a series of raw tracking devices, and implements the ability to push them around
	together. This is useful because when using something like an elevator demo, the elevator needs to go
	up and down, moving the viewpoint, and the user avatar with it
	"""
	def __init__(self):
		# Composites store a name for themselves, and also a view type string. Both of them can be set to anything
		# that you want. However, the view type string is used to select from the view list that a script provides,
		# so the naming must match that.
		self.comp_name = ""
		self.comp_viewtype = VT_DEFAULT

		# We need to implement three extra nodes, which are manipulated both internally and by some Vizard code.
		# If the Vizard code wants to push the user around, like on a platform or an elevator, they need to
		# use origin_movable and they can adjust this or link to it or whatever. If the Vizard code wants to
		# reset the current position so that where the user is standing right now, that will be the origin
		# of the demo, then the resetXZ command can do that for you. Note that origin_node should never be pushed
		# around, because vizmultiscript assumes this is always left as 0,0,0 and only swaps out the parent
		# origin_movable node. So we don't provide a method to access the origin_node to standard Vizard code.
		self.origin_node = viz.addGroup ()
		self.origin_movable = viz.addGroup ()
		self.origin_node.parent(self.origin_movable)
		self.reset_node = viz.addGroup ()
		self.origin_fixed = False # If this flag is true then other code is not allowed to change the origin

		# We support the ability to drive things around using something like a set of keyboard trackers, but have an empty default
		self.driver_node_list = []

		# Defines and arrays that show what each node does
		self.HEAD  = 0
		self.LHAND = 1
		self.RHAND = 2
		self.LFOOT = 3
		self.RFOOT = 4
		self.HIP   = 5
		self.tracker_names  = [ "Head", "Left Hand", "Right Hand", "Left Foot", "Right Foot", "Hip" ]
		self.tracker_input  = [ None, None, None, None, None, None ] # These are actual 3D transforms useable by Vizard code
		self.tracker_output = [ None, None, None, None, None, None ] # Output 3D transforms useable by Vizard code
		self.driverlink_list= [ None, None, None, None, None, None ]
		self.pos_scale_list = [ None, None, None, None, None, None ]
		self.ori_scale_list = [ None, None, None, None, None, None ]
		self.dictionary = {} # Configure an empty dictionary of values that we keep references to in here

		# Initialize for no hands
		self.left_hand = None
		self.right_hand = None
		self.misc_hands = []

		# Initialize to use the default display configuration
		self.configDisplayCommands = ""

		# Other defaults needed
		self.overridelink = None

		# Set up keys that will handle changes in position scaling
		onkeydownspecial('`', self.setPosScale, [0,1,0])
		onkeydownspecial('q', self.setPosScale, [1,1,1])
		onkeydownspecial('w', self.setPosScale, [2,1,2])
		onkeydownspecial('e', self.setPosScale, [3,1,3])

	def getName(self):
		"""Return the name assigned to this composite object"""
		return self.comp_name

	def getViewType(self):
		"""Return the type of view object that this composite should try to use"""
		return self.comp_viewtype

	def getCompType(self):
		"""Return the name of the object type"""
		return "%s" % self

	def setName(self, name):
		"""Change the name of the composite object"""
		self.comp_name = name

	def setViewType(self, viewtype):
		"""Change the type of view that this composite should try to use"""
		self.comp_viewtype = viewtype

	def get(self, value):
		"""Return dictionary entry for this composite"""
		return self.dictionary[value]

	def getDebug(self):
		return "No debug information available\n"

	def isMovableFixed(self):
		"""Returns true if the movable node cannot be adjusted, typically used in situations like when a CAVE user is inside a CAVE"""
		return self.origin_fixed

	def _setMovableFixed(self, flag):
		"""Set this to true if you want to lock a movable node so it cannot be changed, like with a CAVE user node inside a CAVE"""
		self.origin_fixed = flag

	def getMovableNode(self):
		"""This method returns a reference to the origin parent, so that scripts can push around the user if desired"""
		par = self.origin_node.getParents()
		if len(par) is not 1:
			FatalError("Found an origin node with %d parents, but this should always be 1" % len(par))
		return par[0]

	def _setOriginParent(self, parent):
		"""Internal function you can use to change the parent, should not be used by normal Vizard programs"""
		if self.origin_fixed:
			FatalError("Cannot change the parent of an origin_node that has been configured to be fixed")
		if parent is None: # Deal with clearing the origin parent, make sure we set it to the original movable parent node
			self.origin_node.parent (self.origin_movable)
		elif parent is viz.WORLD:
			FatalError("Cannot change parent of an origin_node to being viz.WORLD, must be a valid VizNode")
		else:
			self.origin_node.parent (parent)

	def isMovableDefault(self):
		"""Returns True if the origin_node parent is origin_movable, ie, it is not modified by other code from the startup defaults"""
		return (self.getMovableNode() is self.origin_movable)

	def resetNodeClear(self):
		"""Clears out the reset node to the default identity matrix"""
		m = vizmat.Transform()
		self.reset_node.setMatrix (m)

	def resetNodeXYZ(self):
		"""Captures the current tracker and applies that to the reset node, making the current XYZ position the origin"""
		m = self.reset_output.getMatrix()
		minv = m.inverse()

		r = self.reset_node.getMatrix()
		r.postMult(minv)
		self.reset_node.setMatrix(r)

	def resetNodeXZ(self):
		"""Captures the current tracker and applies that to the reset node, making the current XZ position the origin, ignoring the Y height value"""
		pos = self.reset_output.getPosition()
		m = vizmat.Transform()
		m.setPosition (pos[0], 0, pos[2])
		minv = m.inverse()

		r = self.reset_node.getMatrix()
		r.postMult(minv)
		self.reset_node.setMatrix(r)

	def resetNodeXZH(self):
		"""Captures the current tracker and applies that to the reset node, making the current XZ position the origin, ignoring the Y height value, using heading as well"""
		pos = self.reset_output.getPosition()
		m1 = vizmat.Transform()
		m1.setPosition (pos[0], 0, pos[2])
		m1inv = m1.inverse()

		m2 = vizmat.Transform()
		m2.setEuler (self.reset_output.getEuler()[0], 0, 0)
		m2inv = m2.inverse()

		r = self.reset_node.getMatrix()
		r.postMult(m2inv)
		r.postMult(m1inv)
		self.reset_node.setMatrix(r)

	def addDriverNode(self, tracker):
		"""Add a VUTracker-type object to the list of driver nodes, these can be used to push around the final tracker. These are not active until finishTrackers() is called"""
		self.driver_node_list.append (tracker)

	def finishTrackers(self):
		"""This method should be called once all the storeTracker() and addDriverNode() commands have been made"""
		t = 0
		# Traverse all links, but skip those which are not defined (not all classes define all of them)
		while t < len(self.driverlink_list):
			i = 0
			if self.driverlink_list[t] is not None:
				# Reset the operators on each link in case this method has been called previously
				self.driverlink_list[t].reset(viz.RESET_OPERATORS)

				# Apply the reset node first to the driver link
				resetTrans  = self.driverlink_list[t].postMultLinkable (self.reset_node, mask=viz.LINK_POS)
				resetRotate = self.driverlink_list[t].preMultLinkable (self.reset_node, mask=viz.LINK_ORI)

				# For each driver in the list, we need to apply it to the link
				while i < len(self.driver_node_list):
					self.driverlink_list[t].postMultLinkable (self.driver_node_list[i], mask=viz.LINK_POS)
					self.driverlink_list[t].preMultLinkable  (self.driver_node_list[i], mask=viz.LINK_ORI)
					i = i + 1
			t = t + 1

	def setPosScale(self, scale=[1,1,1], id=None):
		"""Set the position scaling factor for all or a specified tracker in the list, by default will reset to defaults"""
		if id is None:
			for each in self.pos_scale_list:
				if each is not None:
					each.setScale (scale)
		else:
			if self.pos_scale_list[id] is not None:
				self.pos_scale_list[id].setScale(scale)

	def setOriScale(self, scale=[1,1,1], id=None):
		"""Set the orientation scaling factor for all or a specified tracker in the list, by default will reset to defaults"""
		if id is None:
			for each in self.ori_scale_list:
				if each is not None:
					each.setScale (scale)
		else:
			if self.ori_scale_list[id] is not None:
				self.ori_scale_list[id].setScale(scale)

	def getTracker(self, slot, fatal=True):
		"""
		Return the output tracker for the given composite slot number
		@param fatal: Set this to False if you are ok with getting None when no tracker is available, otherwise a fatal error occurs
		"""
		if self.tracker_output[slot] is None and fatal is True:
			FatalError ("Cannot retrieve missing body part " + self.tracker_names[slot])
		return self.tracker_output[slot]

	def getRawTracker(self, slot, fatal=True):
		"""
		Return the actual input tracker for the given composite slot number
		@param fatal: Set this to False if you are ok with getting None when no tracker is available, otherwise a fatal error occurs
		"""
		if self.tracker_input[slot] is None and fatal is True:
			FatalError ("Cannot retrieve missing body part " + self.tracker_names[slot])
		return self.tracker_input[slot]

	def _configHand(self, inhand, fingerRadius=None, touchRadius=None, pinchEnable=None, debugPrimitives=None, handSize=None):
		"""
		Store extra attributes that define how the hand should perform
		@param inhand: The internal hand object to add attributes to
		@param fingerRadius: The size of the sphere to attach to the finger tips to detect grabbing
		@param touchRadius: How far apart two finger spheres can be to be considered a pinch gesture
		@param pinchEnable: Indicates if we want to enable pinch detection with this hand
		@param debugPrimitives: Should the underlying physics primitives be shown
		@param handSize: Scaling factor to apply to the size of the hands (default is 1.0)
		"""
		if fingerRadius is None:
			inhand.configFingerRadius = HAND_FINGER_RADIUS
		else:
			inhand.configFingerRadius = fingerRadius
		if touchRadius is None:
			inhand.configTouchRadius = HAND_TOUCH_RADIUS
		else:
			inhand.configTouchRadius = touchRadius
		if pinchEnable is None:
			inhand.configPinchEnable = HAND_PINCH_ENABLE
		else:
			inhand.configPinchEnable = pinchEnable
		if debugPrimitives is None:
			inhand.configDebugPrimitives = HAND_DEBUG_PRIMITIVES
		else:
			inhand.configDebugPrimitives = debugPrimitives

		# Ability to scale the hands and other features
		if handSize is not None:
			inhand.configHandSize = handSize
			sc = inhand.getScale() # Need to adjust scale relative to existing scale since the hand defines other internal transforms as well
			sc[0] = sc[0] * handSize
			sc[1] = sc[1] * handSize
			sc[2] = sc[2] * handSize
			inhand.setScale(sc)
		else:
			inhand.configHandSize = 1.0 # By default we leave the hand at the default size

	def copyHandOriFromHead(self, extraori=None, horizofs=-30, pitchofs=-45):
		"""
		This is an indirect way to apply extraori and pitchofs values to createLeftHand and createRightHand. There are cases like
		in the demo CD where we define the tracker in one part, and the hands in another. So using this method you can set some
		variables so that they will be used later on by createLeft/RightHand() methods.
		@param extraori: source of the orientation data, typically it is self.tracker_output[comp.HEAD]
		@param pitchofs: An offset to apply to the hand to pitch it towards or away from the user, makes the hand look better at the default -45 degrees
		"""
		if extraori is not None:
			self._handorifromhead = extraori
		else:
			self._handorifromhead = self.tracker_output[self.HEAD]
		self._handorifromheadpitchofs = pitchofs
		self._handorifromheadhorizofs = horizofs

	def createLeftHand(self, grabsensor, visible=True, extraori=None, horizofs=-30, pitchofs=-45, *args, **kw):
		"""
		Takes in a 5DT glove, CyberGlove, or any hand class input sensor
		Sometimes we don't have trackers that supply orientation directly, so we can override it here. Typically you
		would use the orientation from the user's head.
		@param grabsensor: The sensor device supplying the actions of the hand
		@param visible: Set this to False if you do not want the hand to be made visible
		@param extraori: The orientation data from this tracker will be linked against the hand, useful in cases when you only have position tracking on the hands
		@param horizofs: When extraori is supplied, we can also supply an offset to rotate the hand around so you can see the fingers easier
		@param pitchofs: When extraori is supplied, we can also supply an offset to apply to the hand to pitch it towards or away so you can see the fingers easier
		"""
		if self.tracker_output[self.LHAND] is None:
			viz.logWarn("Warning! Left hand is not defined, so skipping createLeftHand setup")
			return
		if not grabsensor.valid():
			viz.logWarn("Warning! Left hand sensor is not valid, so will create hand but the input device could not be found")
			grabsensor = hand.MultiInputSensor() # Create sensor to supply empty data
		self.left_hand = hand.add (grabsensor, left=True)
		self._configHand(self.left_hand,**kw)

		# If copyHandOriFromHead() has been called, then we should use these attributes instead
		if hasattr(self,"_handorifromhead"):
			extraori = self._handorifromhead
			pitchofs = self._handorifromheadpitchofs
			horizofs = self._handorifromheadhorizofs

		# We disable rendering so that if other code calls obj.visible(1) it will still not be rendered
		if visible is False:
			self.left_hand.disable (viz.RENDERING)
		if extraori is not None:
			viz.link (self.getTracker(self.LHAND), self.left_hand, mask=viz.LINK_POS)
			handlink = viz.link (extraori, self.left_hand, mask=viz.LINK_ORI)
			handlink.preEuler([-horizofs,pitchofs,0])
		else:
			handlink = viz.link (self.getTracker(self.LHAND), self.left_hand)

	def createRightHand(self, grabsensor, visible=True, extraori=None, horizofs=-30, pitchofs=-45, **kw):
		"""
		Takes in a 5DT glove, CyberGlove, or any hand class input sensor
		Sometimes we don't have trackers that supply orientation directly, so we can override it here. Typically you
		would use the orientation from the user's head.
		@param grabsensor: The sensor device supplying the actions of the hand
		@param visible: Set this to False if you do not want the hand to be made visible
		@param extraori: The orientation data from this tracker will be linked against the hand, useful in cases when you only have position tracking on the hands
		@param horizofs: When extraori is supplied, we can also supply an offset to rotate the hand around so you can see the fingers easier
		@param pitchofs: When extraori is supplied, we can also supply an offset to apply to the hand to pitch it towards or away so you can see the fingers easier
		"""
		if self.tracker_output[self.RHAND] is None:
			viz.logWarn("Warning! Right hand is not defined, so skipping createRightHand setup")
			return
		if not grabsensor.valid():
			viz.logWarn("Warning! Right hand sensor is not valid, so will create hand but the input device could not be found")
			grabsensor = hand.MultiInputSensor() # Create sensor to supply empty data
		self.right_hand = hand.add (grabsensor, left=False)
		self._configHand(self.right_hand,**kw)

		# If copyHandOriFromHead() has been called, then we should use these attributes instead
		if hasattr(self,"_handorifromhead"):
			extraori = self._handorifromhead
			pitchofs = self._handorifromheadpitchofs
			horizofs = self._handorifromheadhorizofs

		# We disable rendering so that if other code calls obj.visible(1) it will still not be rendered
		if visible is False:
			self.right_hand.disable (viz.RENDERING)
		if extraori is not None:
			viz.link (self.getTracker(self.RHAND), self.right_hand, mask=viz.LINK_POS)
			handlink = viz.link (extraori, self.right_hand, mask=viz.LINK_ORI)
			handlink.preEuler([horizofs,pitchofs,0])
		else:
			handlink = viz.link (self.getTracker(self.RHAND), self.right_hand)

	def getLeftHand(self):
		"""Return reference to the left hand object"""
		return self.left_hand

	def getRightHand(self):
		"""Return reference to the right hand object"""
		return self.right_hand

	def getMiscHands(self):
		"""Return reference to the list of miscellaneous hand objects"""
		return self.misc_hands

	def addMiscHand(self, handsensor, **kw):
		"""
		This method is used if you want to add arbitrary hand objects to an avatar. This is useful if you want
		to work with motion captured tools, or make it so the feet could be used to punch with, etc.
		"""
		if not handsensor.valid():
			viz.logWarn("Warning! Miscellaneous hand sensor is not valid, so will create hand but the input device could not be found")
			handsensor = hand.MultiInputSensor() # Create sensor to supply empty data
		self._configHand(handsensor,**kw)
		self.misc_hands.append(handsensor)

	def getAvatar(self):
		"""Return the avatar that was created for this composite"""
		if not hasattr(self, "avatar"):
			FatalError("Cannot run this method until one of the createAvatar*() methods are called on the object")
		return (self.avatar)

	def _addNewPart (self, slot, label, dir, size):
		"""Internal debugging function for debugLabels method below"""
		tracker = self.tracker_output[slot]
		if tracker is not None:
			objx = viz.add ('ball.wrl', scale=[size, size, size])
			textx = viz.add(viz.TEXT3D, label, scale=[size/2.0, size/2.0, size/2.0])
			textx.alignment(dir)
			textx.billboard(viz.BILLBOARD_VIEW)
			viz.link (tracker, objx)
			label = viz.link (tracker, textx)
			label.postTrans ([0,0.3,0])

	def debugLabels(self, size=0.2):
		"""Attach labels to the trackers on each body part for debugging purposes"""
		self._addNewPart (self.HEAD,  "Head",  viz.TEXT_LEFT_TOP, size)
		self._addNewPart (self.LHAND, "LH", viz.TEXT_LEFT_TOP, size)
		self._addNewPart (self.RHAND, "RH", viz.TEXT_RIGHT_TOP, size)
		self._addNewPart (self.LFOOT, "LF", viz.TEXT_LEFT_BOTTOM, size)
		self._addNewPart (self.RFOOT, "RF", viz.TEXT_RIGHT_BOTTOM, size)
		self._addNewPart (self.HIP,   "Hip", viz.TEXT_RIGHT_BOTTOM, size)


	# ---- Begin viewpoint and display specific code (non-tracker related) ----

	def defineViewpoint(self, viewobj=None, offset=[0,0,0], priority=PRIORITY_LINKS_POST_VIEWPOINT, debugSphere=False, noWindow=False):
		"""
		Call this to define a viewpoint to use, typically a user would either use an avatar head bone, or a tracker.
		By default, we go with the head tracker at offset HEAD unless something else is supplied
		@param viewobj: The object to attach the viewpoint to, default is None which is assigned to the HEAD tracker
		@param offset: Specify an additional offset to move the viewpoint away, useful to get in front of a 3D object
		@param priority: The priority to use for the internal link, no need to modify this in most cases
		@param debugSphere: Show a sphere rendered at the viewpoint location so we can see it when debugging
		@param noWindow: Set this to true and a window will not be allocated, there are some times like a CAVE user where we never use this window
		"""

		# Create VizView object to define this viewpoint
		self.viewpoint = addVUVizView()
		if viewobj == None:
			self.viewsrc = self.getTracker(self.HEAD)
		else:
			self.viewsrc = viewobj
		self.viewlink = viz.link (self.viewsrc, self.viewpoint, enabled=False)
		self.viewlink.preTrans (offset)
		vizact.onupdate (priority, self.viewlink.update)

		# Create a debugging sphere to represent the eye location if requested
		if debugSphere:
			import vizshape
			sphere = vizshape.addSphere(0.02)
			sphere.color(1,0,0)
			slink = viz.link (self.viewpoint, sphere, enabled=False)
			vizact.onupdate (priority, slink.update)

		if noWindow:
			# Do not allocate a window. Some times we want to create a composite so that we can reference
			# where the viewpoint might be, but we don't want it to actually render anywhere. So we set
			# noWindow to True in these cases, and this composite will not create or return a window
			self.window = None
		else:
			# Create a full-sized VizWindow object so this viewpoint can appear wherever we desire
			self.window = addVUVizWindow()
			self.window.setView(self.viewpoint)
			self.window.visible(0) # Make it invisible initially, cluster code will enable it if desired

		# Save viewpoint priority so we can override it if needed
		self.viewpriority = priority

		# Return the window back in case something wants to reference it
		return self.window

	# This code is currently not finished and so it is commented out
	#	def setCollisionDetect(self, active=True, priority=PRIORITY_LINKS_POST_VIEWPOINT):
	#		"""
	#		Calling this method enables viewpoint collision detection. It is a little tricky to do this since
	#		the driver is pushed through a series of links to get to the actual rendered viewpoint. But we use
	#		the reset_node to work out offsets that need to be applied so that movements from trackers are
	#		applied correctly.
	#
	#		Note: This method is not completed and does not fully work yet.
	#		"""
	#		if active:
	#			# Activate collision detection on the actual final output node
	#			self.viewpoint.collision(viz.ON)
	#			# We have self.viewsrc (input) and self.viewpoint (actual output) and so we can compute the difference
	#			self.collidelink = viz.link (self.viewpoint, self.reset_node)
	#			self.collidelink.setMask(viz.LINK_POS)
	#			self.collidelink.postMultInverseLinkable (self.viewsrc)
	#		else:
	#			# Turn the special collision link off and set things back to the defaults
	#			self.viewpoint.collision(viz.OFF)
	#			self.collidelink.remove()
	#			self.collidelink = None
	#			self.resetNodeClear()

	def setCollision(self, state=True, stepsize=0.5):
		"""
		Enabled collision support for this composite viewpoint. Currently this code only works for VUTrackerVirtual objects
		although we are planning on making this support for all composite types later on.
		"""
		if state:
			if hasattr(self.getRawTracker(self.HEAD), "setCollision"):
				viz.logNotice("Setting collision mode for a VUTrackerVirtual-based composite")
				self.getRawTracker(self.HEAD).setCollision(state=True, stepsize=stepsize)
				self.getAvatar().getRawAvatar().disable(viz.INTERSECTION)
				if self.getLeftHand():  self.getLeftHand().disable(viz.INTERSECTION)
				if self.getRightHand(): self.getRightHand().disable(viz.INTERSECTION)
			else:
				viz.logNotice("Ignoring activate setCollision() call since normal composites do not implement this yet")
		else:
			if hasattr(self.getRawTracker(self.HEAD), "setCollision"):
				viz.logNotice("Disabling collision mode for a VUTrackerVirtual-based composite")
				self.getRawTracker(self.HEAD).setCollision(state=False, stepsize=stepsize)
				self.getAvatar().getRawAvatar().enable(viz.INTERSECTION)
				if self.getLeftHand():  self.getLeftHand().enable(viz.INTERSECTION)
				if self.getRightHand(): self.getRightHand().enable(viz.INTERSECTION)
			else:
				viz.logNotice("Ignoring deactivate setCollision() call since normal composites do not implement this yet")

	def getWindowList(self):
		"""
		Return back a list of windows assigned to this composite. Normally each composite has only one
		window, but CAVEs can have more than one, so we use a list to return a single element here
		"""
		if self.window is None:
			return []
		else:
			return [self.window]

	def overrideViewpoint(self, newview):
		"""Use this method if you want to temporarily override the current viewpoint with something like an auto-fly"""
		if self.overridelink is not None:
			# print "Warning! Viewpoint already overridden, so clearing existing override before beginning"
			self.overridelink.remove()
		self.overridelink = viz.link (newview, self.viewpoint, enabled=False)
		vizact.onupdate (self.viewpriority+1, self.overridelink.update)

	def clearOverrideViewpoint(self):
		"""Call this to reset the viewpoint back to the standard view, removes any auto-fly"""
		if self.overridelink is None:
			# print "Warning! Viewpoint not overridden, so cannot clear an existing link"
			pass
		else:
			self.overridelink.remove()
		self.overridelink = None

	def getViewpointSource (self):
		"""Return back the view for the user, the actual location of the user, before it is possibly adjusted by an auto-fly or something"""
		if not hasattr(self, "viewsrc"):
			FatalError("Cannot run this method until defineViewpoint() is called on the object")
		return self.viewsrc

	def getViewpointFinal (self):
		"""Return back the actual view location for this user, it may be adjusted by an auto-fly, so don't call this to find out where the user is standing"""
		return self.viewpoint

	# These methods are deprecated and will be removed if we rewrite all our dependent code

	def setConfigDisplayCommands(self, cmds):
		"""Deprecated: Set display commands to apply to this composite"""
		self.configDisplayCommands = cmds

	def addConfigDisplayCommands(self, cmds):
		"""Deprecated: Add extra display commands to apply to this composite"""
		self.configDisplayCommands = self.configDisplayCommands + cmds

	def getConfigDisplayCommands(self):
		"""Deprecated: Return back the current list of display commands to apply to this composite"""
		return self.configDisplayCommands


	def forceLookAt(self, target):
		"""
		This method takes the current composite, and overrides the final avatar so that it constantly
		looks at the specified target object. It works out the right way depending on if we have a simple
		object or a full avatar. Note we need to implement lookat functionality here and not as a real
		tracker because the origin node and reset node are not applied to trackers, the avatar is the only
		place where we see the final avatar position, and so we can do the lookat properly here.
		"""

		# We firstly need to take the avatar and make the body and head face in the correct direction
		VUControlAvatarLookAt (self.getAvatar(), target)

		# This may seem strange, but we still need to make the viewpoint do the lookat as well. It is
		# because there are so many update events at different priorities that it is difficult to make
		# everything link together properly. So we also adjust the viewpoint like a standard object. If
		# we don't do this then the viewpoint does not match the avatar properly
		VUControlObjectLookAt (self.getViewpointSource(), target)




class VUCompositeTrackers (VUCompositeGeneric):
	"""This is a composite class for dealing with a series of markers defining a body, up to six of them, say from PPT"""
	def __init__(self, priority=PRIORITY_LINKS_TRACKER):
		VUCompositeGeneric.__init__(self) # Initialise the base class
		self.link_priority = priority

	def getCompType(self):
		"""Return the name of the object type"""
		return "Multi-tracker Composite"

	def getDebug(self):
		"""Return debugging information for this object"""
		output = ""
		output = output + "Viewpoint  %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.viewpoint.getPosition(viz.ABS_GLOBAL)) + tuple(self.viewpoint.getEuler(viz.ABS_GLOBAL)))
		output = output + "ResetNode  %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.reset_node.getPosition(viz.ABS_GLOBAL)) + tuple(self.reset_node.getEuler(viz.ABS_GLOBAL)))
		output = output + "OriginMove %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.origin_node.getPosition(viz.ABS_GLOBAL)) + tuple(self.origin_node.getEuler(viz.ABS_GLOBAL)))
		i = 0
		while i < len(self.driver_node_list):
			output = output + "DriverNode%d " % (i+1)
			output = output + "%.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.driver_node_list[i].getPosition(viz.ABS_GLOBAL)) + tuple(self.driver_node_list[i].getEuler(viz.ABS_GLOBAL)))
			i = i + 1
		i = 0
		while i < len(self.tracker_names):
			# It is possible to have an artificially added output tracker without an input tracker, but not the other way around
			if self.tracker_output[i] is not None:
				output = output + "%s " % (self.tracker_names[i])
				if self.tracker_input[i] is not None:
					output = output + "In: %.1f,%.1f,%.1f %.0f,%.0f,%.0f " % (tuple(self.tracker_input[i].getPosition(viz.ABS_GLOBAL)) + tuple(self.tracker_input[i].getEuler(viz.ABS_GLOBAL)))
				else:
					output = output + "In: [n/a - output only] "
				output = output + "Out: %.1f,%.1f,%.1f %.0f,%.0f,%.0f" % (tuple(self.tracker_output[i].getPosition(viz.ABS_GLOBAL)) + tuple(self.tracker_output[i].getEuler(viz.ABS_GLOBAL)))
				output = output + "\n"
			i = i + 1
		return output

	def storeHeadTracker(self, tracker):
		"""Call this method if you only need to store one tracker"""
		self.storeTracker(self.HEAD, tracker)

	def storeTracker(self, slot, tracker):
		"""
		Store the incoming tracker to the selected slot. Note that finishTrackers() still needs to be called to produce the final output
		@param slot: The slow number to assign the tracker to (HEAD, LHAND, RHAND, LFOOT, RFOOT, HIP)
		@param tracker: The VUTracker-type object to be used as the input, also supports standard Vizard objects too
		"""

		# If the incoming object is not a VUTrackerGeneric then we need to wrap it up within one
		if not isinstance(tracker, VUTrackerGeneric):
			tracker = VUTrackerGeneric(tracker)

		# print "Storing incoming tracker into slot %d %s" % (slot, self.tracker_names[slot])
		self.tracker_input[slot] = tracker

		# Create a link and a target node that applies the offsets that we need. Note that we apply
		# all of our driver nodes as well as the reset_node here. Other transforms such as the origin_node
		# are special and can be manipulated by the scene graph, so it needs to have a different priority,
		# otherwise code that drives the scene graph around to move the viewpoint will cause stuttering
		# in the viewpoint output
		tempTracker = viz.addGroup()
		driverlink = viz.link(self.tracker_input[slot], tempTracker, enabled=False)
		vizact.onupdate (self.link_priority, driverlink.update)

		# We only support capturing the current position and using this as the origin, anything else doesn't make sense any more
		if slot is 0:
			onkeydownspecial ('p', self.resetNodeXZ)

		# Store the link for later use
		self.driverlink_list[slot] = driverlink


		# Now we build up a final node which has both the tracker and the origin_node combined together
		# Note the higher priority, which puts it after the basic tracker but before the viewpoint which is
		# typically done later on using the default priority
		self.tracker_output[slot] = viz.addGroup()
		finallink = viz.link(tempTracker, self.tracker_output[slot], enabled=False)
		vizact.onupdate (self.link_priority+1, finallink.update)

		# Add a scaling factor to all outputs so we can scale position values to boost user motion to larger areas
		# Use the finallink so that the scaling is applied to the tracker and the driver together, but the origin node is not scaled
		self.pos_scale_list[slot] = finallink.postScale([1,1,1], target=viz.LINK_POS_OP)
		self.ori_scale_list[slot] = finallink.postScale([1,1,1], target=viz.LINK_ORI_OP)

		# Keep a copy of the tempTracker for slot 0, this will be used for resetting the coordinate system later on
		if slot is 0:
			self.reset_output = tempTracker

		# Apply the global origin offset to this new link, must do this last as mentioned earlier. Also, we use post
		# operations for both trans and rotate and in the proper order, because we want these to be applied properly.
		# The driver nodes are applied in reverse, and rotate is done pre-mult to avoid problems with keyboard rotations
		finallink.postMultLinkable (self.origin_node, flag=viz.ABS_GLOBAL, mask=viz.LINK_ORI)
		finallink.postMultLinkable (self.origin_node, flag=viz.ABS_GLOBAL, mask=viz.LINK_POS)

	def overrideTracker(self, slot, tracker):
		"""Call this method if you want to override the output tracker, needed if you want to make a VUTrackerMouse2D into a 3D tracker"""
		self.tracker_output[slot] = tracker

	def createAvatarSimple(self, obj3d, seeself=True, priority=PRIORITY_LINKS_POST_AVATAR):
		"""
		Create a simple object representation for the viewpoint
		@param obj3d: The object to use as the avatar
		@param seeself: Should this avatar be visible to the window in the same composite, can the composite see it's own body
		@param priority: Internal priority to assign to the link moving the avatar around, no need to adjust this usually
		"""
		self.avatar = VUAvatarSimple (self.getTracker(self.HEAD), obj3d, seeself=seeself, priority=priority)
		return (self.avatar)

	def createAvatarNone(self, priority=PRIORITY_LINKS_POST_AVATAR):
		"""
		Use this if you do not want to have any avatar representation at all
		@param priority: Internal priority to assign to the link moving the avatar around, no need to adjust this usually
		"""
		self.avatar = VUAvatarSimple (self.getTracker(self.HEAD), viz.addGroup(), priority=priority)
		return (self.avatar)

	def createAvatarFixedBody(self, avatar, groundlevel=False, seeself=True, priority=PRIORITY_LINKS_POST_AVATAR):
		"""
		Use this to create an avatar with a fixed body, you can control whether it is fixed to the ground or not
		@param avatar: Define a Vizard avatar such as vcc_male.cfg or vcc_female.cfg and pass it in here
		@param groundlevel: If set to True, the avatar will always be kept at ground level no matter what the tracker height is
		@param seeself: Should this avatar be visible to the window in the same composite, can the composite see it's own body
		@param priority: Internal priority to assign to the link moving the avatar around, no need to adjust this usually
		"""
		self.avatar = VUAvatarFixedBody (self.getTracker(self.HEAD), avatar, groundlevel=groundlevel, seeself=seeself, priority=priority)
		return (self.avatar)

	def createAvatarSteve(self, seeself=True, priority=PRIORITY_LINKS_POST_AVATAR, *args,**kw):
		"""
		Use this to use a STEVE object, which looks like a space alien, with physics for the body motion
		@param seeself: Should this avatar be visible to the window in the same composite, can the composite see it's own body
		@param priority: Internal priority to assign to the link moving the avatar around, no need to adjust this usually
		"""
		self.avatar = VUAvatarSteve (self.getTracker(self.HEAD), seeself=seeself, priority=priority, *args, **kw)
		return (self.avatar)




class VUCompositeTrackersVRPN (VUCompositeTrackers):
	"""
	This is a composite class which is basically the same as the standard one, except it does VRPN automatically for all the body parts.
	Note that you can also add one supplemental orientation sensor, but it will only be added to the head tracker.
	If you want to supplement others then you probably should implement the following code yourself and add orientation manually.
	@param hostname: The VRPN hostname string to use. For PPT it would be PPT0@HOSTNAME
	@param inputs: By default it is [0,1,2,3,4,5] which tells it to add trackers for all of the head, hands, feet, and hips, use None if you don't want to do anything
	@param nodes: (Deprecated) Previously defaulted to [1,1,1,1,1,1] which controls which trackers we try and add, we prefer to use the inputs array if possible now
	@param swapPos: Apply swapping of position arguments for the raw tracker inputs, needed by some devices
	@param swapQuat: Apply swapping of quaternion arguments for the raw tracker inputs, needed by some devices
	@param supplementIntersense: Set to the com port of the InterSense device if you want to add one to the head, can also be an array of flags too
	@param supplementXsens: Set to the com port of the Xsense device if you want to add one to the head, can also be an array of flags too
	@param supplementGeneric: Set a generic tracker if you want to add one to the head manually, can also be an array of flags too
	@param supplementAuto: Set to True or a com port if you want to do an automatic search for any InterSense or Xsens device, can also be an array of flags too
	@param magneticzero: Set to an angle if you want to apply an offset to correct for differences between tracker and magnetic north
	"""
	def __init__(self, hostname, inputs=[0,1,2,3,4,5], nodes=None, swapPos=None, swapQuat=None, supplementIntersense=None, supplementXsens=None, supplementAuto=None, supplementGeneric=None, magneticzero=None):
		VUCompositeTrackers.__init__(self) # Initialise the base class
		if len(inputs) > 6:
			FatalError("Input array list must have 6 or less elements, found %d" % len(inputs))
		if nodes is not None and len(nodes) > 6:
			FatalError("Deprecated nodes array list must have 6 or less elements, found %d" % len(nodes))
		i = 0
		while i < 6:
			# The nodes array is simpler but is not being used any more, only left for compatibility with some very old scripts
			if nodes is not None and i < len(nodes) and nodes[i] is 1:
				tracker = VUTrackerVRPN(hostname, i, swapPos=swapPos, swapQuat=swapQuat)
			# Assign inputs based on the assignments in the array
			elif i < len(inputs) and inputs[i] is not None:
				tracker = VUTrackerVRPN(hostname, inputs[i], swapPos=swapPos, swapQuat=swapQuat)
			else:
				tracker = None

			# Add supplemental trackers if we actually added a tracker
			if tracker is not None:
				s = None
				a = supplementIntersense
				if isinstance(a,list) and a[i] is not None:
					s = a[i]
				elif i == 0 and a is not None:
					s = a
				if s is not None:
					viz.logNotice("Adding supplemental InterSense %s to VRPN tracker input" % s)
					tracker.supplementIntersense(comport=s, magneticzero=magneticzero)

				s = None
				a = supplementXsens
				if isinstance(a,list) and a[i] is not None:
					s = a[i]
				elif i == 0 and a is not None:
					s = a
				if s is not None:
					viz.logNotice("Adding supplemental Xsens %s to VRPN tracker input" % s)
					tracker.supplementXsens(comport=s, magneticzero=magneticzero)

				s = None
				a = supplementGeneric
				if isinstance(a,list) and a[i] is not None:
					s = a[i]
				elif i == 0 and a is not None:
					s = a
				if s is not None:
					viz.logNotice("Adding supplemental generic orientation %s to VRPN tracker input" % s)
					tracker.supplementGeneric(s, magneticzero=magneticzero)

				s = None
				a = supplementAuto
				if isinstance(a,list) and a[i] is not None:
					s = a[i]
				elif i == 0 and a is not None:
					s = a
				if s is not None:
					viz.logNotice("Adding supplemental automatic detected sensor %s to VRPN tracker input" % s)
					tracker.supplementAutoOrientation(comport=s, magneticzero=magneticzero)

				# Store the tracker now and move on to the next one
				self.storeTracker (i, tracker)
			else:
				viz.logNotice("Ignore VRPN input for slot %d since it is marked as being empty" % i)

			# Move on to the next tracker
			i = i + 1




class VUCompositeLiveCharacters (VUCompositeGeneric):
	"""This is a composite class for dealing with an incoming avatar defining a body, typically from LiveCharacters"""
	def __init__(self, character, seeself=True, priority=PRIORITY_LINKS_TRACKER):
		VUCompositeGeneric.__init__(self)    # Initialise the base class
		self.link_priority = priority
		self._storeLiveCharacter (character) # Store the supplied character
		self._createAvatarLiveCharacters (character, seeself) # Create a matching avatar object

	def getCompType(self):
		"""Return the name of the object type"""
		return "LiveCharacters Composite"

	def getDebug(self):
		"""Return debugging output showing the state of all the internal trackers"""
		output = ""
		output = output + "Viewpoint  %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.viewpoint.getPosition(viz.ABS_GLOBAL)) + tuple(self.viewpoint.getEuler(viz.ABS_GLOBAL)))
		output = output + "ResetNode  %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.reset_node.getPosition(viz.ABS_GLOBAL)) + tuple(self.reset_node.getEuler(viz.ABS_GLOBAL)))
		output = output + "OriginMove %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.origin_node.getPosition(viz.ABS_GLOBAL)) + tuple(self.origin_node.getEuler(viz.ABS_GLOBAL)))
		i = 0
		while i < len(self.driver_node_list):
			output = output + "DriverNode%d " % (i+1)
			output = output + "%.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.driver_node_list[i].getPosition(viz.ABS_GLOBAL)) + tuple(self.driver_node_list[i].getEuler(viz.ABS_GLOBAL)))
			i = i + 1
		i = 0
		while i < len(self.tracker_names):
			output = output + "Bone %s " % (self.tracker_names[i])
			output = output + "In/Out: %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.tracker_input[i].getPosition(viz.ABS_GLOBAL)) + tuple(self.tracker_input[i].getEuler(viz.ABS_GLOBAL)))
			i = i + 1
		return output

	def _createAvatarLiveCharacters(self, avatar, seeself=True):
		"""Internally allocate an avatar like the other composite objects do with createAvatar*() methods, but this is done automatically"""
		self.avatar = VUAvatarLiveCharacters (avatar, seeself=seeself)
		return (self.avatar)

	def _storeLiveCharacter(self, character):
		"""Internal method to store the incoming LiveCharacter object"""
		self.live_character = character

		# We need to grab all the character nodes and store them in the tracker slots
		self.tracker_input [self.HEAD]  = self.live_character.getBone ("Bip01 Head") # Do not use head nub, had problems with MotionBuilder here!
		self.tracker_input [self.LHAND] = self.live_character.getBone ("Bip01 L Finger0")
		self.tracker_input [self.RHAND] = self.live_character.getBone ("Bip01 R Finger0")
		self.tracker_input [self.LFOOT] = self.live_character.getBone ("Bip01 L Toe0")
		self.tracker_input [self.RFOOT] = self.live_character.getBone ("Bip01 R Toe0")
		self.tracker_input [self.HIP]   = self.live_character.getBone ("Bip01 Pelvis")

		# This code is similar to the standard tracking example, please see the above comments for more info on this.
		# Create a link and a target node that applies the offsets that we need. Note that we apply
		# all of our driver nodes as well as the reset_node here. Other transforms such as the origin_node
		# are special and can be manipulated by the scene graph, so it needs to have a different priority,
		# otherwise code that drives the scene graph around to move the viewpoint will cause stuttering
		# in the viewpoint output
		emptyInput = viz.addGroup()
		tempTracker = viz.addGroup()
		driverlink = viz.link(emptyInput, tempTracker, enabled=False)
		vizact.onupdate (self.link_priority, driverlink.update)

		# Keep a copy of the tempTracker for slot 0, this will be used for resetting the coordinate system later on
		self.reset_output = tempTracker

		# We only support capturing the current position and using this as the origin, anything else doesn't make sense any more
		onkeydownspecial ('p', self.resetNodeXZ)

		# Save the link for later use
		self.driverlink_list[0] = driverlink


		# Now we build up a final node which has both the tracker and the origin_node combined together
		# We do this using a similar method as for tracking devices, see that for more info
		finallink = viz.link(tempTracker, self.live_character, enabled=False)
		vizact.onupdate (self.link_priority+1, finallink.update)

		# Add a scaling factor to all outputs so we can scale position values to boost user motion to larger areas
		# Use the finallink so that the scaling is applied to the tracker and the driver together, but the origin node is not scaled
		self.pos_scale_list[self.HEAD] = finallink.postScale([1,1,1], target=viz.LINK_POS_OP)
		self.ori_scale_list[self.HEAD] = finallink.postScale([1,1,1], target=viz.LINK_ORI_OP)

		# Apply the global origin offset to this new link, must do this last as mentioned earlier
		finallink.postMultLinkable (self.origin_node, flag=viz.ABS_GLOBAL, mask=viz.LINK_POS)
		finallink.preMultLinkable (self.origin_node, flag=viz.ABS_GLOBAL, mask=viz.LINK_ORI)

		# Since the avatar handles the transforms, the outputs can be just mapped to the inputs
		i = 0
		while i < len(self.tracker_names):
			self.tracker_output[i] = self.tracker_input[i]
			i = i + 1

	def overrideHeadOrientation(self, orisrc, priority=PRIORITY_LINKS_POST_AVATAR):
		"""
		We support the ability to override the orientation. This is useful in cases when using avatars, sometimes the
		software streaming in data adds latency, and so we want to send orientation data in directly from a device to
		ensure that it is as up to date as possible. Note we only use the orientation data, we don't use position data
		because then it might be possible for the viewpoint to move in such a way that the user sees their own head.
		"""

		# Note that self.tracker_output is just a list of pointers to self.tracker_input, so lets create a replacement
		headnode = viz.addGroup()
		self.tracker_output [self.HEAD] = headnode

		# Use a link to copy over the orientation from the source, and the position is from the avatar
		orilink = viz.link (orisrc, headnode, enabled=False, mask=viz.LINK_ORI)
		vizact.onupdate (priority, orilink.update)
		poslink = viz.link (self.tracker_input[self.HEAD], headnode, enabled=False, mask=viz.LINK_POS)
		vizact.onupdate (priority, poslink.update)

		# Note we need to apply any driver offsets to the orientation as well, which are implemented on the base of the avatar
		orilink.postMultLinkable (self.live_character)

	def defineViewpoint(self, offset=[0,0.11,0.09], **kw): # The default offset is used to move the viewpoint from the avatar's neck/chin to where the eyes are located
		"""
		Define a viewpoint but by default with a small offset to clear the avatar's head.
		This method is the same as VUCompositeGeneric, but we need to apply a small offset to get the viewpoint forward of the user's head.
		"""
		return VUCompositeGeneric.defineViewpoint(self, offset=offset, **kw)


	def createLeftHand(self, fistAngle=HAND_FIST_ANGLE, *args, **kw):
		"""
		This method creates a hand interface based on the hands of the LiveCharacter. When a grab condition
		is detected then this will generate a grab event. Note that no extra hands are added, the LiveCharacter
		provides the rendering of the hands. If you have a 5DT or CyberGlove, you should try to connect them
		through MotionBuilder so that everything is nicely integrated, otherwise you can use the create*HandSensor()
		methods below, particularly if you have a keyboard or mouse clicker-style binary input device.
		"""
		grabsensor = hand.AvatarSensor(self.live_character, left=True, fingerCloseAngle=fistAngle)
		self.left_hand = hand.add (grabsensor)
		self._configHand(self.left_hand,**kw)

	def createRightHand(self, fistAngle=HAND_FIST_ANGLE, *args, **kw):
		"""
		This method creates a hand interface based on the hands of the LiveCharacter. When a grab condition
		is detected then this will generate a grab event. Note that no extra hands are added, the LiveCharacter
		provides the rendering of the hands. If you have a 5DT or CyberGlove, you should try to connect them
		through MotionBuilder so that everything is nicely integrated, otherwise you can use the create*HandSensor()
		methods below, particularly if you have a keyboard or mouse clicker-style binary input device.
		"""
		grabsensor = hand.AvatarSensor(self.live_character, left=False, fingerCloseAngle=fistAngle)
		self.right_hand = hand.add (grabsensor)
		self._configHand(self.right_hand,**kw)

	def createLeftHandSensor(self, grabsensor, **kw):
		"""
		Takes in a 5DT glove, CyberGlove, or any hand class InputSensor, as a grabbing device,
		and makes them work with a LiveCharacter. The hand classes have the ability to override the
		LiveCharacter, but ideally you should have all the input device data being processed before it reaches
		Vizard to get the best accuracy, particularly with something like a glove used here.
		"""
		if not grabsensor.valid():
			viz.logWarn("Warning! Left hand sensor is not valid, so will create hand but the input device could not be found")
			grabsensor = hand.MultiInputSensor() # Create sensor to supply empty data
		self.left_hand = hand.AvatarHandModel(self.live_character, left=True, sensor=grabsensor)
		self._configHand(self.left_hand,**kw)

	def createRightHandSensor(self, grabsensor, **kw):
		"""
		Takes in a 5DT glove, CyberGlove, or any hand class InputSensor, as a grabbing device,
		and makes them work with a LiveCharacter. The hand classes have the ability to override the
		LiveCharacter, but ideally you should have all the input device data being processed before it reaches
		Vizard to get the best accuracy, particularly with something like a glove used here.
		"""
		if not grabsensor.valid():
			viz.logWarn("Warning! Right hand sensor is not valid, so will create hand but the input device could not be found")
			grabsensor = hand.MultiInputSensor() # Create sensor to supply empty data
		self.right_hand = vizshape.addPyramid(base=(0.5,0.5),height=0.5,color=viz.YELLOW)
		self._configHand(self.right_hand,**kw)




class VUCompositeCAVE (VUCompositeTrackers):
	"""This is a composite class that integrates CAVE environments into the overall system"""
	def __init__(self, pos=[0,0,0], priority=PRIORITY_LINKS_TRACKER):
		VUCompositeTrackers.__init__(self, priority) # Initialise the base class
		import vizcave
		self.cavedef = vizcave.Cave() # Create a vizcave object to store walls in

		# Create a plain tracker to represent where the CAVE is located. We hard wire this because CAVEs do not
		# move around in the physical world. You can use addDriverNode if you want to move the CAVE around.
		self.storeTracker(self.HEAD, VUTrackerGeneric(pos=pos))

		# Create a node that represents the base of the CAVE, everything will be relative to this node
		self.caveorigin = viz.addGroup()

		# Initialise lists of our walls and windows
		self.window_list = []
		self.wall_list = []

	def getCompType(self):
		"""Return the name of the object type"""
		return "CAVE %d-Wall Composite\n" % len(self.window_list)

	def getDebug(self):
		output = ""
		output = output + "CAVE-Origin %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.caveorigin.getPosition(viz.ABS_GLOBAL)) + tuple(self.caveorigin.getEuler(viz.ABS_GLOBAL)))
		output = output + "View-Source %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.viewsrc.getPosition(viz.ABS_GLOBAL)) + tuple(self.viewsrc.getEuler(viz.ABS_GLOBAL)))
		output = output + "View-Local %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.viewlocal.getPosition(viz.ABS_GLOBAL)) + tuple(self.viewlocal.getEuler(viz.ABS_GLOBAL)))
		output = output + "View-Final  %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.viewpoint.getPosition(viz.ABS_GLOBAL)) + tuple(self.viewpoint.getEuler(viz.ABS_GLOBAL)))
		output = output + "ResetNode  %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.reset_node.getPosition(viz.ABS_GLOBAL)) + tuple(self.reset_node.getEuler(viz.ABS_GLOBAL)))
		output = output + "OriginMove %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.origin_node.getPosition(viz.ABS_GLOBAL)) + tuple(self.origin_node.getEuler(viz.ABS_GLOBAL)))
		i = 0
		while i < len(self.driver_node_list):
			output = output + "DriverNode%d " % (i+1)
			output = output + "%.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.driver_node_list[i].getPosition(viz.ABS_GLOBAL)) + tuple(self.driver_node_list[i].getEuler(viz.ABS_GLOBAL)))
			i = i + 1
		i = self.HEAD
		output = output + "CAVE-Base "
		output = output + "In: %.1f,%.1f,%.1f %.0f,%.0f,%.0f " % (tuple(self.tracker_input[i].getPosition(viz.ABS_GLOBAL)) + tuple(self.tracker_input[i].getEuler(viz.ABS_GLOBAL)))
		output = output + "Out: %.1f,%.1f,%.1f %.0f,%.0f,%.0f\n" % (tuple(self.tracker_output[i].getPosition(viz.ABS_GLOBAL)) + tuple(self.tracker_output[i].getEuler(viz.ABS_GLOBAL)))
		return output

	def _adjustWall(self, wall, xflip, yflip):
		"""Helper method take takes in a CAVE Wall object, and flips the images around if the projector is not setup right"""
		import vizcave
		if xflip and not yflip:
			fUL = wall.getUpperRight()
			fUR = wall.getUpperLeft()
			fLL = wall.getLowerRight()
			fLR = wall.getLowerLeft()
		elif not xflip and yflip:
			fUL = wall.getLowerLeft()
			fUR = wall.getLowerRight()
			fLL = wall.getUpperLeft()
			fLR = wall.getUpperRight()
		elif xflip and yflip:
			fUL = wall.getLowerRight()
			fUR = wall.getLowerLeft()
			fLL = wall.getUpperRight()
			fLR = wall.getUpperLeft()
		else:
			return wall # Do nothing to the wall if no arguments supplied

		# Return back a new CAVE wall if changes were made
		return vizcave.Wall (name=wall.getName(), upperLeft=fUL, upperRight=fUR, lowerLeft=fLL, lowerRight=fLR)


	# Add a wall to our internal CAVE object, we also create windows and viewpoints for each one as well
	def addWall(self, wall, xflip=False, yflip=False, stereo=0):
		# Create a window
		window = addVUVizWindow()
		window.visible(0) # Make it invisible initially, cluster code will enable it if desired
		window.setView(self.viewpoint) # Make the window use the viewpoint we created for the CAVE
		if stereo is not 0:
			window.stereo(stereo) # Enable desired stereo mode based on supplied argument
		self.cavedef.addWall(self._adjustWall(wall,xflip=xflip,yflip=yflip), window=window)
		self.wall_list.append (wall)
		self.window_list.append (window)

		# Check that the window has stereo flags enabled if stereo mode was nominated in defineViewpoint()
		# It doesn't make sense to have one but not both, so make this a fatal error in case the user forgot
		if self.stereo and window.getStereo() is 0:
			FatalError ("CAVE declared to be using a stereo tracker, but addWall call did not include any stereo mode request")

		# Return a reference to the window in case the caller wants to use it
		return window

	def createAvatarNone(self, avatarpriority=PRIORITY_LINKS_POST_AVATAR):
		"""If you do not want to see any CAVE representation at all, you still need to create an avatar, so use this method for that"""
		self.createAvatarCAVE(drawLabels=False, drawOrigin=False, drawWalls=False, avatarpriority=avatarpriority)

	def createAvatarCAVE(self, seeself=True, drawLabels=False, drawOrigin=True, drawWalls=True, wallcolor=[1,0,0], drawInputWalls=False, inputwallcolor=[0,1,0], collisionThickness=5, collisionDensity=10, avatarpriority=PRIORITY_LINKS_POST_AVATAR):
		""" Create a representation of the CAVE frame so that others can see where it is exactly (not intended for the CAVE user to see)"""

		# We add this new CAVE origin as our avatar for now. It does not render anything. However later
		# on in this method we add extra detail to this node as required
		self.avatar = VUAvatarSimple (self.getTracker(self.HEAD), self.caveorigin, priority=avatarpriority, seeself=seeself)

		# Create a sphere at the origin, add it to our special avatar origin node
		if drawOrigin:
			import vizshape
			origin = vizshape.addSphere(radius=0.1, slices=5, stacks=5)
			origin.lineWidth(2)
			origin.parent(self.caveorigin)
			origin.polyMode(viz.POLY_WIRE)
			origin.color(wallcolor)

		# Sanity check that we actually have some walls added
		if len(self.wall_list) <= 0:
			FatalError ("Cannot render CAVE outline since no walls have been defined")

		# Container to hold the collision volume objects, see the explanation later for setCollisionPattern()
		# We do not parent this to self.caveorigin, because this object implements the seeself flags. We always
		# want the collision pattern to be visible, so we need to keep this object updated with the origin matrix
		self.collision_pattern = viz.addGroup()
		collision_link = viz.link (self.caveorigin, self.collision_pattern, enabled=False)
		vizact.onupdate (avatarpriority+1, collision_link.update)

		# Draw out the walls, using the actual stored internal vectors used to calculate the frustums
		# If you use the vizcave.drawWalls() method, it actually plots the input data, which may not
		# be accurate if the user makes a mistake with the input data being non-rectangular. So we
		# render the actual data used to draw the frustums, which helps with debugging.
		for each in self.wall_list:
			internal_mat = each._Wall__mat # Bypass private protection to get the matrix
			mat = viz.Transform(internal_mat)
			mat.invert() # Make sure you use a copy, otherwise this will mangle the internal cave matrix used for rendering

			side      = viz.Vector(mat.data[0],  mat.data[1],  mat.data[2])
			up        = viz.Vector(mat.data[4],  mat.data[5],  mat.data[6])
			forward   = viz.Vector(mat.data[8],  mat.data[9],  mat.data[10])
			lowerLeft = viz.Vector(mat.data[12], mat.data[13], mat.data[14])

			LL = lowerLeft
			LR = lowerLeft + side*each.getWidth()
			UR = lowerLeft + side*each.getWidth() + up*each.getHeight()
			UL = lowerLeft + up*each.getHeight()

			if drawWalls:
				# Draw out the walls calculated from the frustum properties, this is what is actually used to render with
				viz.startLayer (viz.LINE_LOOP)
				viz.vertexColor(wallcolor)
				viz.lineWidth(2)
				viz.vertex (UL)
				viz.vertex (UR)
				viz.vertex (LR)
				viz.vertex (LL)
				outline = viz.endLayer(parent=self.caveorigin)

			if drawLabels:
				# Draw out text labels at the center of the walls
				text = self.caveorigin.add(viz.TEXT3D,each.getName())
				bb = text.getBoundingBox()
				s = (each.getWidth() / bb.width) / 2.0
				text.scale(s,s,1)
				text.setQuat(each.getQuat())
				text.translate(each.getCenter())
				text.alignment(viz.TEXT_CENTER_CENTER)
				text.disable(viz.LIGHTING)

			if drawInputWalls:
				# Draw out the walls using the input data supplied by the user, may not match what is actually used
				# Use a line which is thicker and it is drawn afterwards so it is possible to see both at the same time
				viz.startLayer (viz.LINE_LOOP)
				viz.vertexColor(inputwallcolor)
				viz.lineWidth(4)
				viz.vertex (each.getUpperLeft())
				viz.vertex (each.getUpperRight())
				viz.vertex (each.getLowerRight())
				viz.vertex (each.getLowerLeft())
				outline = viz.endLayer(parent=self.caveorigin)

			# There are times when we want to stop the user from walking into the CAVE walls. If the user gets too close
			# then we draw a pattern onto the walls so that the user will not be tempted to walk too close. We prepare it
			# here and then hide it, and make it accessible via a method later
			viz.startLayer (viz.LINES)
			viz.vertexColor(wallcolor)
			viz.lineWidth(collisionThickness)

			x = 0.0
			while x < 1.0:
				vert1 = lowerLeft + side*(each.getWidth()*x)
				vert2 = lowerLeft + side*(each.getWidth()*x) + up*each.getHeight()
				viz.vertex (vert1)
				viz.vertex (vert2)
				x += (1.0/collisionDensity)

			y = 0.0
			while y < 1.0:
				vert1 = lowerLeft + up*(each.getHeight()*y)
				vert2 = lowerLeft + up*(each.getHeight()*y) + side*each.getWidth()
				viz.vertex (vert1)
				viz.vertex (vert2)
				y += (1.0/collisionDensity)

			collision_wall = viz.endLayer(parent=self.collision_pattern)

		# Finished building up the CAVE avatar, lets now hide the collision pattern by default
		self.setCollisionPattern(False)

	def setCollisionPattern(self, state):
		"""
		Use this to control if the collision pattern is shown or not. If set to true then a pattern is drawn
		across the CAVE wall indicating the user is about to collide with it.
		"""
		self.collision_pattern.visible(state)

	def _detectWallCollision(self, tolerance):
		"""Internal method is called to see if the user is too close or outside of the CAVE, and if so then show the collision pattern"""
		collision = False

		# Find inverse transform for the overall CAVE origin
		cavemat = self.caveorigin.getMatrix(viz.ABS_GLOBAL).inverse()

		# Traverse each of the walls in the CAVE
		for each in self.wall_list:
			internal_mat = each._Wall__mat # Bypass private protection to get the matrix

			# Test each body part (head, hands, etc) to check that none of them are near the CAVE wall
			for tracker in self.caveusersrc.tracker_output:
				if tracker is not None:
					# Find the tracker relative to the CAVE, and then to the CAVE wall
					reltracker = viz.Vector(tracker.getPosition(viz.ABS_GLOBAL))
					reltracker *= cavemat
					reltracker *= internal_mat

					if reltracker[2] > -tolerance:
						collision = True

		# If we are outside any of the CAVE walls, then we should activate the visible collision grid
		self.setCollisionPattern(collision)


	# Override this to return back all the windows stored in this object
	def getWindowList(self):
		return self.window_list


	# Override the existing defineViewpoint so that it is CAVE compatible. We should use the supplied caveuser viewpoint as
	# the location of the tracker for the CAVE. Note that you can only have one viewpoint, since CAVEs can only render
	# for one user at a time.
	def defineViewpoint(self, caveuser, offset=[0,0,0], stereo=False, originpriority=PRIORITY_LINKS_POST_AVATAR, priority=PRIORITY_LINKS_POST_VIEWPOINT, detectCollisions=0.1):
		# Store the tracker we will use for the viewpoint, base it on the caveuser supplied
		self.viewsrc = caveuser.getViewpointSource()
		self.caveusersrc = caveuser

		# Create a new tracker that specifies the viewpoint in terms of the CAVE coordinate system, not in global coordinates
		# The vizcave code requires you to specify the setTracker() relative to the CAVE origin where the frustums are defined
		# This code takes the child, post-multiplies it by the inverse of the parent, and calculates the child relative to the CAVE
		self.viewlocal = viz.addGroup()
		findrelative = viz.link (self.viewsrc, self.viewlocal, enabled=False)
		findrelative.postMultInverseLinkable (self.caveorigin)
		vizact.onupdate (originpriority, findrelative.update)

		# Add a handler to detect wall collision and flash up the grid if the user is outside the CAVE or near the walls
		if detectCollisions is not None:
			vizact.ontimer(0.1, self._detectWallCollision, detectCollisions) # No need to run this every frame to save CPU time

		# Tell vizcave to use this newly calculated local coordinates viewpoint for it
		self.stereo = stereo
		if stereo:
			self.cavedef.setTracker(pos=self.viewlocal, ori=self.viewlocal)
		else:
			self.cavedef.setTracker(pos=self.viewlocal)

		# Create VizView object to define this viewpoint, do not create any VizWindow objects because they are created in addWall() above
		# Note that the viewpoint is always defined in world coordinates, we need to be located at the right location in the world to
		# get the view we want. Note that since self.viewlocal is in local coordinates, the distorted CAVE frustum walls effectively
		# "follow" us around the world.
		self.viewpoint = addVUVizView()

		# We need to make sure self.viewpoint is expressed in world coordinates where the user really is, there
		# is no need to use vizcave.CaveView because we do the same transformations ourselves in VUCompositeCAVE
		self.vieworilink = viz.link (self.caveorigin, self.viewpoint, enabled=False, srcFlag=viz.ABS_GLOBAL, dstFlag=viz.ABS_GLOBAL, mask=viz.LINK_ORI)
		self.viewlink    = viz.link (self.viewsrc, self.viewpoint, enabled=False, srcFlag=viz.ABS_GLOBAL, dstFlag=viz.ABS_GLOBAL, mask=viz.LINK_POS)
		self.viewlink.preTrans (offset)
		vizact.onupdate (priority, self.vieworilink.update)
		vizact.onupdate (priority, self.viewlink.update)

		# Save viewpoint priority so we can override it if needed with overrideViewpoint
		self.viewpriority = priority

		# Make it so that the CAVE user has its origin node set to being the CAVE, so all the transforms are done properly
		# It is also possible for other users to go along for a ride with the CAVE as well if they are passed to addRiderComposite
		self.addRiderComposite(caveuser)

		# Do not return anything, if there was just one window we would have returned it here like in the other classes
		return None

	# Specify composite objects that you would like to attach to the CAVE, so when the CAVE moves, the composites move too
	def addRiderComposite(self, composite):
		composite._setOriginParent(self.getTracker(self.HEAD))
		composite._setMovableFixed(True) # Mark this relationship as being fixed and not adjustable by vizmultiscript or anything else




class VUExternalViewpoint (object):
	"""
	This class generates an external viewpoint, and updates with each frame to ensure it matches the user location
	@param pos: The position of the viewpoint
	@param target: The object that the viewpoint should constantly follow
	@param relative: If this is True, makes the viewpoint always relative to the target object
	@param key: The key used to activate the viewpoint (default is the right shift key)
	@param window: The window that is used to provide stereo information
	"""
	def __init__(self, target, pos=[-3.0,1.0,3.0], key=viz.KEY_CONTROL_L, window=viz.MainWindow):
		# Add a picture-in-picture view, which can be toggled on later on as desired
		self.subWindow = viz.addWindow()        # Create a window for the view
		self.subWindow.setSize(0.9, 0.9)        # Set the size of the window to fill most of the display
		self.subWindow.setPosition([0.05,0.95])

		# Configure a viewpoint that is at the desired position, and follows the target object
		lookView = viz.addView() # Internal use only, do not allocate using addVUVizView
		lookView.eyeheight (0) # Need to set the default eye height to zero as always
		lookView.collision (viz.OFF)
		VUControlObjectFollowLookAt (lookView, target, pos)

		# 5m above ground level
		aboveView = viz.addView() # Internal use only, do not allocate using addVUVizView
		aboveView.eyeheight (0)
		aboveView.collision (viz.OFF)
		VUControlObjectFollowLookAt (aboveView, target, [0,5,-0.1])

		# 50m above ground level
		topView = viz.addView() # Internal use only, do not allocate using addVUVizView
		topView.eyeheight (0)
		topView.collision (viz.OFF)
		VUControlObjectFollowLookAt (topView, target, [0,50,-0.1])

		# 200m above ground level
		satView = viz.addView() # Internal use only, do not allocate using addVUVizView
		satView.eyeheight (0)
		satView.collision (viz.OFF)
		VUControlObjectFollowLookAt (satView, target, [0,200,-0.1])

		self.views = [None, lookView, aboveView, topView, satView]

		self.subWindow.setView (lookView) # Set something to keep it happy, toggle() will fix it up later
		self.subWindow.	fov(60)
		self.state = 0
		self.subWindow.stereo (window.getStereo())
		self.subWindow.visible (0)
		if key is not None:
			vizact.onkeydown (key, self.toggle) # Toggle through viewpoints using the supplied key

	def setSize(self, x, y):
		self.subWindow.setSize (x, y)

	def setPosition(self, x, y):
		self.subWindow.setPosition (x, y)

	def setFov(self, fov):
		self.subWindow.fov(fov)

	def toggle(self):
		self.state = self.state + 1
		if self.state == len(self.views):
			self.state = 0
			self.subWindow.visible (0)
		else:
			self.subWindow.visible (1)
			self.subWindow.setView (self.views[self.state])




# This is a simple program that can be used to load in 3D models and preview them easily, it is a complete Vizard program
class SimpleObjectViewer(viz.EventClass):
	def __init__(self, filename="gallery.ive", showFPS=False, distScale=3.0, stereo=False, saveFile="test-output.ive"):
		viz.EventClass.__init__(self)
		self.callback(viz.TIMER_EVENT,self.refresh)
		self.starttimer(0,0,viz.PERPETUAL)
		self.showFPS = showFPS

		if stereo:
			viz.go(viz.STEREO_HORZ)
		else:
			viz.go()
		viz.clearcolor(0.5,0.5,0.5)

		# Load in the 3D model
		self.model = viz.add (filename)
		vizact.onkeydown('s', self.save, saveFile)

		# Setup pivot camera
		import vizcam
		cam = vizcam.PivotNavigate()
		vizact.onkeydown(' ',viz.cam.reset)

		# Position the camera to see the entire object bounds
		bs = self.model.getBoundingSphere()
		bs.angle = 180
		cam.setCenter(bs.center)
		cam.rotateTo(viz.Vector(bs.center)-[0,0,bs.radius*distScale])
		viz.cam.setReset()
		viz.logNotice("Object %s bounding radius = %.1f" % (filename, bs.radius))

	def getModel(self):
		return self.model

	def save(self, filename):
		self.model.save (filename)
		viz.logNotice("Saved out model to file %s" % filename)

	def refresh(self, num):
		if self.showFPS:
			viz.logNotice("FPS = %.0f" % (1/viz.elapsed()))



_VUOrigin__alloc_vuorigin_seq = 0

VT_DEFAULT   = "Default"   # Used for most views that are controlled by a user in a HMD/CAVE, typically centered on the object of interest
VT_VIEWER    = "Viewer"    # Used for automatic viewers that keep an eye on the environment
VT_AERIAL    = "Aerial"    # Used for top down viewpoints that show the entire scene
VT_DESKTRACK = "DeskTrack" # Used on a desktop with some kind of tracker, these typically need specially tweaked viewpoints that can see the object of interest
VT_DESKTOP   = "Desktop"   # Used when we are using a keyboard and mouse to control things, similar to desk track but no FOV or rotation offsets are applied


class VUOrigin (viz.VizNode):
	"""
	Object that is used to store parameters that define an origin in a demo. An origin is a location
	where a user starts out in a demo. An origin can be pushed around like a movable platform if allowed.
	When a composite is used in a demo, a suitable origin is selected from a demo to attach it to. It is
	possible to share the same origin, and for them to be moved independently if needed. An origin can
	also define other special attributes like start position, orientation, field of view, near and far planes.
	By default, origins are fixed for each demo, although vizmultiscript is able to task switch them in
	and out for separate demos.
	"""

	def __init__(self, inobj=None, pos=None, euler=None, posScale=None, oriScale=None, parent=None, fov=None, collision=None, viewtype=None, description="", name=""):
		global __alloc_vuorigin_seq
		if viewtype is None:
			FatalError("The viewtype attribute for each VUOrigin must be specified")

		if inobj is None:
			group = viz.addGroup()
		else:
			group = inobj

		viz.VizNode.__init__(self, group.id)
		if pos is not None:
			self.setPosition(pos)
		if euler is not None:
			self.setEuler(euler)
		self.viewtype    = viewtype
		self.description = description
		self.name        = name
		if parent is not None:
			self.parent(parent)
		self.sequence    = __alloc_vuorigin_seq
		__alloc_vuorigin_seq += 1

		# Deal with special VizWindow attributes that we actually modify and need to restore
		self.fov = fov
		self.saved_fov = None
		self.posScale = posScale
		self.oriScale = oriScale
		self.collision = collision

		# Sanity check to make sure the input data is valid
		if collision is not None:
			import vizmat
			if vizmat.Distance(self.getPosition(viz.ABS_GLOBAL), [0,0,0]) > 0.01:
				FatalError("Collision detection cannot be activated if the start position is not the origin")
			if vizmat.Distance(self.getEuler(viz.ABS_GLOBAL), [0,0,0]) > 0.01: # Not technically correct for an angle, but just checking to see if it is 0,0,0
				FatalError("Collision detection cannot be activated if the start orientation is not the default")
			if viewtype is not VT_DESKTOP and viewtype is not VT_DESKTRACK:
				FatalError("Collision detection cannot be activated except in desktop modes at this time")
			if parent is not None:
				FatalError("Collision detection cannot be activated when the origin uses a parent transform")
			if posScale is not None or oriScale is not None:
				FatalError("Collision detection cannot be activated when position or orientation scale is in use")

	def copy(self):
		onew = VUOrigin(pos=self.getPosition(), euler=self.getEuler(), posScale=self.posScale, oriScale=self.oriScale, fov=self.fov, collision=self.collision, viewtype=self.viewtype, description=self.description, name=self.name)
		parentlist = self.getParents()
		if len(parentlist) > 1:
			FatalError("An input VUOrigin object to be copied should not be able to have more than one parent, found %d parents" % len(parentlist))
		elif len(parentlist) == 1:
			onew.parent(parentlist[0])
		return onew

	def apply(self, composite):
		"""
		This method takes special attributes, and applies them to the supplied composite. We also save attributes that we modify for later restoration.
		In many cases this method will do nothing, since only the fov attribute at this time needs to be processed here.
		"""
		if self.fov is not None: # If no fov override is set, no need to do anything to the fov (this is the standard case)
			# Make sure that the composite only has one window. If it has more than one, like a CAVE, you cannot change the field of view anyway!
			windowlist = composite.getWindowList()
			if len(windowlist) > 1:
				FatalError("Cannot apply special attributes to a composite containing multiple windows")
			if len(windowlist) == 0:
				FatalError("Cannot apply special attributes to a composite with no windows")
			window = windowlist[0]

			# Save the current state firstly
			if self.saved_fov is not None:
				FatalError("apply() method has been called without previous restore() call, which should not occur")
			self.saved_fov = window.getVerticalFOV()

			# Now set the new state
			window.fov(self.fov, window.getAspectRatio())

		if self.posScale is not None: # Some demos request changes to the scaling factors of the composite tracker
			composite.setPosScale(self.posScale)

		if self.oriScale is not None: # Some demos request changes to the scaling factors of the composite tracker
			composite.setOriScale(self.oriScale)

		if self.collision is not None: # Some demos set collision mode and this is set to the step size
			composite.setCollision(state=True, stepsize=self.collision)

	def restore(self, composite):
		"""
		This method restores back the original attributes of the window that were saved previously
		"""
		if self.fov is not None: # If no fov override is set, no need to do anything to the fov (this is the standard case)
			# Make sure that the composite only has one window. If it has more than one, like a CAVE, you cannot change the field of view anyway!
			windowlist = composite.getWindowList()
			if len(windowlist) > 1:
				FatalError("Cannot apply special attributes to a composite containing multiple windows")
			if len(windowlist) == 0:
				FatalError("Cannot apply special attributes to a composite with no windows")
			window = windowlist[0]

			# Check that we are doing this at the right time
			if self.saved_fov is None:
				FatalError("restore() method has been called with no previous apply() call, which should not occur")

			# Restore the FOV state
			window.fov(self.saved_fov, window.getAspectRatio())
			self.saved_fov = None

		if self.posScale is not None: # If a demo has reprogrammed the position scale, then make sure we reset it back to the defaults here
			composite.setPosScale()

		if self.oriScale is not None: # If a demo has reprogrammed the orientation scale, then make sure we reset it back to the defaults here
			composite.setOriScale()

		if self.collision is not None: # Turn collision mode off by default here
			composite.setCollision(state=False)


def allocVUOrigin(olist, viewtype=VT_DEFAULT):
	global _VUOrigin__alloc_vuorigin_seq

	# If the list contains any legacy items like VizNode objects then we should fix them up to have other attributes we need
	for i in range(0,len(olist)):
		o = olist[i]
		if not hasattr(o, "sequence"):
			if i == 0:
				newvt = VT_DEFAULT # First node is always the default user
			else:
				newvt = VT_VIEWER # Other nodes are usually external viewpoints
			# print "Promoting legacy viewpoint node %d of %d to %s" % (i+1, len(olist), viewtype)
			onew = VUOrigin(o, viewtype=newvt) # Create new upgraded object
			olist[i] = onew # Replace existing with new object

	# Prepare variables for our search
	found = None
	foundseq = _VUOrigin__alloc_vuorigin_seq + 1 # Make it so we default to one larger than all available values
	foundofs = 0

	# Traverse the list, and find all elements with matching viewtype. Of those elements, find the one with the smallest sequence value
	count = 0
	for o in olist:
		if o.viewtype == viewtype:
			if o.sequence < foundseq:
				found = o
				foundseq = o.sequence
				foundofs = count
			count += 1

	if found is None:
		viz.logNotice("allocVUOrigin: Could not find any viewpoints of type %s in view point list, falling back to generic viewpoints" % viewtype)
		count = 0
		for o in olist:
			if o.viewtype == VT_DEFAULT:
				if o.sequence < foundseq:
					found = o
					foundseq = o.sequence
					foundofs = count
				count += 1
		if found is None:
			FatalError ("Could not find any viewpoints of type %s or fallback type %s in view point list" % (viewtype, VT_DEFAULT))

	# Yes, increment the sequence number and return it
	found.sequence = _VUOrigin__alloc_vuorigin_seq
	_VUOrigin__alloc_vuorigin_seq += 1
	copy = found.copy()
	# print "VUOrigin: Returning copy of element %d of %d of type [%s] Copy=%s" % (foundofs+1, count, viewtype, copy)
	return copy




# Global variable to store the manager in, this should be accessed using getManager()
global_manager = None

def getManager():
	"""
	Global way to get access to the manager class, so that scripts can find out about the
	manager that is controlling the simulation, and make changes, etc. This method hides the
	way we actually get access to this. Some code imports vizuniverse directly into its own
	namespace, and so we need to use a global variable that is not in vizuniverse to do this.
	The value returned here is None if no manager has been created yet.
	"""
	return global_manager


# This class is a manager, you give it all of your composite trackers and you can pick which view to use
# You can also specify the type of HMD to use and this code will configure it up for you as well in cluster mode
class VUManager (viz.EventClass):
	def __init__(self, debugkey=None):
		self.list_comp = []
		viz.EventClass.__init__(self)				   # Initialize the base class
		self.setupGUI(debugkey)						   # Set up the GUI so that our callbacks will work
		self.callback(viz.TIMER_EVENT,self.refreshGUI) # Create a callback to our own event class function
		self.starttimer(0,0,viz.PERPETUAL)             # Start a perpetual timer for this event class, make it run every frame so our FPS stats are correct

		self._topView = viz.addView() # Define a viewpoint to use if we are in cluster mode and there are more viewers than composite trackers
		self._topView.eyeheight (0)
		self._topView.collision (viz.OFF)
		self._topView.setPosition (0,50,0) # 50m above ground level
		self._topView.lookat (0,0,0)

		self.hands_visible = True # Hands are always visible by default
		self.handdetectlist = []

		self.manual_cluster = False # This flag is set when the user controls the cluster masks, otherwise we just assign machine 1 to composite 1, etc

		self.dictionary = {} # Configure an empty dictionary of values that we keep references to in here

	def refreshGUI(self, num):
		i = 0
		output = "Render Performance: %.0f fps\n" % (1/viz.elapsed()) # Show the frame rate in the status window
		while i < len(self.list_comp):
			comp = self.getComposite(i)
			output += "[#%d-%s] %s" % (i+1, comp.getName(), comp.getCompType())
			if len(comp.getViewType()) > 0:
				output += "View:%s\n" % comp.getViewType()
			else:
				output += "\n"
			output += self.list_comp[i].getDebug()
			i = i + 1
		self.msg.message (output)

	def setupGUI(self, key): # Setup the pop up dialog that we draw when the tracker is enabled
		self.msg = vizinfo.add ("")
		self.msg.title ("Tracker Manager Status")
		self.msg.drag (1)
		self.msg.visible (0)
		self.msg.translate   (0.01, 0.97)
		self.msg.scale       (0.75, 0.75)
		self.msg.alignment (vizinfo.UPPER_LEFT)
		self.msg.bgcolor     (0.75, 0, 0, 0.4)
		self.msg.bordercolor (0.5,  0, 0, 0.4)
		self.msg.titlebgcolor(0.5,  0, 0, 0.4)
		if key is not None:
			vizact.onkeydown (key, self.toggleGUI)

	def toggleGUI(self):
		self.msg.visible (viz.TOGGLE)


	def addComposite(self, comp, name=None, viewtype=None):
		if name is not None:
			comp.setName(name)
		if viewtype is not None:
			comp.setViewType(viewtype)
		if len(comp.getName()) is 0:
			FatalError("Cannot add a composite object to a manager that does not have a name")
		self.list_comp.append (comp)

	def getCompositeList(self):
		return self.list_comp

	def getComposite(self, idx):
		return self.list_comp[idx]

	def getNumComposites(self):
		return len(self.list_comp)

	def getNumCompositeWindows(self):
		return len(self.getCompositeWindowList())

	def getCompositeWindowList(self):
		winlist = []
		for comp in self.getCompositeList():
			winlist += comp.getWindowList()
		return winlist

	def getMovableNode(self, idx):
		"""Return back a reference to the movable node for a composite, which can be used to push the specified user around"""
		return self.getComposite(idx).getMovableNode()

	def assignViewpointsComposites(self, viewlist):
		"""Take in a list of VUOrigin viewpoints, or VizNode objects, and assign them as parents to the movable objects for each composite"""
		count = 0
		for c in range(0,self.getNumComposites()):
			comp = self.getComposite(c)
			# If the composite is marked as having a fixed parent, then do not adjust it
			if comp.isMovableFixed():
				viz.logNotice("Composite %s is attached to a fixed origin parent, so will not adjust the viewpoint" % comp.getName())
			else:
				# Allocate a viewpoint from the available list based on the composite type
				vuorigin = allocVUOrigin(viewlist, self.getComposite(c).getViewType())
				comp._setOriginParent (vuorigin)
				# Assign special attributes stored in the VUOrigin objects
				vuorigin.apply(comp)

	# Always return the main user here, since this controls things like detecting the user location for walking over the pit
	# This is the recommended way to get the current user location instead of using viz.MainView, since it returns the location
	# of the user, and not where an auto-fly may have put the user's current view
	def getDefaultView(self):
		return self.getComposite(0).getViewpointSource()

	# Takes in all the composites, and creates a tiled set of sub-windows showing each window that exists in the system, a complete summary
	thumblist = []
	thumbinit = False
	def toggleThumbnailViews(self, resizeOriginals=False):
		if self.thumbinit is False:
			# Calculate a suitable thumbnail size, don't let them get too large
			thumbsize = 1/float(self.getNumCompositeWindows() + 1) # Add one for MainWindow
			if thumbsize > 0.2:
				thumbsize = 0.2
			# Create a thumb window for each composite window that we have
			wincount = 0
			for count in range(0, self.getNumComposites()):
				for eachwin in self.getComposite(count).getWindowList():
					if hasattr(eachwin, "noThumb") and eachwin.noThumb is True:
						continue
					window = addVUVizWindow()
					window.copyVUVizWindow(eachwin)
					window.setSize(thumbsize, thumbsize)
					window.setPosition([1-thumbsize, 1-wincount*thumbsize])
					window.visible(0) # Set to 0 so we can toggle it on later on below
					eachwin.addTarget(window)
					self.thumblist.append(window)

					if resizeOriginals: # Test that our cloned windows are actually good copies with nothing left out, for debug only
						viz.logWarn("Warning! During clone for thumbnails, resized input windows into tiles as well - this should only be used during debugging")
						if viz.MainWindow.id is not eachwin.id:
							# Note that we skip resizing viz.MainWindow so that it always uses the full display area
							eachwin.setSize(thumbsize, thumbsize)
							eachwin.setPosition([0, 1-wincount*thumbsize])
							eachwin.visible(1)
					wincount += 1
			self.thumbinit = True

		# Decide if we toggle on or off the thumbnails
		for each in self.thumblist:
			each.visible(viz.TOGGLE)


	# Returns back a list of all hand objects here, useful for writing demos that just want to use every hand available
	def getHandList(self):
		i = 0
		output = []
		while i < len(self.list_comp):
			lh = self.list_comp[i].getLeftHand()
			if lh is not None:
				output.append (lh)
			rh = self.list_comp[i].getRightHand()
			if rh is not None:
				output.append (rh)
			misc = self.list_comp[i].getMiscHands()
			for each in misc:
				output.append (each)
			i = i + 1
		# print "Returned back %d hands currently available" % len(output)
		return output

	# Controls hand visibility, 0 is hide, 1 is show, 2 is automatic, -1 is cycle between them
	def changeHandListVisible(self, state=-1):
		if state == -1:
			self.hands_visible += 1
			if self.hands_visible == 3:
				self.hands_visible = 0
		else:
			self.hands_visible = state

		if self.hands_visible == 2 and len(self.handdetectlist) == 0:
			viz.logNotice("No automatic hand list initialized, so skipping to forced off mode")
			self.hands_visible = 0

		if self.hands_visible == 0:
			viz.logNotice("Changing hand visibility to forced off")
			for each in self.getHandList():
				each.visible(0)
			for each in self.handdetectlist:
				each.disable() # Disable the auto-detector
		elif self.hands_visible == 1:
			viz.logNotice("Changing hand visibility to forced on")
			for each in self.getHandList():
				each.visible(1)
			for each in self.handdetectlist:
				each.disable() # Disable the auto-detector
		elif self.hands_visible == 2:
			viz.logNotice("Changing hand visibility to automatic")
			for each in self.getHandList():
				each.visible(1) # Make sure the hands are visible by default, they should always be in this state when created
			for each in self.handdetectlist:
				each.enable() # Activate the auto-detector
				each.resetOff() # By default leave the hands off until they move, prevents hands being visible until tracking works

	# Must call this method to initialize automatic hand visibility controls
	def initAutoHandHide(self, timeout=0, posthresh=0, orithresh=0):
		handlist = self.getHandList()
		self.handdetectlist = []
		for eachhand in handlist:
			handdetector = VUDetectMotion (eachhand, timeout, posthresh, orithresh, cb=eachhand)
			handdetector.disable() # Disable this code by default, only enabled in state 2 above
			self.handdetectlist.append (handdetector)
		# Change into automatic hand mode if we call this function
		self.changeHandListVisible()




	# Convert a cluster node number into the mask needed for Vizard
	# Note that 1 is MASTER, 2 is CLIENT1, 4 is CLIENT2, 8 is CLIENT3, 16 is CLIENT4, etc, there are no constants for CLIENT10 and higher defined either
	def _vizClusterMask(self,id):
		assert (id >= 0)
		return 2**id # 2 raised to the power of the id number

	# Take a hostname and convert it into a cluster client id value, it logs out messages if anything is wrong
	# Note that 0 is returned if the hostname is not part of the cluster, this is an error
	def _vizGetClientID(self,hostname):
		if hostname.lower() == "localhost":
			return viz.MASTER
		else:
			id = viz.cluster.getClientID(hostname)
			if id <= 0:
				viz.logWarn("Warning! Could not find cluster host %s, so commands for this host will be ignored" % hostname)
			return id

	# If hostnames do not exist for setHostDisplay, should this be fatal or not?
	cluster_fatal = False
	def setClusterFatal(self, value):
		self.cluster_fatal = value

	# Method to configure a cluster node to control certain windows
	host_display = []
	def setHostDisplay(self, hostname, window, commands):
		self.manual_cluster = True
		self.host_display.append([hostname, window, commands])

	def _addLinkLabel(self,text,obj):
		text = viz.add(viz.TEXT3D, text) # Create the text label
		text.setScale([0.1,0.1,0.1])
		text.alignment(viz.TEXT_LEFT_TOP)
		text.billboard(viz.BILLBOARD_VIEW) # Use billboarding so it is always visible
		label = viz.link (obj, text, srcFlag=viz.ABS_GLOBAL)
		label.setMask(viz.LINK_POS) # Only update the position, not the orientation
		label.postTrans ([0,0.3,0]) # Put the label slightly above the user's head
		return text

	def setGlobalClip(self,near=0.01,far=10000): # Near = 1 cm, Far = 10 km
		""" Gives the ability to override the automatic clip plane detection, needed when using large models """
		viz.logNotice("Setting global clipping plane for all windows to near=%f, far=%f" % (near, far))
		for comp in self.getCompositeList():
			for win in comp.getWindowList():
				win.clip(near,far)
			if hasattr(comp, "cavedef"):
				comp.cavedef.setNearPlane(near)
				comp.cavedef.setFarPlane(far)

	label_list = []
	def toggleCompositeLabels(self):
		"""Add labels to all the participants, and then able to toggle them on and off"""
		if len(self.label_list) is 0:
			compid = 0
			for compid in range(self.getNumComposites()):
				composite = self.getComposite(compid) # Find the composite information
				compname = composite.getName()
				viewsrc = composite.getAvatar().getHeadBone()
				text = self._addLinkLabel(compname, viewsrc) # Create the text label and link to it
				self.label_list.append(text)
		else:
			for text in self.label_list:
				text.visible(viz.TOGGLE)

	hand_label_list = []
	def toggleCompositeHandLabels(self):
		"""Add labels to all hands and tools, and then able to toggle them on and off"""
		if len(self.hand_label_list) is 0:
			compid = 0
			while compid in range(self.getNumComposites()):
				composite = self.getComposite(compid) # Find the composite information
				compname = composite.getName()
				lh = composite.getLeftHand()
				if lh is not None:
					self.hand_label_list.append(self._addLinkLabel(compname+"-LH", lh))
				rh = composite.getRightHand()
				if rh is not None:
					self.hand_label_list.append(self._addLinkLabel(compname+"-RH", rh))
				misc = composite.getMiscHands()
				mcount = 0
				for each in misc:
					name = "%s-M%d" % (compname, mcount)
					self.hand_label_list.append(self._addLinkLabel(name, each))
					mcount += 1
				compid += 1
		else:
			for text in self.hand_label_list:
				text.visible(viz.TOGGLE)

	def get(self, value):
		"""Return back dictionary entry"""
		return self.dictionary[value]

	def prepareDictionary(self):
		"""Method called during go() which configures the dictionary with references to interesting objects"""
		compid = 0
		self.dictionary["handlist"] = self.getHandList()
		for compid in range(0,self.getNumComposites()):
			comp = self.getComposite(compid)
			# Set dictionary entries for the composite
			comp.dictionary["name"]      = comp.getName()							# The name of this composite object
			comp.dictionary["lefthand"]  = comp.getLeftHand()						# Reference to the left hand if it exists, is both a VizNode and a hand object
			comp.dictionary["righthand"] = comp.getRightHand()						# Reference to the right hand if it exists, is both a VizNode and a hand object
			comp.dictionary["leftfoot"]  = comp.getTracker(comp.LFOOT, fatal=False)	# Reference to the final location of the user's left foot, represented as an empty VizNode
			comp.dictionary["rightfoot"] = comp.getTracker(comp.RFOOT, fatal=False)	# Reference to the final location of the user's right foot, represented as an empty VizNode
			comp.dictionary["movable"]   = comp.getMovableNode()					# Reference to the movable platform that can be used to push the user and all their parts around
			comp.dictionary["viewpoint"] = comp.getViewpointSource()				# Reference to the output location of the user's viewpoint
			comp.dictionary["avatar"]    = comp.getAvatar().getRawAvatar()			# Reference to the 3D model of the user's body, could be a VizAvatar or a VizNode
			for trackid in range(0,len(comp.tracker_input)): # Traverse through all trackers in a composite
				tracker = comp.getRawTracker(trackid, fatal=False) # Grab a reference to the tracker container for each body part
				if tracker is None:
					comp.dictionary["input%d"  % trackid] = None									# No input tracker available
					comp.dictionary["link%d"   % trackid] = None									# No link available since there was no input
					comp.dictionary["update%d" % trackid] = None									# No link update function since there is no link
					comp.dictionary["output%d" % trackid] = comp.getTracker(trackid, fatal=False)	# Reference to the output, this may be a tracker if using 2D mouse and overrideTracker()
				elif isinstance(tracker, viz.VizBone):
					comp.dictionary["input%d"  % trackid] = tracker									# Reference to the bone generating this tracker
					comp.dictionary["link%d"   % trackid] = None									# There is no individual link available to transform for an avatar
					comp.dictionary["update%d" % trackid] = None									# No link update function since there is no link
					comp.dictionary["output%d" % trackid] = comp.getTracker(trackid, fatal=False)	# The final location for this body part, after all links and transform nodes are applied
				else:
					comp.dictionary["input%d"  % trackid] = tracker.getInput()						# Reference to the input data used to supply this tracker
					comp.dictionary["link%d"   % trackid] = tracker.getLink()						# Reference to the link added for each tracker
					comp.dictionary["update%d" % trackid] = tracker.getLinkUpdate()					# Reference to the link update vizact.onupdate() used by the link
					comp.dictionary["output%d" % trackid] = comp.getTracker(trackid, fatal=False)	# Reference to the final tracker value, after all links and transform nodes are applied

			# Set entries within the manager now
			self.dictionary["comp%d" % compid] = comp
			for key,value in comp.dictionary.items():
				self.dictionary["comp%d:%s" % (compid, key)] = value

			# If this is comp0 then we should set global entries as well
			if compid is 0:
				for key,value in comp.dictionary.items():
					self.dictionary["%s" % key] = value

		# Done, debug it out if desired
		#for key,value in sorted(self.dictionary.items()):
		#	print "Key = %-20s   Value = %s" % (key, value)


	window_default = 1
	def debugDisplayWindow(self, ofs=None):
		"""Method used for debugging our viewpoints, it should not be used except for software testing"""

		# If no argument is supplied, then call the go() method to reset everything
		if ofs is None:
			self.go()
			return

		# Build up a list of all windows
		winlist = self.getCompositeWindowList()

		# Calculate a new default window offset
		if ofs < 0:
			self.window_default -= 1
		elif ofs >= 32: # Cannot support more than 32 windows
			self.window_default += 1
		else:
			self.window_default = ofs

		# Adjust the window if necessary to make it fit within the number of windows we have
		if self.window_default < 0:
			self.window_default = len(winlist)-1
		if self.window_default >= len(winlist):
			self.window_default = 0
		viz.logNotice("Debug: Setting display window on all cluster nodes to window %d" % self.window_default)

		# Now disable them all, and activate only the one we want
		for win in winlist:
			win.visible(0)
		winlist[self.window_default].visible(1)

	# Method that takes all of our composite objects, and makes them available via VRPN. Useful with the PPT VRPN import plugin and the mocap plugin.
	def startVRPNServer(self):
		# Empty tracker to use whenever we get a None tracker defined
		empty = viz.addGroup()

		# Get ready to create VRPN server objects
		vrpn = viz.add('vrpn7.dle')

		# Traverse each composite object we have
		for compid in range(0, self.getNumComposites()):
			# Lookup the composite
			comp = self.getComposite(compid)
			compname = comp.getName()

			# Create a server for this composite
			servname = "Comp%d" % compid
			server = vrpn.addTrackerServer (servname)
			viz.logNotice("Created VRPN server %s with 6 trackers, based on composite %s" % (servname, compname))

			# Now add each tracker we have to the composite server, 6 is for each of the body parts we track
			for id in range(0,6):
				tracker = comp.getTracker(id,fatal=False)
				if tracker is None:
					tracker = empty
				server.setTracker(tracker, id)

	
	# This method should be called by all scripts, it basically give the VUManager control over everything, and any
	# error checking or other tests could be performed here. We set up some sane defaults here as well, you can override
	# them later if you want, but these are good for most scripts to use. 
	def go(self, mode=0):
		global global_manager

		modestr = ""
		if mode is not 0:
			modestr = "%d" % mode
		viz.logNotice("VUManager.go(%s) method called, calling viz.go(%s), configuring clustering" % (modestr, modestr) )

		# Takes the supplied VUManager object and assigns it to a globally accessibly handle so that other scripts can easily use it
		# Scripts will not need to access the manager unless they want to get access to the hands or other internals. Note that code
		# should always use the getManager() call to access this, and should never look at this variable directly!
		global_manager = self
		

		# Do not modify viz.MainWindow or viz.MainView, by default this code configures it to be set to the first composite created
		# Note that while these are provided, you should not be using them because things like viz.MainView are affected by
		# auto-fly mode, and you can only access the first composite user. So you should use the vizuniverse manager methods
		# instead to get information about the participants.

		# We support the ability to specify cluster masks in two ways. The old method was to specify cluster masks for
		# each composite, which mapped one composite to one viewpoint and display. If the user has specified any display
		# masks, then we will still implement them. Also, we support a flag called seeself, which we implement here as
		# well, using window masks which is a much smarter way.
		if viz.cluster:
			viz.logNotice("Clustering mode detected, will configure cluster masks and displays")
		else:
			viz.logNotice("Single machine detected, will only configure the first composite")
		if self.manual_cluster:
			viz.logNotice("Manual clustering detected, will only assign according to setHostDisplay commands")
		else:
			viz.logNotice("Automatic legacy clustering detected, composites will be assigned in order to available clients")
		legacy = False
		clusterid = 0
		# Traverse all composite objects
		for compid in range(self.getNumComposites()):
			composite = self.getComposite(compid)
			compname = composite.getName()

			# If the seeself flag is set to False, then we need to implement a mask so the avatar can be hidden from this composite
			av = composite.getAvatar()
			if av.getSeeSelf() is False:
				av.maskid = viz.addNodeMask() # Allocate a mask, store it in the avatar object for future reference if needed
				viz.logNotice("Composite %d %s contains avatar seeself=False options, implemented using window cull mask id %d" % (compid, compname, av.maskid))
				av.getRawAvatar().setMask(av.maskid,mode=viz.MASK_REMOVE,op=viz.OP_ROOT) # Must use OP_ROOT to propagate to all avatar child objects
			elif av.getSeeSelf() is True:
				pass # Do nothing
			else:
				# seeself is a link to another avatar, so lets copy over the mask from that source object
				if hasattr(av.getSeeSelf().getAvatar(), "maskid"):
					av.maskid = av.getSeeSelf().getAvatar().maskid # Copy the mask from the source object
					viz.logNotice("Composite %d %s contains avatar seeself=linked(False) options, implemented using linked window cull mask id %d" % (compid, compname, av.maskid))
					av.getRawAvatar().setMask(av.maskid,mode=viz.MASK_REMOVE,op=viz.OP_ROOT) # Must use OP_ROOT to propagate to all avatar child objects
				else:
					FatalError ("Composite %d %s contains avatar seeself=linked options, but the target has no maskid attribute, so the target is configured for seeself=True (which is not usable with a CAVE) or the order of CAVE user and box is in the incorrect order" % (compid, compname))

			# Traverse all windows within this composite, most will only have one, CAVEs can have many windows
			for window in composite.getWindowList():
				# Check that the clusterid fits within Vizard limits
				if clusterid >= 32:
					FatalError("The number of windows allocated %d exceeds the Vizard limit of 32, reduce the number of composite objects" % (clusterid+1))

				# By default, disable all windows, and we only enable them if decided below
				window.visible(0)

				# Decide if we will do anything, or just collect legacy flag information. If we are in non-cluster
				# mode, we don't actually change anything for the other displays, we read them but that is it
				config = True
				if not viz.cluster and compid > 0:
					config = False

				# If the avatar is marked as hidden from self in some way, then we need to suppress it for each window here
				if av.getSeeSelf() is not True:
					# Apply the cull mask, we overwrite the original value
					window.setCullMask(av.maskid)

				# Set the mask for this cluster id
				if config:
					viz.cluster.setMask(self._vizClusterMask(clusterid))

				# Do the configuration of display specific properties here
				cmds = composite.getConfigDisplayCommands()
				if len(cmds) > 0:
					legacy = True
					viz.logNotice("Composite %d %s contains specific legacy cluster commands: %s" % (compid, compname, cmds.replace("\n", "\\n "))) # Does not change the exec'd string
					if config:
						exec (cmds)

				# The setHostDisplay() method can be used to configure manual mappings for each window, and
				# is the preferred way of doing this. However, if you do not call this method, then it is
				# assumed that each composite maps to the matching cluster id, so we will configure the
				# windows that way.
				if not self.manual_cluster:
					viz.logNotice("Setting window visible for composite %d %s, cluster id %d" % (compid, compname, clusterid))
					if config:
						window.visible(1)

				# We are done, reset the cluster mask back to normal
				if config:
					viz.cluster.setMask(viz.ALLCLIENTS)
				clusterid += 1

		# If we are in legacy mode, then the user should not be calling setHostDisplay. You can either do automatic
		# cluster assignment, or do it yourself, but it is confusing to do it both ways at the same time.
		if len(self.host_display) > 0 and legacy:
			FatalError ("Detected legacy clustering commands which conflict with new setHostDisplay commands, this is not possible")

		# If the user called setHostDisplay anywhere, then we need to play these commands back now to enable any needed windows
		count = 0
		for entry in self.host_display:
			hostname = entry[0] # The entry is just an array, so unpack the values stored in it
			window   = entry[1]
			commands = entry[2]
			if viz.cluster or count is 0: # We only do these commands with clustering, or if this is the first call with non-clustering
				clientid = self._vizGetClientID(hostname)
				if clientid == 0 and self.cluster_fatal is True:
					FatalError ("The hostname %s was specified to be part of the cluster but is not present, and is required for operation" % hostname)
				viz.cluster.setMask(clientid) # Limit to this client only
				window.visible(1) # Enable this window on this cluster client only
				viz.logNotice("Configuring hostname %s with window %s and display commands: %s" % (hostname, window, commands))
				WINDOW = window # Set the WINDOW variable so that the exec(commands) can access it
				exec (commands)
				viz.cluster.setMask(viz.ALLCLIENTS) # Change back to default all clients mode
			count += 1 # Done with this entry

		# If clustering is not on, then we always need to enable the first window in the first composite so we can see something
		if not viz.cluster:
			winlist = self.getCompositeWindowList()
			if len(winlist) > 0:
				winlist[0].visible(1)
			else:
				FatalError ("Could not find a single window when traversing all composites, which is not a valid configuration")

		# Now start up the graphics rendering, this must be done after all options that setup the display
		viz.go(mode)

		# Disable mouse navigation, but the cursor is still visible
		viz.mouse (viz.OFF)

		# Enable the key handler class so we can detect keystrokes + modifier key combinations
		SpecialKeyHandler()

		# Enable automatic hand show/hide mode, don't check orientation
		self.initAutoHandHide(timeout=AUTOHAND_TIME, posthresh=AUTOHAND_POS)

		# The Alt-H combination controls hand visibility settings, we can hide them if they are annoying or not working right
		onkeydownspecial ('h', self.changeHandListVisible)

		# Prepare the dictionary now that all the composites are initialized
		self.prepareDictionary()




# Uses a keyboard and mouse to control a user in the scene
# Also creates a static external viewpoint that follows the user
def createDesktopManager(mousehand=True, extraviews=0, joystickDrivers=False, collision=False, fixedHeight=False):
	# Create a manager, the left shift key activates it
	manager = VUManager(debugkey=viz.KEY_SHIFT_L)

	if mousehand is True or mousehand is 2:
		# If we want a hand driven by the mouse, we need to add a virtual hand mapped to the mouse movements

		# Create a keypad to drive the user around, turn it on by default
		keypad = VUTrackerNumericKeypad (startpos=[0,0,0], starteuler=[0,0,0])

		comp = VUCompositeTrackers()
		comp.addDriverNode (keypad)
		if joystickDrivers:
			comp.addDriverNode (VUTrackerJoystick())
		comp.storeTracker (comp.HEAD, VUTrackerVirtual(type="Keyboard", startpos=[0,1.8,0], fixedHeight=fixedHeight))
		comp.finishTrackers()
		comp.defineViewpoint()
		comp.copyHandOriFromHead ()
		if mousehand == 2:
			comp.overrideTracker(comp.LHAND, VUTrackerMouse2D(ofs2D=[-0.05,0])) # Create two hands, one centered about the mouse, and the other about the center of the display
			comp.overrideTracker(comp.RHAND, VUTrackerMouse2D(ofs2D=[+0.05,0])) # This is useful for testing if programs can support two hands properly or not
			comp.createLeftHand  (hand.MultiInputSensor (pinchButtons=[viz.KEY_PAGE_UP,   viz.MOUSEBUTTON_LEFT],  fistButtons=[viz.MOUSEBUTTON_MIDDLE]))
			comp.createRightHand (hand.MultiInputSensor (pinchButtons=[viz.KEY_PAGE_DOWN, viz.MOUSEBUTTON_RIGHT], fistButtons=[viz.MOUSEBUTTON_MIDDLE]))
		else:
			comp.overrideTracker(comp.RHAND, VUTrackerMouse2D()) # Override internals to use mouse tracker with direct 3D output, use right hand so that scripts don't work with just getHandList()[0]
			comp.createRightHand (hand.MultiInputSensor (pinchButtons=[viz.KEY_PAGE_UP,viz.KEY_PAGE_DOWN,viz.MOUSEBUTTON_LEFT,viz.MOUSEBUTTON_RIGHT], fistButtons=[viz.MOUSEBUTTON_MIDDLE]))
		#comp.createAvatarSimple (viz.add ('biohead_eyes.vzf', scale=[1,1,1])) # Use a simple head object model, scaled 1:1
		#comp.createAvatarNone() # Use this if you don't want any avatar at all
		comp.createAvatarSteve(seeself=False) # Use this for the Steve avatar
		#comp.createAvatarFixedBody (viz.add ('vcc_male.cfg'), groundlevel=True, seeself=True) # Use a full avatar, fixed to the ground
		comp.setViewType (VT_DESKTOP) # This is a desktop tester, so use a suitable desktop viewpoint if available
		if collision:
			comp.setCollision() # Enable collision detection to allow walking up steps if configured
		manager.addComposite (comp, "MainUser")
		maintracker = manager.getComposite(0)
	else:
		# Standard desktop case, just keyboard and mouse motions, no hands

		# Create a keypad to drive the user around, but leave it off by default, since the tracker below can do most of what we want
		keypad = VUTrackerNumericKeypad (startpos=[0,0,0], starteuler=[0,0,0])

		comp = VUCompositeTrackers()
		comp.addDriverNode (keypad)
		if joystickDrivers:
			comp.addDriverNode (VUTrackerJoystick())
		comp.storeTracker (comp.HEAD, VUTrackerVirtual(type="MouseKeyboard", startpos=[0,1.8,0], fixedHeight=fixedHeight))
		comp.finishTrackers()
		comp.defineViewpoint()
		#comp.createAvatarSimple (viz.add ('biohead_eyes.vzf', scale=[1,1,1])) # Use a simple head object model, scaled 1:1
		#comp.createAvatarNone() # Use this if you don't want any avatar at all
		comp.createAvatarSteve(seeself=False) # Use this for the Steve avatar
		#comp.createAvatarFixedBody (viz.add ('vcc_male.cfg'), groundlevel=True, seeself=True) # Use a full avatar, fixed to the ground
		comp.setViewType (VT_DESKTOP) # This is a desktop tester, so use a suitable desktop viewpoint if available
		if collision:
			comp.setCollision() # Enable collision detection to allow walking up steps if configured
		manager.addComposite (comp, "MainUser")
		maintracker = manager.getComposite(0)

	# We don't always add external viewers, not much use in a standalone demo
	if extraviews >= 1:
		# Add a fixed viewer that always looks towards the main avatar 0 viewpoint object
		compd = VUCompositeTrackers()
		compd.storeTracker (compd.HEAD, VUTrackerGeneric(pos=[0,1.8,0]))
		if joystickDrivers:
			compd.addDriverNode (VUTrackerJoystick())
		compd.finishTrackers()
		compd.defineViewpoint()
		compd.createAvatarSteve(seeself=False) # Use this for the Steve avatar
		#compd.createAvatarNone() # Use this if you don't want any avatar at all
		#compd.createAvatarSimple (viz.add ('biohead_eyes.vzf', scale=[1,1,1]), seeself=False) # Use a simple head object model, scaled 1:1
		#compd.createAvatarFixedBody (viz.add ('vcc_male.cfg'), groundlevel=True, seeself=False) # Use a full avatar, fixed to the ground
		VUControlObjectLookAt (compd.getViewpointSource(), maintracker.getViewpointSource()) # LookAt is a special tracker and needs to be done this way
		compd.setViewType (VT_VIEWER)
		manager.addComposite (compd, "LookAt-Viewer")

	# If the user presses right-shift then they will get an external viewpoint watching the user from a variety of locations
	ev = VUExternalViewpoint(target=maintracker.getViewpointSource())

	# Create a small info box showing how to use this interface, good for new users
	if mousehand is True:
		info = vizinfo.add("""
Scroll-lock activates moving via keyboard
Use the numeric keypad to move around
Use the mouse to control the left hand
Scroll wheel moves the hand back and forth
Left mouse button grabs objects
F5/F6 controls auto-fly mode
Left shift activates debugging output
Righ shift activates external views""")
	else:
		info = vizinfo.add("""
Use the mouse and arrow keys to move around
Use the mouse to control the left hand
F5/F6 controls auto-fly mode
Left shift activates debugging output
Right shift activates external views""")

	info.title ("User Instructions")
	info.drag (1)
	info.alignment (vizinfo.LOWER_RIGHT)
	info.translate (0.99, 0.01)
	info.scale (0.75, 0.75)
	vizact.onkeydown (' ', info.visible, viz.TOGGLE)
	manager.infoWindow = info

	# Done
	return manager




# Things to do only when we run this script directly
if __name__ == "__main__":

	# Allocate a manager for testing, use the standard keyboard routines, create VRPN server as well
	manager = createDesktopManager (mousehand=True, collision=True, extraviews=1, fixedHeight=False, joystickDrivers=True)
	manager.go()
	manager.startVRPNServer()

	# Load an environment to look at
	viz.add ('gallery.ive')
