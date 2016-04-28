#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx 
import ogre.renderer.OGRE as ogre 
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from random import random

class RoROgreWindow(wxOgreWindow): 
    def __init__(self, parent, ID, size = wx.Size(200,200), renderSystem = "OpenGL", **kwargs): 
        self.rand = str(random())
        wxOgreWindow.__init__(self, parent, ID, size = size, renderSystem = renderSystem, **kwargs) 
        self.parent = parent

    def initialize_scene(self):
        # only init things in the main window, not in shared ones!
        # setup resources 
        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/packs/OgreCore.zip", "Zip", "Bootstrap", False)
        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media", "FileSystem", "General", False)
        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/fonts", "FileSystem", "General", False)
        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/materials/programs", "FileSystem", "General", False)
        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/materials/scripts", "FileSystem", "General", False)
        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/materials/textures", "FileSystem", "General", False)
        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/models", "FileSystem", "General", False)
        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/overlays", "FileSystem", "General", False)
        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/particle", "FileSystem", "General", False)
        ogre.ResourceGroupManager.getSingleton().initialiseAllResourceGroups() 

        #get the scenemanager
        self.sceneManager = getOgreManager().createSceneManager(ogre.ST_GENERIC)

        # create a camera
        self.camera = self.sceneManager.createCamera('Camera' + self.rand) 
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
        
        #create objects
        self._prepare_scene()
    
    def _prepare_scene(self):
        self.sceneManager.AmbientLight = ogre.ColourValue(0.7, 0.7, 0.7 )
        self.sceneManager.setShadowTechnique(ogre.ShadowTechnique.SHADOWTYPE_STENCIL_ADDITIVE);
        self.sceneManager.setSkyDome(True, 'Examples/CloudySky', 4.0, 8.0) 

        self.MainLight = self.sceneManager.createLight('MainLight') 
        self.MainLight.setPosition (ogre.Vector3(20, 80, 130))

        # add some fog 
#        self.sceneManager.setFog(ogre.FOG_EXP, ogre.ColourValue.White, 0.0002) 

        # create a floor Mesh
        plane = ogre.Plane() 
        plane.normal = ogre.Vector3(0, 1, 0) 
        plane.d = 200 
        
        ogre.MeshManager.getSingleton().createPlane('FloorPlane' + self.rand, "General", plane, 200000.0, 200000.0, 
                                                    20, 20, True, 1, 50.0, 50.0,ogre.Vector3(0, 0, 1),
                                                    ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY, 
                                                    ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY, 
                                                    True, True)

        # create floor entity 
        entity = self.sceneManager.createEntity('floor', 'FloorPlane' + self.rand) 
        entity.setMaterialName('Examples/RustySteel') 
        self.sceneManager.getRootSceneNode().createChildSceneNode().attachObject(entity) 
        
        # create a mesh
        fishNode = self.sceneManager.getRootSceneNode().createChildSceneNode("fishNode" + self.rand) 
        entity = self.sceneManager.createEntity('fishEnt' + self.rand, 'fish.mesh') 
        fishNode.attachObject(entity) 
        fishNode.setScale(10.0,10.0,10.0) 
        entity.setCastShadows(True)
        
    
    
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

