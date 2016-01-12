#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys
import wx
import math
import ogre.renderer.OGRE as ogre 
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from random import random

class RoRTerrainSelectedObjectTopOgreWindow(wxOgreWindow): 
    def __init__(self, parent, ID, RoRTerrainOgreWindow, size = wx.Size(200,200), **kwargs):
        self.sceneManager = RoRTerrainOgreWindow.sceneManager
        self.mainWindow = RoRTerrainOgreWindow
        self.rand = str(random())
        wxOgreWindow.__init__(self, parent, ID,"terrainSelectedObjectTop", size = size, **kwargs) 
        self.parent = parent
        self.distance = 50

    def getTerrainHeight(self, pos):
        try:
            ray = ogre.Ray(ogre.Vector3(pos.x, 5000, pos.z), ogre.Vector3.NEGATIVE_UNIT_Y)
            self.terrainRaySceneQuery.setRay(ray)
            #self.terrainRaySceneQuery.setSortByDistance(True)
            #Perform the scene query
            result = self.terrainRaySceneQuery.execute()
            if len(result) > 0 and not result[0] is None and not result[0].worldFragment is None:
                return result[0].worldFragment.singleIntersection.y
        except:
            pass
                    
    def cameraCollision(self):
        camPos = self.camera.getPosition()
        terrainHeight = self.getTerrainHeight(camPos)
        if terrainHeight + 1 > camPos.y:
            self.camera.setPosition(camPos.x, terrainHeight + 1, camPos.z)
        
    def OnFrameStarted(self):
        # sync with main
        if not self.mainWindow.mSelected is None:
            n = self.mainWindow.mSelected.getParentNode()
            pos = n.getPosition()
            terrainHeight = self.getTerrainHeight(pos)
            camHeight = self.distance
            self.camera.setNearClipDistance(camHeight)
            self.camera.setFarClipDistance(camHeight * 10)
            self.camera.setPosition(pos - ogre.Vector3(0, 0.1, camHeight))
            self.camera.lookAt(pos)
        wxOgreWindow.OnFrameStarted(self)

    def SceneInitialisation(self):
        # create a camera
        self.camera = self.sceneManager.createCamera('SharedCamera' + self.rand) 
        
        self.camera.setProjectionType(ogre.ProjectionType.PT_ORTHOGRAPHIC)
        self.camera.setNearClipDistance(5)
        self.camera.setPosition(ogre.Vector3(0.1,-100,0))
        self.camera.lookAt(ogre.Vector3(0,0,0))
        #self.camera.setAutoAspectRatio(True) 

        # create the Viewport"
        self.viewport = self.renderWindow.addViewport(self.camera, 0, 0.0, 0.0, 1.0, 1.0) 
        self.viewport.backgroundColour = ogre.ColourValue(0, 0, 0) 
        self.terrainRaySceneQuery = self.sceneManager.createRayQuery(ogre.Ray());

        #activate mouse events
        self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)

    def onMouseEvent(self,event):
        if event.GetWheelRotation() != 0:
            zfactor = 0.1
            if event.ShiftDown():
                zfactor = 5
            self.distance += zfactor * -event.GetWheelRotation()
            if self.distance < 0.2:
                self.distance = 0.2
        event.Skip()
        
            