import viz
import vizact
import vizinput

viz.setMultiSample(4)
viz.fov(60)

# Start Vizard with a prompt dialog box
viz.go(viz.PROMPT)

import vizinfo
vizinfo.add('This script demonstrates how to gather input from the user at startup.')

#Retrieve text from the prompt
speed = viz.get(viz.INITMESG)

#Ask user for name
name = vizinput.input('What is your name?')

choices = ['Blue','Green','Orange']
colors = [[0,0,1],[0,1,0],[1,0.5,0]]
#Ask user for favorite color
favColor = vizinput.choose('Which of the following colors is your most favorite?',choices)

#Create text object of user name
text = viz.addText(name)
text.setPosition([0,3,7])
text.color(colors[favColor])

# Try to convert the text into a number.
# If the text is invalid, then set the rotation speed to 90.
try:
    rotateSpeed = float(speed)
except:
    rotateSpeed = 90

# Add the ball and move it in front of the viewer
ball = viz.addChild('beachball.osgb')
ball.setPosition([0,1.5,3])
ball.addAction(vizact.spin(0,1,0,rotateSpeed))

# Initialize the second ball to 0
ball2 = 0

# If Option 1 is checked then add the
# second ball and space both balls apart
if viz.get(viz.OPTION1):
    ball2 = ball.clone()
    ball.setPosition([-1,1.5,3])
    ball2.setPosition([1,1.5,3])
    ball2.addAction(vizact.spin(0,1,0,-rotateSpeed))

# If Option 2 is checked then set the
# background color to blue
if viz.get(viz.OPTION2):
    viz.clearcolor(viz.SKYBLUE)