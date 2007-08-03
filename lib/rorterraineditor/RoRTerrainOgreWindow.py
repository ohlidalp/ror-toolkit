#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx, os, os.path, copy
import ogre.renderer.OGRE as ogre 
from ror.truckparser import *
from ror.terrainparser import *
from ror.odefparser import *
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from ror.rorcommon import *
from ror.SimpleTruckRepresentation import *

ADDEDBY = "//added by the terrrain editor:\n"
SHIFT_SPEED_FACTOR = 20
SLOW_DOWN_FACTOR = 0.75
LOW_SPEED_THRESHOLD = 1

# this class holds all the needed 3d data and also the underlying object data
class Entry:
    uuid = None
    node = None
    entity = None
    data = None
    manual = None
    
class HistoryEntry:
    uuid = None
    Position = None
    Rotation = None

class MyDropTarget(wx.PyDropTarget):
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
    
class RoRTerrainOgreWindow(wxOgreWindow):
    terrain = None
    
    commandhistory = []
    historypointer = 0
    
    selectedEntry = None
    selectedCoords = None
    
    currentStatusMsg = ""
    
    cameralandcollisionenabled = True
    
    entries = {}

    # movement related
    keyPress = ogre.Vector3(0,0,0)
    moveVector = ogre.Vector3(0,0,0)
    virtualMoveNode = None
    
    # selection related
    selectionMaterial = None
    selectionMaterialAnimState = 0


    SelectedArrow = None
    StartDragLeftX = (0,0)
    StartDragLeftY = (0,0)
    TranslationRotationMode = False
    TranslateNode = None
    RotateNode = None
    stickCurrentObjectToGround = False
    
    
    
    def __init__(self, parent, ID, size = wx.Size(200,200), rordir = "", maininstance=None, **kwargs): 
        self.rordir = rordir
        self.maininstance = maininstance
        if not maininstance is None:
            self.sceneManager = maininstance.sceneManager
        self.parent = parent
        self.size = size
        self.kwargs = kwargs
        self.ID = ID
        wxOgreWindow.__init__(self, self.parent, self.ID, size = self.size, **self.kwargs) 
        myDrop = MyDropTarget(self)
        self.SetDropTarget(myDrop)

    def CameraLandCollision(self, value):
        self.cameralandcollisionenabled = value
        
    def animateSelection(self):
        if not self.selectionMaterial is None:
            self.selectionMaterialAnimState += 0.01
            if self.selectionMaterialAnimState >= 0.2:
                self.selectionMaterialAnimState = - 0.2
            val = 0.8 + abs(self.selectionMaterialAnimState)
            #print val
            self.selectionMaterial.setDiffuse(1, 0.3, 0, val)
            self.selectionMaterial.setSpecular(1, 0.3, 0, val)

    def OnFrameStarted(self):
        if self.cameralandcollisionenabled:
            self.cameraLandCollision()
        self.animateSelection()
        if not self.TranslateNode is None:
            if self.selectedEntry:
                if not self.selectedEntry.data.mayRotate and self.TranslationRotationMode:
                    self.TranslationRotationMode = False

                if self.TranslationRotationMode:
                    # rotation mode
                    self.TranslateNode.setScale(0,0,0)
                    self.RotateNode.setScale(self.arrowScale,self.arrowScale,self.arrowScale)
                else:
                    # translation mode
                    self.TranslateNode.setScale(self.arrowScale,self.arrowScale,self.arrowScale)
                    self.RotateNode.setScale(0,0,0)
            else:
                self.TranslateNode.setScale(0,0,0)
                self.RotateNode.setScale(0,0,0)
            if not self.selectedCoords is None:
                self.TerrainSelectNode.setScale(0.2,0.2,0.2)
            else:
                self.TerrainSelectNode.setScale(0,0,0)
                
                
        #move cam a bit
        if not self.moveVector is None:
            """ DEBUG STATEMENTS
            pos = self.moveVector
            kp = self.keyPress
            print "MV: %.3f %.3f %.3f\tKP: %.3f %.3f %.3f" % (pos.x,pos.y,pos.z,kp.x,kp.y,kp.z)
            """
            self.moveVector += self.keyPress
            self.camera.moveRelative(self.moveVector)
            self.moveVector *= SLOW_DOWN_FACTOR # each iteration slow the movement down by some fator
            if self.moveVector < self.moveVector.normalize()*LOW_SPEED_THRESHOLD:
                self.moveVector *= 0

    def OnFrameEnded(self): 
        pass 
        
        
    def cameraLandCollision(self):
        try:
            camPos = self.camera.getPosition()
            cameraRay = ogre.Ray(ogre.Vector3(camPos.x, 5000, camPos.z), ogre.Vector3.NEGATIVE_UNIT_Y)
            self.terrainRaySceneQuery.setRay(cameraRay)
            #Perform the scene query
            result = self.terrainRaySceneQuery.execute()
            if len(result) > 0 and not result[0] is None and not result[0].worldFragment is None:
                terrainHeight = result[0].worldFragment.singleIntersection.y
                if ((terrainHeight + 1) > camPos.y):
                    self.camera.setPosition(camPos.x, terrainHeight + 1, camPos.z)
        except:
            pass

    
    def SceneInitialisation(self):
        hasparent = (not self.sceneManager is None)
        if not hasparent:
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
            self.sceneManager = getOgreManager().createSceneManager(ogre.ST_EXTERIOR_CLOSE)
        else:
            self.terrain = self.maininstance.terrain
        # create a camera
        cameraUUID = randomID()
        self.camera = self.sceneManager.createCamera(str(cameraUUID)+"camera")
        self.camera.lookAt(ogre.Vector3(0, 0, 0)) 
        self.camera.setPosition(ogre.Vector3(0, 0, 100))
        self.camera.nearClipDistance = 0.1
        self.camera.setAutoAspectRatio(True) 

        # create the Viewport"
        self.viewport = self.renderWindow.addViewport(self.camera, 0, 0.0, 0.0, 1.0, 1.0) 
        self.viewport.backgroundColour = ogre.ColourValue(0, 0, 0) 

        #set some default values
        self.sceneDetailIndex = 0
        self.filtering = ogre.TFO_BILINEAR

        # bind mouse and keyboard
        self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown) 
        self.Bind(wx.EVT_KEY_UP, self.onKeyUp) 
        self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)

        self.virtualMoveNode = self.sceneManager.getRootSceneNode().createChildSceneNode()
        
        # this is for debugging of the grid system:
        #self.virtualMoveNode.attachObject(self.sceneManager.createEntity("afsdfsdfsfsdfsdfasdf", "arrow.mesh") )

        #create objects
        self.populateScene()
        

    def updateWaterPlane(self):
        self.waternode.setPosition(1500, self.terrain.WaterHeight + 200, 1500)
    
    def createWaterPlane(self):
        if self.terrain.WaterHeight is None:
            return
        plane = ogre.Plane() 
        plane.normal = ogre.Vector3(0, 1, 0) 
        plane.d = 200 
        # see http://www.ogre3d.org/docs/api/html/classOgre_1_1MeshManager.html#Ogre_1_1MeshManagera5
        waterid = str(randomID())
        mesh = ogre.MeshManager.getSingleton().createPlane(waterid+'WaterPlane', "General", plane, 3000, 3000, 
                                                    20, 20, True, 1, 200.0, 200.0, ogre.Vector3(0, 0, 1),
                                                    ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY, 
                                                    ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY, 
                                                    True, True)
        self.waterentity = self.sceneManager.createEntity(waterid+"entity", waterid+'WaterPlane')
        self.waterentity.setMaterialName('mysimple/water')
        
        self.waternode = self.sceneManager.getRootSceneNode().createChildSceneNode()
        self.waternode.attachObject(self.waterentity) 
        self.updateWaterPlane()
        

    def getSelectionPositionRotation(self):
        if not self.selectedEntry is None:
            return self.getPositionRotation(self.selectedEntry.node)
                
    def getPositionRotation(self, obj):
        scale = obj.getScale()
        obj.setScale(1, 1, 1)
        obj.rotate(ogre.Vector3.UNIT_X, ogre.Degree(90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        pos = obj.getPosition()
        rot = obj.getOrientation()
        rot.normalise()
        obj.rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        obj.setScale(scale)

        rotx = ogre.Radian(rot.getPitch(False)).valueDegrees()
        roty = ogre.Radian(rot.getRoll(False)).valueDegrees()
        rotz = -ogre.Radian(rot.getYaw(False)).valueDegrees() 
        return pos.x, pos.y, pos.z, rotx, roty, rotz
        
    def reattachArrows(self, entity):
        self.TranslateNode.setPosition(entity.getParentNode().getPosition())
        self.TranslateNode.setOrientation(entity.getParentNode().getOrientation())
        
        self.RotateNode.setOrientation(entity.getParentNode().getOrientation())
        self.RotateNode.setPosition(entity.getParentNode().getPosition())
        
        self.virtualMoveNode.setOrientation(entity.getParentNode().getOrientation())
        self.virtualMoveNode.setPosition(entity.getParentNode().getPosition())
        
    def createArrows(self):
        if not self.TranslateNode is None:
            return
        #translation nodes
        n = self.sceneManager.getRootSceneNode().createChildSceneNode("movearrowsnode") 
        nx = n.createChildSceneNode("movearrowsnodeX")
        ex = self.sceneManager.createEntity("movearrowsX", "arrow.mesh") 
        ex.setMaterialName("mysimple/transred")
        nx.attachObject(ex)

        ny = n.createChildSceneNode("movearrowsnodeY")
        ey = self.sceneManager.createEntity("movearrowsY", "arrow.mesh") 
        ey.setMaterialName("mysimple/transgreen")
        ny.attachObject(ey)
        ny.rotate(ogre.Vector3.UNIT_Y, ogre.Degree(90).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)

        nz = n.createChildSceneNode("movearrowsnodeZ")
        ez = self.sceneManager.createEntity("movearrowsZ", "arrow.mesh") 
        ez.setMaterialName("mysimple/transblue")
        nz.attachObject(ez)
        nz.rotate(ogre.Vector3.UNIT_Z, ogre.Degree(90).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)

        #rotation nodes
        nr = self.sceneManager.getRootSceneNode().createChildSceneNode("rotatearrowsnode") 
        nrx = nr.createChildSceneNode("rotatearrowsnodeX")
        erx = self.sceneManager.createEntity("rotatearrowsX", "roundarrow.mesh") 
        erx.setMaterialName("mysimple/transblue")
        nrx.rotate(ogre.Vector3.UNIT_X, ogre.Degree(90).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        nrx.attachObject(erx)
        nrx.setInheritOrientation(True)

        nry = nr.createChildSceneNode("rotatearrowsnodeY")
        ery = self.sceneManager.createEntity("rotatearrowsY", "roundarrow.mesh") 
        nry.rotate(ogre.Vector3.UNIT_X, ogre.Degree(180).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        nry.rotate(ogre.Vector3.UNIT_Y, ogre.Degree(90).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        ery.setMaterialName("mysimple/transred")
        nry.setInheritOrientation(True)
        nry.attachObject(ery)

        nrz = nr.createChildSceneNode("rotatearrowsnodeZ")
        erz = self.sceneManager.createEntity("rotatearrowsZ", "roundarrow.mesh") 
        erz.setMaterialName("mysimple/transgreen")
        nrz.setInheritOrientation(True)
        nrz.attachObject(erz)
        
        # terrain selection node
        nt = self.sceneManager.getRootSceneNode().createChildSceneNode("terrainselectnode") 
        et = self.sceneManager.createEntity("circlepointer", "cylinder.mesh") 
        et.setMaterialName("mysimple/terrainselect")
        nt.rotate(ogre.Vector3.UNIT_X, ogre.Degree(90).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        nt.attachObject(et)
        nt.setScale(5,5,5)
       
        self.TerrainSelectNode = nt
        self.TranslateNode = n
        self.RotateNode = nr
        n.setPosition(0,0,0)
        nr.setPosition(0,0,0)

    def deselectSelection(self):
        if self.selectedEntry:
            #self.selectedEntry.entity.getSubEntity(0).setMaterialName(self.oldmaterial)
            self.selectedEntry.entity.setMaterialName(self.oldmaterial)   
            self.selectedEntry.entity.getParentSceneNode().showBoundingBox(False)
    
    
    def changeSelection(self, newnode):
        self.deselectSelection()
        key = newnode.getName()[:-len("entity")]
        self.selectedEntry = self.entries[key]
        
        self.oldmaterial = self.selectedEntry.entity.getSubEntity(0).getMaterialName()
        
        
        newmatname = "mysimple/selectedobject"
        selectedmat = ogre.MaterialManager.getSingleton().getByName(newmatname)
        mat = ogre.MaterialManager.getSingleton().getByName(self.selectedEntry.entity.getSubEntity(0).getMaterialName())
        if not mat is None:
            mat.copyDetailsTo(selectedmat)
        newmat = ogre.MaterialManager.getSingleton().getByName(newmatname)
        newmat.setSceneBlending(ogre.SceneBlendFactor.SBF_SOURCE_ALPHA, ogre.SceneBlendFactor.SBF_DEST_ALPHA )
        newmat.setSelfIllumination(1, 0.3, 0)
        newmat.setDiffuse(1, 0.3, 0, 0.9)
        newmat.setAmbient(1, 0.3, 0)
        newmat.setSpecular(1, 0.3, 0, 0.9)
        self.selectionMaterial = newmat
        #self.selectedEntry.entity.getSubEntity(0).setMaterialName(snewmatname)
        self.selectedEntry.entity.setMaterialName(newmatname)
        self.selectedEntry.entity.getParentSceneNode().showBoundingBox(True)
        self.reattachArrows(self.selectedEntry.entity)
        self.arrowScale = self.selectedEntry.entity.getBoundingRadius() / 100

    def free(self):
        #self.sceneManager.clearScene()
        self.sceneManager.destroyAllManualObjects()
              
        # try to clear things up
        #try:
        for key in self.entries.keys():
            entry = self.entries[key]
            if not entry.node is None:
                try:
                    entry.node.detachAllObjects()
                    self.sceneManager.destroySceneNode(entry.node.getName())
                except:
                    pass
            if not entry.entity is None:
                try:
                    self.sceneManager.destroyEntity(entry.entity)
                except:
                    pass
            if not entry.data is None:
                del entry.data
            del self.entries[key]
                
                    
        try:
            self.waternode.detachAllObjects()
            self.sceneManager.destroySceneNode(self.waternode)
            self.sceneManager.destroyEntity(self.waterentity)
        except:
            pass
        
        self.terrain = None
        self.entries = {}
        #except:
        #    pass
    
    def updateDataStructures(self):
        for uuid in self.entries.keys():
            entry = self.entries[uuid]
            x, y, z, rotx, roty, rotz = self.getPositionRotation(entry.node)
            if entry.data.name.lower() in ['truck', 'load']:
                rotx -= 90
            entry.data.setPosition(x, y, z)
            entry.data.setRotation(rotx, roty, rotz)
    
    def SaveTerrain(self, fn = None):
        self.updateDataStructures()
        if not self.terrain is None:
            res = self.terrain.save(fn)
            self.currentStatusMsg = "Terrain saved!"
            return res

            
    def LoadTerrain(self, filename):
        if not self.terrain is None:
            self.free()
        #print filename
        self.terrain = RoRTerrain(filename)
        #print len(self.terrain.objects)

        cfgfile = os.path.join(os.path.dirname(filename), self.terrain.TerrainConfig)
        self.sceneManager.setWorldGeometry(cfgfile)

        self.createWaterPlane()
        self.createArrows()
        try:
            if not self.terrain.CharacterStartPosition is None:
                self.camera.setPosition(self.terrain.CharacterStartPosition)
            else:
                self.camera.setPosition(self.terrain.CameraStartPosition)
        except Exception, err:
            log().error("Error while setting initial camera:")
            log().error(str(err))
        
        for truck in self.terrain.trucks:
            try:
                self.addTruckToTerrain(data=truck)
            except Exception, err:
                log().error("Error while adding a truck to the terrain:")
                log().error(str(err))

        for load in self.terrain.loads:
            try:
                self.addTruckToTerrain(data=load)
            except Exception, err:
                log().error("Error while adding a load to the terrain:")
                log().error(str(err))

        for object in self.terrain.objects:
            try:
                self.addObjectToTerrain(data=object)
            except Exception, err:
                log().error("Error while adding an object to the terrain:")
                log().error(str(err))

        self.currentStatusMsg = "Terrain loaded" 
    
    def addObjectToTerrain(self, data=None, odefFilename=None, coords=None):
        if coords is None:
            coords = self.selectedCoords
        if coords is None and data is None:
            return False

        uuid = randomID()

        if data is None:
            data = Object()
            data.name = os.path.basename(odefFilename).split(".")[0]
            data.filename = os.path.basename(odefFilename).split(".")[0]
            data.comments = ['// added by terrain editor\n']
            data.setPosition(coords.x, coords.y, coords.z)
            data.setRotation(0, 0, 0)
            data.additionaloptions =[]
            self.terrain.objects.append(data)        
        else:
            odefFilename = data.filename

        if os.path.basename(odefFilename) == odefFilename:
            if odefFilename[-5:] != ".odef":
                odefFilename += ".odef"
            odefFilename = self.rordir + "\\data\\objects\\"+odefFilename
        
        meshname = None
        try:
            (meshname, sx, sy, sz) = loadOdef(odefFilename)
        except Exception, err:
            data.error=True
            log().error("error while processing odef file %s" % odefFilename)
            log().error(str(err))
            return
        
        entry = Entry()
        entry.uuid = uuid
        entry.node = self.sceneManager.getRootSceneNode().createChildSceneNode(str(uuid)+"node")
        entry.entity = self.sceneManager.createEntity(str(uuid)+"entity", meshname)
        entry.data = data
        
        entry.node.attachObject(entry.entity)
        entry.node.rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        entry.node.rotate(ogre.Vector3.UNIT_Z, ogre.Degree(data.rotz).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)        
        entry.node.rotate(ogre.Vector3.UNIT_Y, ogre.Degree(data.roty).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        entry.node.rotate(ogre.Vector3.UNIT_X, ogre.Degree(data.rotx).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        entry.node.setPosition(data.x, data.y, data.z)
        if not sx is None:
            entry.node.setScale(sx, sy, sz)
            
        self.entries[uuid] = entry
        return True

    def addTruckToTerrain(self, data=None, truckFilename=None, coords=None):
        if coords is None:
            coords = self.selectedCoords
        if coords is None and data is None:
            return False

        uuid = randomID()

        if data is None:
            data = Object()
            data.name = truckFilename.split(".")[-1] # truck or load
            data.filename = os.path.basename(truckFilename)
            data.comments = ['// added by terrain editor\n']
            data.setPosition(coords.x, coords.y, coords.z)
            data.setRotation(0, 0, 0)
            data.additionaloptions =[data.filename]
            if truckFilename.split(".")[-1].lower() == "truck":
                self.terrain.trucks.append(data)
            elif truckFilename.split(".")[-1].lower() == "load":
                self.terrain.loads.append(data)
        else:
            truckFilename = data.filename

        if os.path.basename(truckFilename) == truckFilename:
            truckFilename = self.rordir + "\\data\\trucks\\"+truckFilename
            
        entry = Entry()
        entry.uuid = uuid
        entry.node, entry.entity, entry.manualobject = createTruckMesh(self.sceneManager, truckFilename, uuid)        
        entry.data = data
        
        entry.node.rotate(ogre.Vector3.UNIT_Z, ogre.Degree(data.rotz).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)        
        entry.node.rotate(ogre.Vector3.UNIT_Y, ogre.Degree(data.roty).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        entry.node.rotate(ogre.Vector3.UNIT_X, ogre.Degree(data.rotx).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        entry.node.setPosition(data.x, data.y, data.z)
        self.entries[uuid] = entry
        return True



    def getPointedPosition(self, event):
        x, y = event.GetPosition() 
        width, height, a, b, c = self.renderWindow.getMetrics()       
        mouseRay = self.camera.getCameraToViewportRay((x / float(width)), (y / float(height)));
        myRaySceneQuery = self.sceneManager.createRayQuery(ogre.Ray());
        myRaySceneQuery.setRay(mouseRay)
        result = myRaySceneQuery.execute()
        if len(result) > 0 and not result[0] is None and not result[0].worldFragment is None:
            return result[0].worldFragment.singleIntersection
        return None
                       

    def populateScene(self):  
        self.sceneManager.AmbientLight = ogre.ColourValue(0.7, 0.7, 0.7 )

        fadeColour = (0.8, 0.8, 0.8)
        self.sceneManager.setFog(ogre.FOG_LINEAR, fadeColour, 0.001, 5000.0, 10000.0)
        self.renderWindow.getViewport(0).BackgroundColour = fadeColour

        #l = self.sceneManager.createLight(str(randomID())+"MainLight")
        #l.setPosition(20,80,50)

        #create ray template
        self.selectionRaySceneQuery = self.sceneManager.createRayQuery(ogre.Ray());
        self.terrainRaySceneQuery = self.sceneManager.createRayQuery(ogre.Ray());
        
        # setup the sky plane
        plane = ogre.Plane()
        plane.d = 5000
        plane.normal = -ogre.Vector3.UNIT_Y

    def toggleTranslationRotationMode(self):
        self.TranslationRotationMode = not self.TranslationRotationMode
 
    def StickVectorToGround(self, nPos):
        nRay = ogre.Ray(ogre.Vector3(nPos.x, 5000, nPos.z), ogre.Vector3.NEGATIVE_UNIT_Y)
        self.terrainRaySceneQuery.setRay(nRay)
        #Perform the scene query
        result = self.terrainRaySceneQuery.execute()
        if len(result) > 0 and not result[0] is None and not result[0].worldFragment is None:
            terrainHeight = result[0].worldFragment.singleIntersection.y
            return ogre.Vector3(nPos.x, terrainHeight, nPos.z)
        return nPos

    def ObjectResetRotation(self):
        if self.selectedEntry:
            self.selectedEntry.node.resetOrientation()
            self.selectedEntry.node.rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
            self.RotateNode.resetOrientation()
            self.RotateNode.rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
            
    def selectarrow(self, arrow):
        if self.SelectedArrow.getSubEntity(0).getMaterialName()[-3:] != "sel":
            self.SelectedArrow.setMaterialName(self.SelectedArrow.getSubEntity(0).getMaterialName()+"sel")
    
    def deselectarrow(self, arrow):
        if self.SelectedArrow.getSubEntity(0).getMaterialName()[-3:] == "sel":
            self.SelectedArrow.setMaterialName(self.SelectedArrow.getSubEntity(0).getMaterialName()[:-3])
        
    def selectTerrain(self, event):
        self.deselectSelection()
        self.selectedEntry = None
        self.selectedCoords = self.getPointedPosition(event)
        self.selectedCoords += ogre.Vector3(0,1,0)
        self.TerrainSelectNode.setPosition(self.selectedCoords)
    
    def selectnew(self, event):
        x, y = event.GetPosition() 
        width, height, a, b, c = self.renderWindow.getMetrics()       
        mouseRay = self.camera.getCameraToViewportRay((x / float(width)), (y / float(height)));
        self.selectionRaySceneQuery.setRay(mouseRay)
        self.selectionRaySceneQuery.setSortByDistance(True)
        result = self.selectionRaySceneQuery.execute()

        #ensure that arrows are selected first, always!
        for r in result:
            if not r is None and not r.movable is None and r.movable.getMovableType() == "Entity":
                if r.movable.getName() in ['movearrowsY', 'movearrowsX', 'movearrowsZ', 'rotatearrowsX', 'rotatearrowsY' ,'rotatearrowsZ']:
                    if not self.SelectedArrow is None:
                        self.deselectarrow(self.SelectedArrow)
                    self.SelectedArrow = r.movable
                    self.selectarrow(self.SelectedArrow)
                    return
        selectedSomething = False
        ignorearray = []
        ignorearray.append("circlepointer")
        if not self.terrain.WaterHeight is None:
            ignorearray.append(self.waterentity.getName())
        for r in result:
            if not r is None and not r.movable is None and r.movable.getMovableType() == "Entity":
                if r.movable.getName() in ignorearray:
                    # you cannot select these objects
                    continue
                if not self.selectedEntry is None and self.selectedEntry.entity.getName() == r.movable.getName():
                    continue
                #print r.movable.getMovableType(), r.movable.getName()
                if not self.SelectedArrow is None:
                    self.deselectarrow(self.SelectedArrow)
                self.SelectedArrow = None
                self.selectedCoords = None
                selectedSomething = True
                self.changeSelection(r.movable)
                break
        if not selectedSomething:
            #print "no entities found, selecting ground"
            self.selectTerrain(event)

    def controlSelectedObject(self,action, value):
        pass

    def addObjectToHistory(self, entry):
        if len(self.commandhistory) > 0:
            if self.historypointer < len(self.commandhistory):
                del self.commandhistory[self.historypointer:]

        pos = entry.node.getPosition()
        rot = entry.node.getOrientation()
                    
        if len(self.commandhistory) > 0:
            # check if double
            hentry = self.commandhistory[-1]
            if hentry.position == pos and hentry.rotation == rot:
                return
        
        hentry = HistoryEntry()
        hentry.uuid = entry.uuid
        hentry.position = pos
        hentry.rotation = rot
        self.commandhistory.append(hentry)
        self.historypointer = len(self.commandhistory)

    def undoHistory(self):
        if self.historypointer == 0:
            return
        self.SelectedArrow = None
        
        
        self.historypointer -= 1
        hentry = self.commandhistory[self.historypointer]
        self.entries[hentry.uuid].node.setPosition(hentry.position)
        self.entries[hentry.uuid].node.setOrientation(hentry.rotation)
        
        # update node positions
        self.TranslateNode.setPosition(self.entries[hentry.uuid].node.getPosition())
        self.RotateNode.setPosition(self.entries[hentry.uuid].node.getPosition())
        #self.TranslateNode.setOrientation(self.entries[hentry.uuid].node.getOrientation())
        self.RotateNode.setOrientation(self.entries[hentry.uuid].node.getOrientation())
        
        #self.entries[obj.uuid].node.setPosition(obj.node.getPosition)
        self.currentStatusMsg = "undo step %d of %d" % (self.historypointer+1, len(self.commandhistory))
        
    def redoHistory(self):
        if self.historypointer + 1 >= len(self.commandhistory):
            return
        self.SelectedArrow = None        
        
        self.historypointer += 1
        hentry = self.commandhistory[self.historypointer]
        self.entries[hentry.uuid].node.setPosition(hentry.position)
        self.entries[hentry.uuid].node.setOrientation(hentry.rotation)
        
        # update node positions
        self.TranslateNode.setPosition(self.entries[hentry.uuid].node.getPosition())
        self.RotateNode.setPosition(self.entries[hentry.uuid].node.getPosition())
        #self.TranslateNode.setOrientation(self.entries[hentry.uuid].node.getOrientation())
        self.RotateNode.setOrientation(self.entries[hentry.uuid].node.getOrientation())
        
        #self.entries[obj.uuid].node.setPosition(obj.node.getPosition)
        self.currentStatusMsg = "redo step %d of %d" % (self.historypointer+1, len(self.commandhistory))
                


    def rotateSelected(self, axis, amount, steps=True):
        if not self.selectedEntry:
            return
        
        self.virtualMoveNode.rotate(axis, amount, relativeTo=ogre.Node.TransformSpace.TS_LOCAL)
        newrot = self.virtualMoveNode.getOrientation()
        
        # todo: get this working!
        if False:
            print amount
            stepsize = 10
            rotzz = -ogre.Radian(newrot.getYaw()).valueDegrees()
            rotz = rotzz - (rotzz % stepsize)
            rotyy = ogre.Radian(newrot.getRoll()).valueDegrees()
            roty = rotyy - (rotyy % stepsize)
            rotxx = ogre.Radian(newrot.getPitch()).valueDegrees()
            rotx = rotxx - (rotxx % stepsize)
            print rotx, roty, rotz, rotxx, rotyy, rotzz
            self.virtualMoveNode.resetOrientation()
            self.virtualMoveNode.rotate(ogre.Vector3.UNIT_Z, ogre.Degree(rotz).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
            self.virtualMoveNode.rotate(ogre.Vector3.UNIT_Y, ogre.Degree(roty).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
            self.virtualMoveNode.rotate(ogre.Vector3.UNIT_X, ogre.Degree(rotx).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        
            newrot = self.virtualMoveNode.getOrientation()

        self.RotateNode.setOrientation(newrot)        
        self.addObjectToHistory(self.selectedEntry)
        self.selectedEntry.node.setOrientation(newrot)
                
    def translateSelected(self, vector, steps=True):
        if not self.selectedEntry:
            return
        self.virtualMoveNode.translate(vector, relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        newpos = self.virtualMoveNode.getPosition()
        
        if steps:
            stepsize = 2
            x = newpos.x - (newpos.x % stepsize)
            y = newpos.y - (newpos.y % stepsize)
            z = newpos.z - (newpos.z % stepsize)
            newpos = ogre.Vector3(x, y, z)

        if self.stickCurrentObjectToGround:
            newpos = self.StickVectorToGround(newpos)
        

        self.TranslateNode.setPosition(newpos)
        self.RotateNode.setPosition(newpos)
        self.addObjectToHistory(self.selectedEntry)
        self.selectedEntry.node.setPosition(newpos)

    def controlArrows(self, event):
        if self.SelectedArrow is None:
            return
        
        forcex = float(0)
        forcey = float(0)
        if event.Dragging() and event.LeftIsDown():
            x,y = event.GetPosition() 
            forcex = float(self.StartDragLeftX - x)
            forcey = float(self.StartDragLeftY - y)
            self.StartDragLeftX, self.StartDragLeftY = event.GetPosition()

        forcex /= 2
        forcey /= 2
        if event.ShiftDown():
            forcex /= 10
            forcey /= 10
        
        LockSteps = event.AltDown()
        
        forceDegree = ogre.Degree(forcex).valueRadians()

        if not event.Dragging():
            return
        
        #print self.SelectedArrow.getName(), forcex, forcey
        if self.SelectedArrow.getName() == 'movearrowsX':
            self.translateSelected(ogre.Vector3(forcex, 0, 0), LockSteps)
        elif self.SelectedArrow.getName() == 'movearrowsY':
            self.translateSelected(ogre.Vector3(0, forcex, 0), LockSteps)
        elif self.SelectedArrow.getName() == 'movearrowsZ':
            self.translateSelected(ogre.Vector3(0, 0, forcex), LockSteps)
        elif self.SelectedArrow.getName() == 'rotatearrowsX':
            self.rotateSelected(ogre.Vector3.UNIT_Y, forceDegree, LockSteps)
        elif self.SelectedArrow.getName() == 'rotatearrowsY':
            self.rotateSelected(ogre.Vector3.UNIT_X, forceDegree, LockSteps)
        elif self.SelectedArrow.getName() == 'rotatearrowsZ':
            self.rotateSelected(ogre.Vector3.UNIT_Z, forceDegree, LockSteps)
                       
    def onMouseEvent(self, event):
        if self.terrain is None:
            return
       
        width, height, a, b, c = self.renderWindow.getMetrics()       
        
        self.controlArrows(event)

        if event.RightDown() or event.LeftDown():
            self.SetFocus()
    
        if event.RightDown(): #Precedes dragging 
            self.StartDragX, self.StartDragY = event.GetPosition() #saves position of initial click 
        if event.Dragging() and event.RightIsDown() and event.ControlDown():
            x,y = event.GetPosition() 
            dx = self.StartDragX - x
            dy = self.StartDragY - y
            self.StartDragX, self.StartDragY = x, y 
            if event.ShiftDown():
                dx = float(dx) / 10
                dy = float(dy) / 10
            self.camera.moveRelative(ogre.Vector3(dx,-dy,0))
        elif event.Dragging() and event.RightIsDown(): #Dragging with RMB 
            x,y = event.GetPosition() 
            dx = self.StartDragX - x
            dy = self.StartDragY - y
            self.StartDragX, self.StartDragY = x, y 
        
            self.camera.yaw(ogre.Degree(dx/3.0)) 
            self.camera.pitch(ogre.Degree(dy/3.0)) 

        if event.LeftDown() and event.ControlDown() and not self.selectedEntry is None:
            pos = self.getPointedPosition(event)
            if not pos is None:
                self.addObjectToHistory(self.selectedEntry)
                self.TranslateNode.setPosition(pos)
                self.RotateNode.setPosition(pos)
                self.selectedEntry.node.setPosition(pos)
            return
        if event.LeftDown():
            self.selectnew(event)
            self.StartDragLeftX, self.StartDragLeftY = event.GetPosition() #saves position of initial click 

        if event.GetWheelRotation() != 0:
            dir = 5
            if event.ShiftDown():
                dir *= SHIFT_SPEED_FACTOR   # speed is increased by a factor of 16
                        
            if event.GetWheelRotation() > 0:
                dir *= -1   # move backwards
            
            self.moveVector += ogre.Vector3(0, 0, dir)
        event.Skip()


    def onKeyDown(self,event):
        if self.terrain is None:
            return

        #print event.m_keyCode
        d = 0.5
        if event.ShiftDown():
            d *= SHIFT_SPEED_FACTOR

        if event.m_keyCode == 65: # A, wx.WXK_LEFT:
            self.keyPress.x = -d
        elif event.m_keyCode == 68: # D, wx.WXK_RIGHT:
            self.keyPress.x = d
        elif event.m_keyCode == 87: # W ,wx.WXK_UP:
            self.keyPress.z = -d
        elif event.m_keyCode == 83: # S, wx.WXK_DOWN:
            self.keyPress.z = d
        elif event.m_keyCode == 70: # F
            self.undoHistory()
        elif event.m_keyCode == 71: # G
            self.redoHistory()
        elif event.m_keyCode == wx.WXK_PAGEUP:
            self.keyPress.y = d
        elif event.m_keyCode == wx.WXK_PAGEDOWN:
            self.keyPress.y = -d
            
        elif event.m_keyCode == 81: # Q, wx.WXK_LEFT:
            self.toggleTranslationRotationMode()
        elif event.m_keyCode == 84: # 84 = T
            if self.filtering == ogre.TFO_BILINEAR:
                self.filtering = ogre.TFO_TRILINEAR
                self.Aniso = 1
            elif self.filtering == ogre.TFO_TRILINEAR:
                self.filtering = ogre.TFO_ANISOTROPIC
                self.Aniso = 8
            else:
                self.filtering = ogre.TFO_BILINEAR
                self.Aniso = 1
            ogre.MaterialManager.getSingleton().setDefaultTextureFiltering(self.filtering)
            ogre.MaterialManager.getSingleton().setDefaultAnisotropy(self.Aniso)
        elif event.m_keyCode == 82: # 82 = R
            detailsLevel = [ ogre.PM_SOLID,
                             ogre.PM_WIREFRAME,
                             ogre.PM_POINTS ]
            self.sceneDetailIndex = (self.sceneDetailIndex + 1) % len(detailsLevel)
            self.camera.polygonMode=detailsLevel[self.sceneDetailIndex]
        elif event.m_keyCode == 80: # 80 = P
            pos = self.camera.getDerivedPosition()
            o = self.camera.getDerivedOrientation()
            print "P: %.3f %.3f %.3f O: %.3f %.3f %.3f %.3f" % (pos.x,pos.y,pos.z, o.w,o.x,o.y,o.z)
              
        event.Skip()
    
    def onKeyUp(self,event):
        if self.terrain is None:
            return
            
        if event.m_keyCode == 65: # A, wx.WXK_LEFT:
            self.keyPress.x = 0
        elif event.m_keyCode == 68: # D, wx.WXK_RIGHT:
            self.keyPress.x = 0
        elif event.m_keyCode == 87: # W ,wx.WXK_UP:
            self.keyPress.z = 0
        elif event.m_keyCode == 83: # S, wx.WXK_DOWN:
            self.keyPress.z = 0
        elif event.m_keyCode == wx.WXK_PAGEUP:
            self.keyPress.y = 0
        elif event.m_keyCode == wx.WXK_PAGEDOWN:
            self.keyPress.y = 0
        event.Skip()
        