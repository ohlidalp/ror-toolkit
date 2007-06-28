#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx, os, os.path
import ogre.renderer.OGRE as ogre 
from ror.truckparser import *
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from random import random

ADDEDBY = "//added by the terrrain editor:\n"

class RoRTerrainOgreWindow(wxOgreWindow):

    #myObjects = {}
    myODefs = {}
    
    def __init__(self, parent, ID, size = wx.Size(200,200), rordir = "", **kwargs): 
        self.rordir = rordir
        self.rand = str(random())
        self.TerrainLoaded = False
        self.mCount = 0
        self.rand = str(random())
        self.parent = parent
        self.size = size
        self.kwargs = kwargs
        self.ID = ID
        self.mSelected = None
        self.selectedCoords = None
        self.meshesorder = []
        self.additionaloptions = {}
        self.trucksorder = []
        self.myODefs = {}
        self.trucks = {}
        self.comments = {}
        self.meshes = {}
        self.moveVector = None
        self.moveForce = 0
        self.selectionMaterial = None
        self.selectionMaterialAnimState = 0
        wxOgreWindow.__init__(self, self.parent, self.ID, size = self.size, **self.kwargs) 

        
    def animateSelection(self):
        if not self.selectionMaterial is None:
            self.selectionMaterialAnimState += 0.01
            if self.selectionMaterialAnimState >= 0.4:
                self.selectionMaterialAnimState = - 0.4
            val = 0.6 + abs(self.selectionMaterialAnimState)
            #print val
            self.selectionMaterial.setDiffuse(1, 0.3, 0, val)
            self.selectionMaterial.setSpecular(1, 0.3, 0, val)

    def OnFrameStarted(self): 
        self.cameraLandCollision()
        self.animateSelection()
        if not self.TranslateNode is None:
            if self.mSelected:
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
        if not self.moveVector is None and self.moveForce > 0:
            self.camera.moveRelative(self.moveVector * self.moveForce)
            self.moveForce *= 0.75
            if self.moveForce < 0.000:
                self.moveForce = 0

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

        # create a camera
        self.camera = self.sceneManager.createCamera('Camera' + self.rand) 
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
        self.Bind(wx.EVT_MOUSE_EVENTS, self.onMouseEvent)
        
        #create objects
        self.populateScene()
        
    def loadOdef(self, objname):
        try:
            f=open(self.rordir+"\\data\\objects\\%s.odef" % (objname), 'r')
            content = f.readlines()
            f.close()
            meshname = content[0].strip()
            scalearr = content[1].split(",")
            self.myODefs[objname] = []
            if len(content) > 2:
                for i in range(1,len(content)):
                    line = content[i]
                    if line.lower().strip() == "end":
                        break
                    self.myODefs[objname].append(line.split(","))
                return (meshname, float(scalearr[0]), float(scalearr[1]), float(scalearr[2]))
            else:
                return (meshname, 1, 1, 1)
        except Exception, err:
            print "error while processing odef file of  %s" % objname
            print str(err)
        
    def updateWaterPlane(self):
        self.planenode.setPosition(1500, self.WaterHeight + 200, 1500)
    
    def createWaterPlane(self):
        if self.WaterHeight is None:
            return
        plane = ogre.Plane() 
        plane.normal = ogre.Vector3(0, 1, 0) 
        plane.d = 200 
        # see http://www.ogre3d.org/docs/api/html/classOgre_1_1MeshManager.html#Ogre_1_1MeshManagera5
        mesh = ogre.MeshManager.getSingleton().createPlane('WaterPlane' + self.rand, "General", plane, 3000, 3000, 
                                                    20, 20, True, 1, 50.0, 50.0, ogre.Vector3(0, 0, 1),
                                                    ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY, 
                                                    ogre.HardwareBuffer.HBU_STATIC_WRITE_ONLY, 
                                                    True, True)
        entity = self.sceneManager.createEntity('waterent', 'WaterPlane' + self.rand) 
        entity.setMaterialName('mysimple/water') 
        self.planenode = self.sceneManager.getRootSceneNode().createChildSceneNode()
        self.planenode.attachObject(entity) 
        self.updateWaterPlane()
        
        
    def processTerrnFile(self, content):
        #self.parent.cbObjects.Clear()
        linecounter = 0
        self.UsingCaelum = False
        self.WaterHeight = None
        comm = []
        for i in range(0, len(content)):
            if content[i].strip() == "":
                comm.append(content[i])
                continue
            if content[i].strip()[0:2] == "//":
                comm.append(content[i])
                continue
            if content[i].strip()[0:1] == ";":
                comm.append(content[i].replace(";","//"))
                continue
            if content[i].strip().lower() == "end":
                continue
            linecounter += 1
            if linecounter == 1:
                #terrain name
                self.TerrainName = content[i].strip()
                continue
            elif linecounter == 2:
                # .cfg file
                self.TerrainConfig = content[i].strip()
                continue
            if content[i].strip()[0].lower() == "w":
                self.WaterHeight = float(content[i].strip()[2:])
                continue
            if content[i].strip().lower() == "caelum":
                self.UsingCaelum = True
                continue
            if linecounter < 10 and len(content[i].split(",")) == 3:
                # sky color
                sc = content[i].split(",")
                self.SkyColor = (float(sc[0]), float(sc[1]), float(sc[2]))
                self.SkyColorLine = content[i]
                continue
            if linecounter < 10  and len(content[i].split(",")) == 9 or len(content[i].split(",")) == 6:
                # spawning Position
                sp = content[i].split(",")
                self.TruckStartPosition = ogre.Vector3(float(sp[0]), float(sp[1]), float(sp[2]))
                
                #insert truckshop
                # n = self.sceneManager.getRootSceneNode().createChildSceneNode("objectts") 
                # e = self.sceneManager.createEntity("objentts", "truckshop.mesh") 
                # n.attachObject(e) 
                # n.setPosition(self.TruckStartPosition)
                # n.rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90).valueRadians())
                # self.myObjects["objectts"] = n
                
                self.CameraStartPosition = ogre.Vector3(float(sp[3]), float(sp[4]), float(sp[5]))
                if len(sp) == 9:
                    self.CharacterStartPosition = ogre.Vector3(float(sp[6]), float(sp[7]), float(sp[8]))
                else:
                    self.CharacterStartPosition = None
                continue

            arr = content[i].split(",")
            #try:
            x = float(arr[0])
            y = float(arr[1])
            z = float(arr[2])
            rx = float(arr[3])
            ry = float(arr[4])
            rz = float(arr[5])
            objname = (arr[6]).strip().split("\t")
            if len(objname) == 1:
                objname = (arr[6]).strip().split(" ")
            #print objname
            if objname[0][0:5] == "truck" and len(objname) > 1:
                print "loading truck..."
                fn = self.rordir + "\\data\\trucks\\"+objname[-1].strip()
                n, entname = self.createTruckMesh(fn)
                self.comments[entname] = comm
                comm = []
                if not n is None:
                    n.rotate(ogre.Vector3.UNIT_X, ogre.Degree(rx).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
                    n.rotate(ogre.Vector3.UNIT_Y, ogre.Degree(ry).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
                    n.rotate(ogre.Vector3.UNIT_Z, ogre.Degree(-rz).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
                    n.setPosition(x, y, z)
                continue
            if objname[0][0:4] == "load" and len(objname) > 1:
                print "loading load...."
                fn = self.rordir + "\\data\\trucks\\"+objname[-1].strip()
                n, entname = self.createTruckMesh(fn)
                self.comments[entname] = comm
                comm = []
                if not n is None:
                    n.rotate(ogre.Vector3.UNIT_X, ogre.Degree(rx).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
                    n.rotate(ogre.Vector3.UNIT_Y, ogre.Degree(ry).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
                    n.rotate(ogre.Vector3.UNIT_Z, ogre.Degree(-rz).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
                    n.setPosition(x, y, z)
                continue
            firstobjname = objname[0]

            try:
                (meshname, sx, sy, sz) = self.loadOdef(firstobjname)
            except Exception, inst:
                print inst
                print "########## error loading odef of %s"  % firstobjname
                sx = None
            
            n = self.sceneManager.getRootSceneNode().createChildSceneNode("object" + str(i)+ firstobjname)
            entname = "objent" + str(i)+"_"+firstobjname
            e = self.sceneManager.createEntity(entname, meshname) 
            n.attachObject(e)

            #print "position: ", x,", ", y,", ", z
            #print "rotation: ", rx,", ", ry,", ", rz
            #print "scale: ", sx,", ", sy,", ", sz
            n.setPosition(x, y, z)
            n.rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
            n.rotate(ogre.Vector3.UNIT_Z, ogre.Degree(rz),relativeTo=ogre.Node.TransformSpace.TS_PARENT)
            n.rotate(ogre.Vector3.UNIT_Y, ogre.Degree(ry),relativeTo=ogre.Node.TransformSpace.TS_PARENT)
            n.rotate(ogre.Vector3.UNIT_X, ogre.Degree(rx),relativeTo=ogre.Node.TransformSpace.TS_PARENT)
            if not sx is None:
                n.setScale(sx, sy, sz)
            self.comments[entname] = comm
            comm = []
            self.meshesorder.append(entname)
            if len(objname) > 1:
                self.additionaloptions[entname] = objname[1:]
            self.meshes[entname] = n

            #except Exception, inst:
            #    print inst
            #    print "error parsing line %s" % content[i]
        self.createWaterPlane()
        self.createArrows()
        if not self.CharacterStartPosition is None:
            self.camera.setPosition(self.CharacterStartPosition)
        else:
            self.camera.setPosition(self.CameraStartPosition)

    def formatFloat(self, fl):
        return "%12s" % ("%0.6f" % (float(fl)))

        
    def getCommentsForObject(self, entname):
        if entname in self.comments.keys():
            #print self.comments[entname]
            return self.comments[entname];
        else:
            return ""
        
    def getSelectionPositionRotation(self):
        if not self.mSelected is None:
            return self.getPositionRotation(self.mSelected.getParentNode())
                
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
        
    def SaveTerrnFile(self, fn = None):
            if fn is None:
                fn = self.terrnfile
        # quick and dirty ;)
        #try:
            lines = []
            lines.append(self.TerrainName+"\n")
            lines.append(self.TerrainConfig+"\n")
            if not self.WaterHeight is None:
                lines.append("w "+str(self.WaterHeight)+"\n")
            if self.UsingCaelum:
                lines.append("caelum\n")
            lines.append(self.SkyColorLine.strip()+"\n")

            ar = []
            ar.append(str(self.TruckStartPosition.x))
            ar.append(str(self.TruckStartPosition.y))
            ar.append(str(self.TruckStartPosition.z))
            ar.append(str(self.CameraStartPosition.x))
            ar.append(str(self.CameraStartPosition.y))
            ar.append(str(self.CameraStartPosition.z))
            if not self.CharacterStartPosition is None:
                ar.append(str(self.CharacterStartPosition.x))
                ar.append(str(self.CharacterStartPosition.y))
                ar.append(str(self.CharacterStartPosition.z))
            startline = ", ".join(ar)+"\n"
            lines.append(startline)

            
            #save trucks and loads:
            
            for k in self.trucksorder:
            
                if k in self.comments.keys():
                    for c in self.comments[k]:
                        lines.append(c)
                
                posx, posy, posz, rotx, roty, rotz = self.getPositionRotation(self.trucks[k])

                if rotx != 0:
                    rotx -= 180
                if roty != 0:
                    roty -= 180
                if rotz != 0:
                    rotz -= 180
                truckstring = k.split(".")[-1] + "\t " + k
                ar = [self.formatFloat(posx), 
                      self.formatFloat(posy), 
                      self.formatFloat(posz), 
                      self.formatFloat(rotx), 
                      self.formatFloat(roty), 
                      self.formatFloat(rotz), 
                      truckstring]
                line = ", ".join(ar)
                lines.append(line.strip()+"\n")
                
            # save meshs                   
            for k in self.meshesorder:

                if k in self.comments.keys():
                    for c in self.comments[k]:
                        lines.append(c)
            
                posx, posy, posz, rotx, roty, rotz = self.getPositionRotation(self.meshes[k])
                meshstring = k.split("_")[-1]
                ar = [self.formatFloat(posx), 
                      self.formatFloat(posy), 
                      self.formatFloat(posz), 
                      self.formatFloat(rotx), 
                      self.formatFloat(roty), 
                      self.formatFloat(rotz), 
                      meshstring]
                line = ", ".join(ar)
                
                if k in self.additionaloptions.keys():
                    for ao in self.additionaloptions[k]:
                        line += " " + ao.strip()

                lines.append(line.strip()+"\n")

            lines.append("end\n")
                
            f=open(fn, 'w')
            f.writelines(lines)
            f.close()
            return True
        #except:
        #    return False
    
    
    def reattachArrows(self, entity):
        self.TranslateNode.setPosition(entity.getParentNode().getPosition())
        self.TranslateNode.setOrientation(entity.getParentNode().getOrientation())
        self.RotateNode.setOrientation(entity.getParentNode().getOrientation())
        self.RotateNode.setPosition(entity.getParentNode().getPosition())
        
    def createArrows(self):
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
        et = self.sceneManager.createEntity("circlepointer", "circlepointer.mesh") 
        et.setMaterialName("mysimple/terrainselect")
        nt.rotate(ogre.Vector3.UNIT_X, ogre.Degree(90).valueRadians(), relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        nt.attachObject(et)
       
        self.TerrainSelectNode = nt
        self.TranslateNode = n
        self.RotateNode = nr
        n.setPosition(self.CameraStartPosition)
        nr.setPosition(self.CameraStartPosition)

    def deselectSelection(self):
        if self.mSelected:
            #self.mSelected.getSubEntity(0).setMaterialName(self.oldmaterial)
            self.mSelected.setMaterialName(self.oldmaterial)   
            self.mSelected.getParentSceneNode().showBoundingBox(False)
    
    
    def changeSelection(self, newnode):
        self.deselectSelection()
        self.mSelected = newnode
        self.oldmaterial = self.mSelected.getSubEntity(0).getMaterialName()
        
        
        newmatname = "mysimple/selectedobject"
        selectedmat = ogre.MaterialManager.getSingleton().getByName(newmatname)
        mat = ogre.MaterialManager.getSingleton().getByName(self.mSelected.getSubEntity(0).getMaterialName())
        if not mat is None:
            mat.copyDetailsTo(selectedmat)
        newmat = ogre.MaterialManager.getSingleton().getByName(newmatname)
        newmat.setSceneBlending(ogre.SceneBlendFactor.SBF_SOURCE_ALPHA, ogre.SceneBlendFactor.SBF_DEST_ALPHA )
        newmat.setSelfIllumination(1, 0.3, 0)
        newmat.setDiffuse(1, 0.3, 0, 0.5)
        newmat.setAmbient(1, 0.3, 0)
        newmat.setSpecular(1, 0.3, 0, 0.5)
        self.selectionMaterial = newmat
        #self.mSelected.getSubEntity(0).setMaterialName(snewmatname)
        self.mSelected.setMaterialName(newmatname)
        self.mSelected.getParentSceneNode().showBoundingBox(True)
        self.reattachArrows(self.mSelected)
        self.arrowScale = self.mSelected.getBoundingRadius() / 100


    def LoadTerrnFile(self, filename):
        self.terrnfile = filename
        f=open(filename, 'r')
        content = f.readlines()
        f.close()
        self.processTerrnFile(content)
        
    def populateScene(self):  
        self.sceneManager.AmbientLight = ogre.ColourValue(0.7, 0.7, 0.7 )

        fadeColour = (0.8, 0.8, 0.8)
        self.sceneManager.setFog(ogre.FOG_LINEAR, fadeColour, 0.001, 5000.0, 10000.0)
        self.renderWindow.getViewport(0).BackgroundColour = fadeColour

        l = self.sceneManager.createLight("MainLight")
        l.setPosition(20,80,50)
        
        

        #create the camera Axes object
        self.camAxesNode = None
        self.camAxesEnt = None
        #create ray template
        self.selectionRaySceneQuery = self.sceneManager.createRayQuery(ogre.Ray());
        self.terrainRaySceneQuery = self.sceneManager.createRayQuery(ogre.Ray());
        # setup the sky plane
        plane = ogre.Plane()
        # 5000 world units from the camera
        plane.d = 5000
        # Above the camera, facing down
        plane.normal = -ogre.Vector3.UNIT_Y
        self.SelectedArrow = None
        self.StartDragLeftX, self.StartDragLeftY = (0,0)
        self.TranslationRotationMode = False
        self.TranslateNode = None
        self.RotateNode = None
        self.stickCurrentObjectToGround = False
        self.randomcounter = 0

    
    def FixTerrainConfig(self,filename):
        print "fixing file %s ..." % filename
        f=open(filename, 'r')
        content = f.readlines()
        f.close()
        for i in range(0, len(content)):
            if content[i].lower().find("maxpixelerror") >= 0:
                content[i] = "MaxPixelError=0\n"
                print "FIXED!"
                break
        f=open(filename, 'w')
        f.writelines(content)
        f.close()        


    def free(self):
        self.sceneManager.clearScene()
    	# self.sceneManager.destroyAllEntities()
    	# self.sceneManager.destroyAllManualObjects()
        # self.sceneManager.destroyAllAnimations()
        # self.sceneManager.destroyAllLights()
        
        # if self.selectionRaySceneQuery:
            # self.sceneManager.destroyQuery(self.selectionRaySceneQuery)
            # self.sceneManager.destroyQuery(self.terrainRaySceneQuery)
        # if self.renderWindow:
            # self.renderWindow.removeAllViewports()
        #ogre.ResourceGroupManager.getSingleton().destroyResourceGroup("General")
        #ogre.ResourceGroupManager.getSingleton().destroyResourceGroup("Bootstrap")
        
        #self.SceneInitialisation()
        
    def LoadTerrain(self, filename):
        # create scene 
        self.free()
        dirname = os.path.dirname(filename)
        self.LoadTerrnFile(filename)
        cfgname = os.path.join(dirname, self.TerrainConfig)
        self.FixTerrainConfig(cfgname)
        self.sceneManager.setWorldGeometry(cfgname)
        self.TerrainLoaded = True
        

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
        if self.mSelected:
            self.mSelected.getParentNode().resetOrientation()
            self.mSelected.getParentNode().rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
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
        self.mSelected = None
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
        for r in result:
            if not r is None and not r.movable is None and r.movable.getMovableType() == "Entity":
                if r.movable.getName() in ["waterent", "circlepointer"]:
                    # you cannot select these objects
                    continue
                if not self.mSelected is None and self.mSelected.getName() == r.movable.getName():
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
        
        forceDegree = ogre.Degree(forcex).valueRadians()
            
        #print self.SelectedArrow.getName(), forcex, forcey
        if self.SelectedArrow.getName() == 'movearrowsX':
            self.TranslateNode.translate(forcex,0,0,relativeTo=ogre.Node.TransformSpace.TS_LOCAL)
            if self.stickCurrentObjectToGround:
                self.TranslateNode.setPosition(self.StickVectorToGround(self.TranslateNode.getPosition()))
            self.RotateNode.setPosition(self.TranslateNode.getPosition())
            if self.mSelected:
                self.mSelected.getParentNode().setPosition(self.TranslateNode.getPosition())
        elif self.SelectedArrow.getName() == 'movearrowsY':
            self.TranslateNode.translate(0,0,forcex,relativeTo=ogre.Node.TransformSpace.TS_LOCAL)
            if self.stickCurrentObjectToGround:
                self.TranslateNode.setPosition(self.StickVectorToGround(self.TranslateNode.getPosition()))
            self.RotateNode.setPosition(self.TranslateNode.getPosition())
            if self.mSelected:
                self.mSelected.getParentNode().setPosition(self.TranslateNode.getPosition())
        elif self.SelectedArrow.getName() == 'movearrowsZ':
            self.TranslateNode.translate(0,forcex,0,relativeTo=ogre.Node.TransformSpace.TS_LOCAL)
            if self.stickCurrentObjectToGround:
                self.TranslateNode.setPosition(self.StickVectorToGround(self.TranslateNode.getPosition()))
            self.RotateNode.setPosition(self.TranslateNode.getPosition())
            if self.mSelected:
                self.mSelected.getParentNode().setPosition(self.TranslateNode.getPosition())
        elif self.SelectedArrow.getName() == 'rotatearrowsX':
            self.RotateNode.yaw(forceDegree)
            if self.mSelected:
                self.mSelected.getParentNode().yaw(forceDegree)
        elif self.SelectedArrow.getName() == 'rotatearrowsY':
            self.RotateNode.pitch(forceDegree)
            if self.mSelected:
                self.mSelected.getParentNode().pitch(forceDegree)
        elif self.SelectedArrow.getName() == 'rotatearrowsZ':
            self.RotateNode.roll(forceDegree)
            if self.mSelected:
                self.mSelected.getParentNode().roll(forceDegree)

    def addMeshToTerrain(self, fn):
        if self.selectedCoords is None:
            return False

        self.randomcounter += 1
        meshname = os.path.basename(fn)
        (firstobjname, fileExtension) = os.path.splitext(meshname)
            
        try:
            (meshname, sx, sy, sz) = self.loadOdef(firstobjname)
        except Exception, inst:
            print inst
            print "########## error loading odef of %s"  % firstobjname
            sx = None
        self.randomcounter +=1
        n = self.sceneManager.getRootSceneNode().createChildSceneNode("object" + str(self.randomcounter)+ firstobjname)
        entname = "objent" + str(self.randomcounter)+"_"+firstobjname
        e = self.sceneManager.createEntity(entname, meshname) 
        n.attachObject(e)

        n.setPosition(self.selectedCoords)
        n.rotate(ogre.Vector3.UNIT_X, ogre.Degree(-90),relativeTo=ogre.Node.TransformSpace.TS_WORLD)
        if not sx is None:
            n.setScale(sx, sy, sz)
        self.meshes[entname] = n
        self.comments[entname] = [ADDEDBY]
        self.meshesorder.append(entname)
        return True

                
    def addTruckToTerrain(self, fn):
        if self.selectedCoords is None:
            return False
        n, entname = self.createTruckMesh(fn)
        n.setPosition(self.selectedCoords)
        return True

    def createTruckMesh(self, fn):
        if not os.path.isfile(fn):
            print "truck file not found: " + fn
            return
        p = rorparser()
        p.parse(fn)
        if not 'nodes' in p.tree.keys() or not 'beams' in p.tree.keys() :
            return False
            
        #try:
        self.randomcounter +=1

        myManualObject =  self.sceneManager.createManualObject("manual"+fn+str(self.randomcounter))

        #myManualObjectMaterial = ogre.MaterialManager.getSingleton().create("manualmaterial"+truckname+str(self.randomcounter),"debugger"); 
        #myManualObjectMaterial.setReceiveShadows(False)
        #myManualObjectMaterial.getTechnique(0).setLightingEnabled(True)
        #myManualObjectMaterial.getTechnique(0).getPass(0).setDiffuse(0,0,1,0)
        #myManualObjectMaterial.getTechnique(0).getPass(0).setAmbient(0,0,1)
        #myManualObjectMaterial.getTechnique(0).getPass(0).setSelfIllumination(0,0,1)
        #myManualObjectMaterial.getTechnique(0).getPass(0).setCullingMode(ogre.CULL_ANTICLOCKWISE)

        matname = ""
        if fn[-4:].lower() == "load":
            matname = 'mysimple/loadcolor'
        elif fn[-5:].lower() == "truck":
            matname = 'mysimple/truckcolor'
        
        myManualObject.useIndexes = True
        myManualObject.estimateVertexCount(2000)
        myManualObject.estimateIndexCount(2000)

        myManualObject.begin(matname+"grid", ogre.RenderOperation.OT_LINE_LIST) 
        for nodeobj in p.tree['nodes']:
            if nodeobj.has_key('type'):
                continue
            node = nodeobj['data']
            myManualObject.position(float(node[1]),float(node[2]),float(node[3]))       
        for beamobj in p.tree['beams']:
            if beamobj.has_key('type'):
                continue
            beam = beamobj['data']
            myManualObject.index(int(beam[0]))
            myManualObject.index(int(beam[1]))
        myManualObject.end()
        myManualObject.begin(matname, ogre.RenderOperation.OT_TRIANGLE_LIST) 
        for nodeobj in p.tree['nodes']:
            if nodeobj.has_key('type'):
                continue
            node = nodeobj['data']
            myManualObject.position(float(node[1]),float(node[2]),float(node[3]))       
        faces = []
        for smobj in p.tree['submeshgroups']:
            for cabobj in smobj['cab']:
                if cabobj.has_key('type'):
                    continue
                cab = cabobj['data']
                #print "########face"
                if cab != []:
                    try:
                        myManualObject.triangle(int(cab[0]),int(cab[1]),int(cab[2]))
                    except:
                        print "error with cab: " + str(cab)
                        pass
        myManualObject.end()
        mesh = myManualObject.convertToMesh("manual"+fn+str(self.randomcounter))
        entity = self.sceneManager.createEntity("manualtruckent"+fn+str(self.randomcounter), 
                                                "manual"+fn+str(self.randomcounter))
        #trucknode = self.sceneManager.getRootSceneNode().createChildSceneNode()
        myManualObjectNode = self.sceneManager.getRootSceneNode().createChildSceneNode("manualnode"+fn+str(self.randomcounter))
        myManualObjectNode.attachObject(entity) 
        
        myManualObjectNode.attachObject(myManualObject)
       
        truckname = os.path.basename(fn)
        self.trucksorder.append(truckname)
        self.trucks[truckname] = myManualObjectNode
        return myManualObjectNode, truckname
        #except:
        #    print "error creating truck: " + truckname
        #    return None

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
                    
    def createnew(self):
        x, y = event.GetPosition() 
        mouseRay = self.camera.getCameraToViewportRay((x / float(width)), (y / float(height)));
        myRaySceneQuery = self.sceneManager.createRayQuery(ogre.Ray());
        myRaySceneQuery.setRay(mouseRay)
        result = myRaySceneQuery.execute()
        if len(result) > 0 and not result[0] is None and not result[0].worldFragment is None:
            self.mCount += 1
            rent = self.sceneManager.createEntity("test%d"%self.mCount, "road.mesh")
            mCurrentObject = self.sceneManager.getRootSceneNode().createChildSceneNode("testnode%d"%self.mCount, result[0].worldFragment.singleIntersection)
            mCurrentObject.attachObject(rent)
            #mCurrentObject.setScale(0.1, 0.1, 0.1)
    
    def onMouseEvent(self,event):
        if not self.TerrainLoaded:
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

        if event.LeftDown() and event.ControlDown() and not self.mSelected is None:
            pos = self.getPointedPosition(event)
            if not pos is None:
                self.TranslateNode.setPosition(pos)
                self.RotateNode.setPosition(pos)
                self.mSelected.getParentNode().setPosition(pos)
            return
        if event.LeftDown():
            self.selectnew(event)
            self.StartDragLeftX, self.StartDragLeftY = event.GetPosition() #saves position of initial click 

        if event.GetWheelRotation() != 0:
            zfactor = 5
            if event.ShiftDown():
                zfactor = 80
            dir = 1
            if event.GetWheelRotation() > 0:
                dir = -1
            self.moveVector = ogre.Vector3(0, 0, dir)
            self.moveForce = zfactor
        event.Skip()


    def onKeyDown(self,event):
        if not self.TerrainLoaded:
            return

        #print event.m_keyCode
        d = 2
        if event.ShiftDown():
            d = 15
        if event.m_keyCode == 65: # A, wx.WXK_LEFT:
            self.moveVector = ogre.Vector3(-1,0,0)
            self.moveForce = d
        elif event.m_keyCode == 68: # D, wx.WXK_RIGHT:
            self.moveVector = ogre.Vector3(1,0,0)
            self.moveForce = d
        elif event.m_keyCode == 87: # W ,wx.WXK_UP:
            self.moveVector = ogre.Vector3(0,0,-1)
            self.moveForce = d
        elif event.m_keyCode == 83: # S, wx.WXK_DOWN:
            self.moveVector = ogre.Vector3(0,0,1)
            self.moveForce = d
        elif event.m_keyCode == wx.WXK_PAGEUP:
            self.moveVector = ogre.Vector3(0,1,0)
            self.moveForce = d
        elif event.m_keyCode == wx.WXK_PAGEDOWN:
            self.moveVector = ogre.Vector3(0,-1,0)
            self.moveForce = d
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