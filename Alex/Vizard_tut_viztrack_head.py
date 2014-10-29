import viz

viz.setMultiSample(4)
viz.fov(60)
viz.go()

lab = viz.addChild('lab.osgb')

import viztracker
tracker = viztracker.KeyboardOri()

link = viz.link(tracker,viz.MainView, mask = viz.LINK_ORI)