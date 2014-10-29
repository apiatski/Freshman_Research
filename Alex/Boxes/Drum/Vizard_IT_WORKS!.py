import viz
import viztask
import math
import vizinfo
import vizcam
import vizact
import __main__
import vizuniverse
import vizproximity
import viztracker2 as viztracker

import hand

#messing around w/ tracking

viztracker.go()


composite = viztracker.getManager().getCompositeList()[0]
headTracker = composite.getRawTracker(composite.HEAD)
handTracker = composite.getRawTracker(composite.RHAND)
stupidhand = viztracker.get('righthand') 

viewpoint = viztracker.get('viewpoint')
movable = viztracker.get("movable")
print('viewpoint')
def printData():
    print 'Tracker position',headTracker.getPosition()
    print 'Tracker euler',headTracker.getEuler()
    print 'Hand Tracker position',handTracker.getPosition() #just added this
    print 'Hand Tracker euler',handTracker.getEuler() #and this
    print 'Viewpoint position',viewpoint.getPosition()
    print 'Movable position',movable.getPosition(),'\n'
vizact.ontimer(1, printData)
# Setup tracking if this is the main script
if __name__ == "__main__":
	import viztracker
	viztracker.DEFAULT_HANDS = True
	viztracker.go()


info = vizinfo.add("""
1: Toggle Hat
2: Toggle Snare

Q: Hat
W: Snare
E: Tom
R: Cymbal
T: Kick drum
""",.8)
info.alignment (vizinfo.LOWER_RIGHT)
info.translate (0.95, 0.05)


#Create environment map from drum models
DrumShinyTex = viz.add(viz.ENVIRONMENT_MAP,'nvlobby.png')

#Add drum model
DrumTomModel = viz.add('drum.wrl')
DrumTomModel.translate(0,.1,0)
DrumTomModel.setEuler([20,-15,0])
DrumTomModel.scale(0.7,0.7,0.7)

#Change appearance of drum
DrumTomModel.texture(DrumShinyTex,'shiny')
DrumTomModel.appearance(viz.ENVIRONMENT_MAP|viz.MODULATE,'shiny')
DrumTomModel.texblend(0.6,'shiny')
DrumTomModel.color(0,0,0.5,'shiny')

#Make a clone of the drum model
DrumSnareModel = DrumTomModel.copy()
DrumSnareModel.translate(0,0.1,0)
DrumSnareModel.scale(0.7,0.4,0.7)
DrumSnareModel.setEuler([-20,-15,0])

#Add hihat model
HiHatModel = viz.add('hihat.wrl')
HiHatModel.translate(0,0.1,0)
HiHatModel.scale(0.7,0.7,0.7)

#Get hihat bottom and top part
HiHatTop = HiHatModel.getchild('top')
HiHatBottom = HiHatModel.getchild('bottom')

#Change appearance of cymbal
HiHatModel.texture(DrumShinyTex)
HiHatModel.appearance(viz.ENVIRONMENT_MAP|viz.MODULATE)
HiHatModel.texblend(0.05)

#Add cymbal model
CymbalModel = viz.add('cymbal.wrl')
CymbalModel.translate(0,0.1,0)
CymbalModel.scale(0.7,0.7,0.7)

#Change appearance of cymbal
CymbalModel.texture(DrumShinyTex)
CymbalModel.appearance(viz.ENVIRONMENT_MAP|viz.MODULATE)
CymbalModel.texblend(0.6)
CymbalModel.disable(viz.CULL_FACE)

#Add kick bass model
KickBassModel = viz.add('bass.wrl')

#Change appearance of kick bass
KickBassModel.texture(DrumShinyTex,'shiny')
KickBassModel.appearance(viz.ENVIRONMENT_MAP|viz.MODULATE,'shiny')
KickBassModel.texblend(0.6,'shiny')
KickBassModel.color(0,0,0.5,'shiny')

#Get the hammer of the kick bass
KickBassHammer = KickBassModel.getchild('hammer')
KickBassHammer.translate(-0.05,0.138,-0.172)
KickBassHammer.setAxisAngle([1,0,0,-45])
KickBassHammer.parent(viz.WORLD)

#Detach pedal from model so that size the base drum doesn't affect it
KickBassPedal = KickBassModel.getchild('kickBASE')
KickBassPedal.color(.35,.35,.35)
KickBassPedal.parent(viz.WORLD)
KickBassPedal.appearance(viz.ENVIRONMENT_MAP|viz.MODULATE)


