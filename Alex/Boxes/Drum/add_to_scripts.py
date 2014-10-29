############################################
# This vizconnect code will be used to 
# replace all viztracker code in your script
############################################

import vizconnect

import vizproximity #you already have this

viz.go() #you already have this, but wondering why it's at bottom of script?

piazza = viz.addChild('piazza.osgb') #don't need, just for reference to test tracking

#######################################
#Vizconnect Init code
#######################################
CONFIGURATION = 'vizconnect_config.py'
vizconnect.go(CONFIGURATION)


handTracker = vizconnect.getTracker('ppt_hand')
#handTracker = vizconnect.getRawTracker('ppt_hand')
target = vizproximity.Target(handTracker)
print handTracker
handTrackerpos = handTracker.getPosition()
print handTrackerpos

#or 
#handTracker = vizconnect.getTracker('ppt_hand')
##target = vizproximity.Target(vizproximity.Sphere(0.1,center=[0,0,0]),handTracker) #this only works for sensors, not targets
#sensor = vizproximity.Sensor(vizproximity.Sphere(0.1,center=[0,0,0]),handTracker)



#Create proximity manager  #you already have this
manager = vizproximity.Manager()
manager.setDebug(viz.ON)

manager.addTarget(target)
#manager.addSensor(sensor)

