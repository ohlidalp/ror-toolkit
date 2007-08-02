#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx, math
import ogre.renderer.OGRE as ogre 
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from ror.SimpleTruckRepresentation import *
from ror.odefparser import *
from ror.rorcommon import *


class TreeDropTarget(wx.PyDropTarget):
    def __init__(self, window):
        wx.PyDropTarget.__init__(self)
        self.do = wx.FileDataObject()
        self.SetDataObject(self.do)

    def OnEnter(self, x, y, d):
        print "OnEnter: %d, %d, %d\n" % (x, y, d)
        return wx.DragCopy

    def OnDragOver(self, x, y, d):
        print "OnDragOver: %d, %d, %d\n" % (x, y, d)
        return wx.DragCopy

    def OnLeave(self):
        print "OnLeave\n"

    def OnDrop(self, x, y):
        print "OnDrop: %d %d\n" % (x, y)
        return True

    def OnData(self, x, y, d):
        print "OnData: %d, %d, %d\n" % (x, y, d)
        self.GetData()
        print "%s\n" % self.do.GetFilenames()
        return d
    
class ObjectPreviewOgreWindow(wxOgreWindow): 
    def __init__(self, parent, ID, size = wx.Size(200,200), rordir = "", **kwargs):
        self.rordir = rordir
        self.parent = parent
        self.objnode = None
        self.objentity = None
        self.camalpha = 0
        self.radius = 40
        self.dragging = False
        wxOgreWindow.__init__(self, parent, ID, size = size, **kwargs)
        droptarget = TreeDropTarget(self)
        self.SetDropTarget(droptarget)
        

    def SceneInitialisation(self):
        addresources = [self.rordir+"\\data\\terrains",self.rordir+"\\data\\trucks",self.rordir+"\\data\\objects"]
        # only init things in the main window, not in shared ones!
        # setup resources 
        for r in addresources:
            ogre.ResourceGroupManager.getSingleton().addResourceLocation(r, "FileSystem", "General", False)

        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/packs/OgreCore.zip", "Zip", "Bootstrap", False)
        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media", "FileSystem", "General", False)
        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/materials", "FileSystem", "General", False)
        ogre.ResourceGroupManager.getSingleton().addResourceLocation("media/models", "FileSystem", "General", False)
        ogre.ResourceGroupManager.getSingleton().initialiseAllResourceGroups() 

        #get the scenemanager
        self.sceneManager = getOgreManager().createSceneManager(ogre.ST_GENERIC)

        # create a camera
        self.camera = self.sceneManager.createCamera(str(randomID())+'Camera') 
        self.camera.lookAt(ogre.Vector3(0, 0, 0)) 
        self.camera.setPosition(ogre.Vector3(0, 0, 100))
        self.camera.nearClipDistance = 0.1
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
        self.populateScene()
    
    def loadFile(self, filename):
        self.filename = filename
        filenameonly, extension = os.path.splitext(filename)
        if extension.lower() in [".truck", ".load"]:
            self.free()
            uuid = randomID()
            self.objnode, self.objentity, manualobject = createTruckMesh(self.sceneManager, filename, uuid)
        elif extension.lower() in [".odef"]:
            self.free()
            uuid = randomID()
            self.loadodef(filename, uuid)
        
    def loadodef(self, filename, uuid):
        try:
            (meshname, sx, sy, sz) = loadOdef(filename)
        except Exception, err:
            log().error("error while processing odef file %s" % odefFilename)
            log().error(str(err))
            return
        # create mesh
        print meshname, sx, sy, sz
        self.objnode = self.sceneManager.getRootSceneNode().createChildSceneNode(uuid+"objnode")
        self.objentity = self.sceneManager.createEntity(uuid+'objentity', meshname) 
        self.objnode.attachObject(self.objentity)
        self.objnode.rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        #self.objnode.setPosition(0,0,0) 
        if not sx is None:
            self.objnode.setScale(sx, sy, sz)
    
    def free(self):
        try:
            self.sceneManager.destroyAllManualObjects()
        except:
            pass
        try:
            self.objnode.detachAllObjects()
            self.sceneManager.destroySceneNode(self.objnode.getName())
        except:
            pass
        try:
            self.sceneManager.destroyEntity(self.objentity)    
        except:
            pass
    
    def populateScene(self):
        self.sceneManager.AmbientLight = ogre.ColourValue(0.7, 0.7, 0.7 )
        self.sceneManager.setShadowTechnique(ogre.ShadowTechnique.SHADOWTYPE_STENCIL_ADDITIVE);
        self.sceneManager.setSkyDome(True, 'mysimple/terraineditor/previewwindowsky', 4.0, 8.0) 

        self.MainLight = self.sceneManager.createLight('MainLight') 
        self.MainLight.setPosition (ogre.Vector3(20, 80, 130))

        # add some fog 
        self.sceneManager.setFog(ogre.FOG_EXP, ogre.ColourValue.White, 0.0002) 

        # create a floor Mesh
        plane = ogre.Plane() 
        plane.normal = ogre.Vector3(0, 1, 0) 
        plane.d = 200 
        uuid = str(randomID())
        ogre.MeshManager.getSingleton().createPlane(uuid + 'FloorPlane', "General", plane, 200000.0, 200000.0, 
                                                    20, 20, True, 1, 50.0, 50.0,ogre.Vector3(0, 0, 1),
                                                    ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY, 
                                                    ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY, 
                                                    True, True)

        # create floor entity 
        entity = self.sceneManager.createEntity(uuid+'floor', uuid + 'FloorPlane') 
        entity.setMaterialName('mysimple/terraineditor/previewwindowfloor') 
        self.sceneManager.getRootSceneNode().createChildSceneNode().attachObject(entity) 

    def updateCamera(self):
        if not self.objnode is None:
            if self.objentity is None:
                self.radius = 15
                height = 2
            else:
                self.radius = self.objentity.getBoundingRadius() * 2
                height = self.objentity.getBoundingBox().getMaximum().z
            pos = self.objnode.getPosition() + ogre.Vector3(0, height*0.4, 0)
            dx = math.cos(self.camalpha) * self.radius
            dy = math.sin(self.camalpha) * self.radius
            self.camera.setPosition(pos - ogre.Vector3(dx, -5, dy))
            self.camera.lookAt(pos + ogre.Vector3(0, height / 2, 0))
            if self.dragging == False:
                self.camalpha += math.pi / 720
            if self.camalpha >= 360:
                self.camalpha -= 360


    def OnFrameStarted(self):
        self.updateCamera()
        wxOgreWindow.OnFrameStarted(self)
    
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
        elif event.Dragging() and event.RightIsDown(): #Dragging with RMB 
            x,y = event.GetPosition() 
            dx = self.StartDragX - x
            dy = self.StartDragY - y
            self.StartDragX, self.StartDragY = x, y
            self.camalpha -= float(dx) * (math.pi / 720) * 2
            self.updateCamera()
            self.dragging = True
        else:
            self.dragging = False
        event.Skip()
            