#Apply worldviz logo to kick drum using projected textures
KickDrumFront = KickBassModel.getchild('front_drum')
KickDrumBack = KickBassModel.getchild('back_drum')

import projector

DrumLogo = viz.add('logo.jpg')

ProjFront = projector.add(DrumLogo)
ProjFront.affect(KickDrumFront,0)
ProjFront.ortho(0.2,0.03)
ProjFront.translate(0,0.25,-2)

ProjBack = projector.add(DrumLogo)
ProjBack.affect(KickDrumBack,0)
ProjBack.ortho(0.2,0.03)
ProjBack.translate(0,0.25,2)
ProjBack.setEuler([180,0,0])

KickDrumFront.texblend(0.4)
KickDrumBack.texblend(0.4)

############################################################
################# Initialize Drum Objects ##################
############################################################

DRUM_HIT_EVENT = viz.eventid('DrumHitEvent')

class CymbalHit(viz.EventClass):
	def __init__(self,model):
		viz.EventClass.__init__(self)
		self.model = model
		self.callback(viz.TIMER_EVENT,self.ontimer)
		self.yaw = 0
		self.pitch = 0
		
	def ontimer(self,num):
	
		self.yaw += self.yawspeed * viz.elapsed()
		self.yawspeed *= 0.99
		
		self.pitch += viz.elapsed() * 360
		
		if self.pitch > 360:
			self.magnitude *= 0.7
			self.pitch -= 360
		
		pitch = math.sin(viz.radians(self.pitch)) * self.magnitude
		
		self.model.setEuler([self.yaw,pitch,0])

	def hit(self,speed,magnitude):
		self.yawspeed = speed
		self.magnitude = magnitude
		self.killtimer(0)
		self.starttimer(0,0,viz.FOREVER)

class Drum:
	def __init__(self,sound,action=0):
		self.__pos = viz.Vector()
		self.__radius = 0.16
		self.__minSpeed = 1.0
		self.__inRegion = [False,False]
		
		self.model = viz.add(viz.GROUP)
		self.model.translate(self.__pos.get())
		
		self.sphere = self.model.add('white_ball.wrl')
		self.sphere.visible(0)
		
		scale = self.__radius * 10
		self.sphere.scale(scale,scale,scale)
		
		self.hitSound = sound
		self.hitAction = action
		self.hitSpeed = 0
		
		#Cache sound
		self.model.playsound(sound)
		
	def setPos(self,x,y=0,z=0):
		self.__pos.set(x,y,z)
		self.model.translate(x,y,z)
		
	def setRadius(self,radius):
		self.__radius = radius
		scale = radius * 10
		self.sphere.scale(scale,scale,scale)
		
	def hit(self):
		#Trigger Event
		viz.sendevent(DRUM_HIT_EVENT,self)
		#Play drum sound
		self.model.playsound(self.hitSound)
		#Play hit action
		if self.hitAction:
			self.model.clearActions()
			self.model.translate(self.__pos.get())
			self.model.add(self.hitAction)
				
	def checkHit(self,stick,pos,speed):
		#Check if drum is hit and playsound if it is
		if (self.__pos - pos).length() < self.__radius:
			#Make sure speed is enough for hit sound and that we just entered drum region
			if not self.__inRegion[stick] and speed > self.__minSpeed and pos[1] > self.__pos[1]:
				#Save hit speed
				self.hitSpeed = speed
				self.hit()
				
			self.__inRegion[stick] = True
		else:
			self.__inRegion[stick] = False

#Create action for drum hitting
DrumHitAction = vizact.sequence(vizact.move(0,-1,0,0.05),vizact.move(0,1,0,0.05))

#Create class for animation cymbal hit
CymbalHitAnimation = CymbalHit(CymbalModel)

#Create action to open hihat
OpenHiHat = vizact.goto(0,0,0,0.5)

#Create action to close hihat
CloseHiHat = vizact.goto(0,0.04,0,0.5)

#List of drums
DrumList = []

#Create tom drum
TomDrum = Drum('sounds/tom.wav',DrumHitAction)
TomDrum.setPos(0.18,0.82,0.24)
DrumTomModel.parent(TomDrum.model)
DrumList.append(TomDrum)

