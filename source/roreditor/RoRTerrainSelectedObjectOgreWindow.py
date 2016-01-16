#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys
import wx
import math
import ogre.renderer.OGRE as ogre
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from random import random

class RoRTerrainSelectedObjectOgreWindow(wxOgreWindow):
    def __init__(self, parent, ID, RoRTerrainOgreWindow, size = wx.Size(200,200), **kwargs):
        self.sceneManager = RoRTerrainOgreWindow.sceneManager
        self.mainWindow = RoRTerrainOgreWindow
        self.rand = str(random())
        wxOgreWindow.__init__(self, parent, ID, "terrainSelectedObject", size = size, **kwargs)
        self.parent = parent
        self.camalpha = 0
        self.radius = 40

    def cameraCollision(self):
        try:
            camPos = self.camera.getPosition()
            cameraRay = ogre.Ray(ogre.Vector3(camPos.x, 5000, camPos.z), ogre.Vector3.NEGATIVE_UNIT_Y)
            self.terrainRaySceneQuery.setRay(cameraRay)
            #self.terrainRaySceneQuery.setSortByDistance(True)
            #Perform the scene query
            result = self.terrainRaySceneQuery.execute()
            if len(result) > 0 and not result[0] is None and not result[0].worldFragment is None:
                terrainHeight = result[0].worldFragment.singleIntersection.y
                if ((terrainHeight + 1) > camPos.y):
                    self.camera.setPosition(camPos.x, terrainHeight + 1, camPos.z)
        except:
            pass

    def OnFrameStarted(self):
        # sync with main
        if not self.mainWindow.mSelected is None:
            self.radius = self.mainWindow.mSelected.getBoundingRadius() * 2
            height = self.mainWindow.mSelected.getBoundingBox().getMaximum().y
            n = self.mainWindow.mSelected.getParentNode()
            pos = n.getPosition() + ogre.Vector3(0, height*0.4, 0)
            self.camera.lookAt(pos + ogre.Vector3(0, height/2, 0))
            dx = math.cos(self.camalpha) * self.radius
            dy = math.sin(self.camalpha) * self.radius
            self.camera.setPosition(pos - ogre.Vector3(dx, -5, dy))
            self.camalpha += math.pi / 720
            if self.camalpha >= 360:
                self.camalpha = 0
        self.cameraCollision()
        wxOgreWindow.OnFrameStarted(self)

    def SceneInitialisation(self):
        # create a camera
        self.camera = self.sceneManager.createCamera('SharedCamera' + self.rand)
        self.camera.lookAt(ogre.Vector3(0, 0, 0))
        self.camera.setPosition(ogre.Vector3(0, 0, 100))
        self.camera.nearClipDistance = 0.1
        self.camera.setAutoAspectRatio(True)

        # create the Viewport"
        self.viewport = self.renderWindow.addViewport(self.camera, 0, 0.0, 0.0, 1.0, 1.0)
        self.viewport.backgroundColour = ogre.ColourValue(0, 0, 0)
        self.terrainRaySceneQuery = self.sceneManager.createRayQuery(ogre.Ray());
