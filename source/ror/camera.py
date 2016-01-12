#Chris Ritchey 29/06/2007, rethnor@gmail.com
import ogre.renderer.OGRE as ogre 
import math
from random import random

class Camera:
    "Stores information about the camera position"
    def __init__(self, rootNode, camera):
        self.cameraRadius = 1
        self.camera = camera
        self.rand = str(random())
        
        self.targetNode = rootNode.createChildSceneNode("cameraTargetNode" + self.rand, ogre.Vector3(0,0,0))
        self.cameraNode = self.targetNode.createChildSceneNode("cameraNode" + self.rand, \
            self.targetNode.getPosition() + ogre.Vector3(0,0, self.cameraRadius))\

        self.cameraNode.attachObject(self.camera)
        self.targetNode.flipVisibility()
        
        #self.camera.setPosition(self.cameraNode.getPosition())
        #self.camera.lookAt(self.targetNode.getPosition())
        
        self.camera.nearClipDistance = 0.1
        self.camera.setAutoAspectRatio(True)
        
        self.cameraMotion = ogre.Vector3(0,0,0)
        
        #self.curCoordinate = Cartesian()
        #self.curPosition = ogre.Vector3(0,0,0)
        #self.newPosition = ogre.Vector3(0,0,0)
        #self.origin = ogre.Vector3(0,0,0)
    
    def move(self, movement, modifier):
        #print "I'm here!!: %.3f, %.3f, %.3f" % (movement.x, movement.y, movement.z)
        movement *= ogre.Vector3(-1,1,1)
        movement /= 5
        
        if modifier:
            self.cameraNode.translate(self.cameraNode.getOrientation() * movement)
        else:
            self.targetNode.pitch(ogre.Degree(-movement.y))
            self.targetNode.yaw(ogre.Degree(movement.x))
            self.cameraNode.translate(ogre.Vector3(0,0, movement.z))
        
"""
class Spherical:
    "Spherical coordinates class"
    def __init__(self):
        #  coordinates stored as <rho, phi, theta> in radians
        self.rho = 0
        self.phi = 0
        self.theta = 0

    def setCartesian(self, other):
        rho = sqrt(other.x**2 + other.y**2 + other.z**2)
        phi = atan2(sqrt(other.x**2 + other.z**2), other.y)
        theta = atan2(other.x, other.z)

    def cartesian(self):
        return ogre.Vector3(
            rho * sin(phi) * cos(theta), \
            rho * cos(phi),\
            rho * sin(phi) * sin(theta))

    def vertical(self, amount):
        phi += amount
        phi = fabs(fmod(phi, math.pi))

    def horizontal(self, amount):
        #will need adjust the amount by some factor so the same value can be 
        #used for all three coordinate classes
        theta += amount
        theta = fabs(fmod(phi, 2*math.pi))

    def zoom(self, amount):
        #will need adjust the amount by some factor so the same value can be 
        #used for all three coordinate classes
        rho += amount
        if rho < 0:
            rho = 0
            
    def moveto(self, amount):
        horizontal(self, amount.x)
        vertical(self, amount.y)
        zoom(self, amount.z)

class Cartesian:
    "cartesian coordinates class"
    def __init__(self):
        self.position = ogre.Vector3(0,0,0)
    def setCartesian(self, other):
        self.position = other
        
    def cartesian(self):
        return self.position

    def vertical(self, amount):
        self.position.y += amount

    def horizontal(self, amount):
        self.position.z += amount

    def zoom(self, amount):
        self.position.x += amount

    def moveto(self, amount):
        self.position += amount
        
class Cylindrical:
    "cartesian coordinates class"
    def __init__(self):
        self.r = 0
        self.theta = 0
        self.z = 0

    def cartesian(self):
        return ogre.Vector3(r*sin(theta), y, r*cos(theta))

    def vertical(self, amount):
        y += amount

    def horizontal(self, amount):
        theta += amount
        theta = fabs(fmod(phi, 2*math.pi))

    def zoom(self, amount):
        #will need adjust the amount by some factor so the same value can be 
        #used for all three coordinate classes
        r += amount
        if r < 0:
            r = 0

    def moveto(self, amount):
        horizontal(self, amount.x)
        vertical(self, amount.y)
        zoom(self, amount.z)
"""