#Create snare drum
SnareDrum = Drum('sounds/snare2.wav',DrumHitAction)
SnareDrum.setPos(-0.18,0.82,0.24)
SnareDrum.sounds = ['sounds/snare.wav','sounds/snare2.wav']
SnareDrum.curSound = 1
DrumSnareModel.parent(SnareDrum.model)
DrumList.append(SnareDrum)

#Create cymbal drum
CymbalDrum = Drum('sounds/cymbal.wav',0)
CymbalDrum.setPos(0.47,0.87,0.15)
CymbalModel.parent(CymbalDrum.model)
DrumList.append(CymbalDrum)

#Create hat drum
HatDrum = Drum('sounds/hat_open.wav',DrumHitAction)
HatDrum.setPos(-0.47,0.87,0.15)
HiHatModel.parent(HatDrum.model)
DrumList.append(HatDrum)

#Initialize HiHatBottom drum settings
HiHatBottom.open = 0
HiHatBottom.sounds = ['sounds/hat_open.wav','sounds/hat_closed.wav']
HiHatBottom.action = [OpenHiHat,CloseHiHat]

def ondrum(drum):
	if drum == CymbalDrum:
		#Animate cymbal
		CymbalHitAnimation.hit(360,min(10*drum.hitSpeed,80))

vizact.onevent (DRUM_HIT_EVENT, lambda e: (True, e), ondrum) 

#Create action for when kick drum is hit
SizeUp = vizact.size(1.1,1.1,1.1,8)
SizeDown = vizact.size(1,1,1,8)
SizeUp.object = KickBassModel
SizeDown.object = KickBassModel
KickBassAction = vizact.sequence(vizact.method.rotate(1,0,0,-45),KickBassModel.scale(1,1,1),vizact.spinto(1,0,0,45,1000),vizact.parallel(vizact.spinto(1,0,0,-45,1400),vizact.sequence(SizeUp,SizeDown)))

def kickbass():
	KickBassModel.playsound('sounds/kick.wav')
	KickBassHammer.clear(viz.ALL)
	KickBassHammer.add(KickBassAction)
vizact.onkeydown('t',kickbass)

def ToggleHat():
	HiHatBottom.open = not HiHatBottom.open
	HiHatBottom.add(HiHatBottom.action[HiHatBottom.open])
	HatDrum.hitSound = HiHatBottom.sounds[HiHatBottom.open]
vizact.onkeydown('1',ToggleHat)	

def ToggleSnare():
	SnareDrum.curSound = not SnareDrum.curSound
	SnareDrum.hitSound = SnareDrum.sounds[SnareDrum.curSound]
vizact.onkeydown('2',ToggleSnare)

# Grab hands from viztracker, if we don't have enough then put the sticks below the floor to make things easy
numhands = len(vizuniverse.getManager().getHandList())
if numhands >= 1:
#	LeftSensor = handTracker.getPosition()
	LeftSensor = vizuniverse.getManager().getHandList()[0]
else:
	LeftSensor = handTracker.getPosition() # Create tracker that is below the room
	
if numhands >= 2:
	RightSensor = vizuniverse.getManager().getHandList()[1]
else:
	RightSensor = viz.addGroup(pos=[0,-10,0]) # Create tracker that is below the room


room = viz.add('room/w1523a.wrl')
room.appearance(viz.MODULATE)

############################################################
################# Initialize Drum Sticks ###################
############################################################

#Add stick models
RightStick = viz.add('stick.osg',viz.WORLD,1,0)
RightStickTip = RightStick.add(viz.GROUP)
RightStickTip.translate(0,0,0.3)
LeftStick = viz.add('stick.osg',viz.WORLD,1,0)
LeftStickTip = LeftStick.add(viz.GROUP)
LeftStickTip.translate(0,0,0.3)


# Light Stuff
key_spot = viz.add(viz.LIGHT)
key_spot.position(0,3,-1)
key_spot.direction(1,-10,0)
key_spot.spread(90)
key_spot.intensity(1)
key_spot.spotexponent(2)

LightTexture = viz.add('particle.rgb')
def AddLight(lightColor,glareColor,speed,radius,height):
	LightRoot = viz.add(viz.GROUP)
	LightRoot.translate(radius,height,0)
	LightRoot.center(-radius,0,0)
	LightRoot.add(vizact.spin(0,1,0,speed))
	GlareQuad = LightRoot.add(viz.TEXQUAD)
	GlareQuad.texture(LightTexture)
	GlareQuad.billboard()
	GlareQuad.color(glareColor)
	GlareQuad.disable(viz.LIGHTING)
	GlareQuad.scale(0.2,0.2,0.2)
	GlareQuad.blendFunc(viz.GL_SRC_ALPHA,viz.GL_ONE)
	Light = LightRoot.add(viz.LIGHT)
	Light.position(0,0,0)
	Light.color(lightColor[0],lightColor[1],lightColor[2])
	Light.linearattenuation(0.2)
