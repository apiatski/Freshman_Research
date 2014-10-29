import viz
import viztracker_HMDVideoVision as viztracker

viztracker.go()


dojo = viz.add('dojo.osgb')

avatar = viz.add('vcc_male2.cfg', pos=(0,0,3), euler=(180,0,0) )
avatar.state(1)
