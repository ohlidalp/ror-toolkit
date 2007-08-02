#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx, os, os.path, copy
import ogre.renderer.OGRE as ogre 
from ror.truckparser import *
from ror.terrainparser import *
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from ror.rorcommon import *

def createTruckMesh(sceneManager, fn, uuid):
    if not os.path.isfile(fn):
        #print "truck file not found: " + fn
        log().error("truck file not found: %s" % fn)
        return
    p = rorparser()
    p.parse(fn)
    if not 'nodes' in p.tree.keys() or not 'beams' in p.tree.keys():
        log().error("error while processing truck file %s" % fn)
        return False
        
    try:
        myManualObject =  sceneManager.createManualObject(str(uuid)+"manual")

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
            
        #print len(p.tree['submeshgroups'])
        if len(p.tree['submeshgroups']) > 0:
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
        else:
            print "truck has no faces!"
            
        myManualObject.end()

        try:
            mesh = myManualObject.convertToMesh(str(uuid)+"manual")        
            entity = sceneManager.createEntity(str(uuid)+"entity", str(uuid)+"manual")
            #trucknode = sceneManager.getRootSceneNode().createChildSceneNode()
            myManualObjectNode = sceneManager.getRootSceneNode().createChildSceneNode(str(uuid)+"node")       
            myManualObjectNode.attachObject(myManualObject)
            mesh = myManualObject.convertToMesh(str(uuid)+"manual")
            entity = sceneManager.createEntity(str(uuid)+"entity", str(uuid)+"manual")
            #trucknode = sceneManager.getRootSceneNode().createChildSceneNode()
            myManualObjectNode = sceneManager.getRootSceneNode().createChildSceneNode(str(uuid)+"node")
            myManualObjectNode.attachObject(entity) 
            myManualObjectNode.attachObject(myManualObject)
        except:
            mesh = None
            entity = None
            myManualObjectNode = sceneManager.getRootSceneNode().createChildSceneNode(str(uuid)+"node")
            myManualObjectNode.attachObject(myManualObject)

       
        return myManualObjectNode, entity, mesh
    except Exception, err:
        log().error("error while processing truck file %s" % fn)
        log().error(str(err))
        return None, None, None