AddLight([0.4,0,0],viz.RED,180,-2,1.5)
AddLight([0,0,0.4],viz.BLUE,-90,1,1.0)
AddLight([1,1,1],viz.WHITE,30,1.5,0.5)

# Keyboard bypass
vizact.onkeydown('q',HatDrum.hit)
vizact.onkeydown('w',SnareDrum.hit)
vizact.onkeydown('e',TomDrum.hit)
vizact.onkeydown('r',CymbalDrum.hit)

def ontimer():
	#Get data from sensors
	rightData = RightSensor.getPosition()+RightSensor.getEuler()
	leftData = LeftSensor.getPosition()+LeftSensor.getEuler()
	
	#Save current drumstick position for calculating speed
	PrevRightTipPos = RightStickTip.get(viz.POSITION,viz.ABSOLUTE_WORLD)
	PrevLeftTipPos = LeftStickTip.get(viz.POSITION,viz.ABSOLUTE_WORLD)
	
	#Apply sensor data to drum sticks
	RightStick.translate(rightData[0],rightData[1],rightData[2])
	RightStick.setEuler([rightData[3],rightData[4],rightData[5]])
	LeftStick.translate(leftData[0],leftData[1],leftData[2])
	LeftStick.setEuler([leftData[3],leftData[4],leftData[5]])
	
	#Get position of drumstick tips
	RightTipPos = RightStickTip.get(viz.POSITION,viz.ABSOLUTE_WORLD)
	LeftTipPos = LeftStickTip .get(viz.POSITION,viz.ABSOLUTE_WORLD)
	
	#Calculate speed of drumsticks
	RightTipSpeed = (viz.Vector(RightTipPos) - PrevRightTipPos).length() / viz.elapsed()
	LeftTipSpeed = (viz.Vector(LeftTipPos) - PrevLeftTipPos).length() / viz.elapsed()

	#Update each drum
	for drum in DrumList:
		drum.checkHit(0,RightTipPos,RightTipSpeed)
		drum.checkHit(1,LeftTipPos,LeftTipSpeed)



# Return back a list of camera offsets that we can attach to
def GetViewList():
	list = []
	list.append (vizuniverse.VUOrigin(pos=[  0,  0, -0.5], viewtype=vizuniverse.VT_DEFAULT)) # Main viewpoint slightly offset
	list.append (vizuniverse.VUOrigin(pos=[  1,  0,    3], viewtype=vizuniverse.VT_VIEWER)) # Static view
	list.append (vizuniverse.VUOrigin(pos=[ -3,  0,    3], viewtype=vizuniverse.VT_VIEWER)) # Viewer avatar
	list.append (vizuniverse.VUOrigin(pos=[  3,  0,    3], viewtype=vizuniverse.VT_VIEWER)) # Viewer avatar
	list.append (vizuniverse.VUOrigin(pos=[  0,-0.1, -2.2], posScale=[3.5, 1, 3.5], euler=[0,15,0], fov=55, viewtype=vizuniverse.VT_DESKTRACK, name="DeskTrack", description="Monitor display with tracked hands"))
	list.append (vizuniverse.VUOrigin(pos=[  0,  0, -1.5], euler=[0,35,0], fov=75, viewtype=vizuniverse.VT_DESKTOP, name="Desktop", description="Desktop with keyboard and mouse"))
	return list

def Init():
	# Configure viewpoints for all composites
	vizuniverse.getManager().assignViewpointsComposites(GetViewList())
	return 'Drum Kit'

def Show():
	vizact.ontimer (0, ontimer)
	viz.get(viz.HEAD_LIGHT).disable()
	key_spot.enable()

def Hide():
	viz.get(viz.HEAD_LIGHT).enable()
	key_spot.disable()

def Info(visible):
	info.visible (visible)
#Messing around w/ the collision/sensor stuff

#Create proximity manager
manager = vizproximity.Manager()
manager.setDebug(viz.ON)

