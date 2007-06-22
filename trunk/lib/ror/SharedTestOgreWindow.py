#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import sys
import wx 
import ogre.renderer.OGRE as ogre 
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from random import random

class SharedTestOgreWindow(wxOgreWindow): 
    def __init__(self, parent, ID, sceneManager, size = wx.Size(200,200), renderSystem = "OpenGL", **kwargs):
        self.sceneManager = sceneManager
        self.rand = str(random())
        wxOgreWindow.__init__(self, parent, ID, size = size, renderSystem = renderSystem, **kwargs) 
        self.parent = parent

    def SceneInitialisation(self):
        # create a camera
        self.camera = self.sceneManager.createCamera('SharedCamera' + self.rand) 
        self.camera.lookAt(ogre.Vector3(0, 0, 0)) 
        self.camera.setPosition(ogre.Vector3(0, 0, 100))
        self.camera.nearClipDistance = 1
        self.camera.setAutoAspectRatio(True) 

        # create the Viewport"
        self.viewport = self.renderWindow.addViewport(self.camera, 0, 0.0, 0.0, 1.0, 1.0) 
        self.viewport.backgroundColour = ogre.ColourValue(0, 0, 0) 

        # bind mouse and keyboard
        d=10.0 #displacement for key strokes 
        self.ControlKeyDict={wx.WXK_LEFT:ogre.Vector3(-d,0.0,0.0), 
                             wx.WXK_RIGHT:ogre.Vector3(d,0.0,0.0), 
                             wx.WXK_UP:ogre.Vector3(0.0,0.0,-d), 
                             wx.WXK_DOWN:ogre.Vector3(0.0,0.0,d), 
                             wx.WXK_PAGEUP:ogre.Vector3(0.0,d,0.0), 
                             wx.WXK_PAGEDOWN:ogre.Vector3(0.0,-d,0.0)} 
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown) 
        self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)        
    
    def onKeyDown(self,event):
        validMove = self.ControlKeyDict.get(event.m_keyCode, False) 
        if validMove:
            pos = self.camera.getPosition()
            pos += validMove
            self.camera.setPosition(pos) 
        event.Skip()  
    
    def onMouseEvent(self, event):
        self.SetFocus() #Gives Keyboard focus to the window 
        
        if event.RightDown(): #Precedes dragging 
            self.StartDragX, self.StartDragY = event.GetPosition() #saves position of initial click 
        
        if event.Dragging() and event.RightIsDown(): #Dragging with RMB 
            x,y = event.GetPosition() 
            dx = self.StartDragX - x
            dy = self.StartDragY - y
            self.StartDragX, self.StartDragY = x, y 
        
            self.camera.yaw(ogre.Degree(dx/3.0)) 
            self.camera.pitch(ogre.Degree(dy/3.0)) 
        event.Skip()
            