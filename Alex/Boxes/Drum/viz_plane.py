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
import vizshape
import viz
import vizshape


import viz
import vizshape
viz.go()

#Create box with each face split into separate sub-node
box = vizshape.addBox([1,1,1],splitFaces=True,pos=(0,1.8,4))
box.addAction(vizact.spin(0,1,0,45))

#Create textures
t1 = viz.add('image1.jpg')
t2 = viz.add('image2.jpg')

#Apply first texture to front/back face
box.texture(t1,node='front')
box.texture(t1,node='back')

#Apply second texture to left/right face
box.texture(t2,node='left')
box.texture(t2,node='right')