#Create sensor using drum model
kick_bass_sensor= vizproximity.Sensor(vizproximity.Box([.5,.5,.5],center=[0,.5,0]),source= KickBassModel)
manager.addSensor(kick_bass_sensor)
drum_tom_sensor = vizproximity.Sensor(vizproximity.Box([.3,.3,.3],center=[0,0,0]),source= DrumTomModel)
manager.addSensor(drum_tom_sensor)
drum_snare_sensor = vizproximity.Sensor(vizproximity.Box([.4,.4,.4],center=[0,0,0]),source= DrumSnareModel)
manager.addSensor(drum_snare_sensor)
hi_hat_sensor = vizproximity.Sensor(vizproximity.Box([.3,.2,.4],center=[0,0,0]),source= HiHatModel)
manager.addSensor(hi_hat_sensor)
cymbal_sensor = vizproximity.Sensor(vizproximity.Box([.3,.2,.4],center=[0,0,0]),source= CymbalModel)
manager.addSensor(cymbal_sensor)



def proximityTask1():
    #Play beautiful music
    yield vizproximity.waitEnter(drum_tom_sensor)

viztask.schedule(proximityTask1())




def EnterProximity_TomDrum(drum_tom_sensor):
    """@args vizproximity.ProximityEvent()"""
    TomDrum.hit()


def ExitProximity_Tom_Drum(drum_tom_sensor):
	"""@args vizproximity.ProximityEvent()"""
	print'Hit Tom!'

manager.onEnter(drum_tom_sensor,EnterProximity_TomDrum)
manager.onExit(drum_tom_sensor,ExitProximity_Tom_Drum)

def EnterProximity_Snare_Drum(drum_snare_sensor):
    """@args vizproximity.ProximityEvent()"""
    SnareDrum.hit()


def ExitProximity_Snare_Drum(drum_tom_sensor):
	"""@args vizproximity.ProximityEvent()"""
	print'Hit Snare!'

manager.onEnter(drum_snare_sensor,EnterProximity_Snare_Drum)
manager.onExit(drum_snare_sensor,ExitProximity_Snare_Drum)

def EnterProximity_Cymbal(drum_snare_sensor):
    """@args vizproximity.ProximityEvent()"""
    CymbalDrum.hit()


def ExitProximity_Cymbal(cymbal_sensor):
	"""@args vizproximity.ProximityEvent()"""
	print'Hit Cymbal!'

manager.onEnter(cymbal_sensor,EnterProximity_Cymbal)
manager.onExit(cymbal_sensor,ExitProximity_Cymbal)

def EnterProximity_Cymbal(drum_snare_sensor):
    """@args vizproximity.ProximityEvent()"""
    CymbalDrum.hit()
def EnterProximity_Cymbal(drum_snare_sensor):
    """@args vizproximity.ProximityEvent()"""
    CymbalDrum.hit()


def ExitProximity_Cymbal(cymbal_sensor):
	"""@args vizproximity.ProximityEvent()"""
	print'Hit Cymbal!'

manager.onEnter(cymbal_sensor,EnterProximity_Cymbal)
manager.onExit(cymbal_sensor,ExitProximity_Cymbal)

def EnterProximity_Hi_Hat(hi_hat_sensor):
    """@args vizproximity.ProximityEvent()"""
    HatDrum.hit()


def ExitProximity_Hi_Hat(hi_hat_sensor):
	"""@args vizproximity.ProximityEvent()"""
	print'Hit Hat!'

manager.onEnter(hi_hat_sensor,EnterProximity_Hi_Hat)
manager.onExit(hi_hat_sensor,ExitProximity_Hi_Hat)

def EnterProximity_Kick_Bass(kick_bass_sensor):
    """@args vizproximity.ProximityEvent()"""
    kickbass()


def ExitProximity_Kick_Bass(kick_bass_sensor):
	"""@args vizproximity.ProximityEvent()"""
	print'Kicked Bass!'

manager.onEnter(kick_bass_sensor,EnterProximity_Kick_Bass)
manager.onExit(kick_bass_sensor,ExitProximity_Kick_Bass)



#Add drumstick as proximity target 

#things to try
"""composite.RHAND
RHAND
hand"""
target = vizproximity.Target((stupidhand))
manager.addTarget(target)
print(composite.RHAND)    
#vizact.onkeydown('d',manager.setDebug,viz.TOGGLE) 

# If this is a standalone script, start up and load things
if __name__ == "__main__":
	Init()
	Show()
	vizact.onkeydown(' ', Info, viz.TOGGLE)
