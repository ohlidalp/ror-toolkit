#Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
import wx, os, os.path, copy
import ogre.renderer.OGRE as ogre 
from ror.truckparser import *
from ror.terrainparser import *
from wxogre.OgreManager import *
from wxogre.wxOgreWindow import *
from ror.rorcommon import *

def createTruckMesh(sceneManager, fn, uuid):
    #if not os.path.isfile(fn):
    #    #print "truck file not found: " + fn
    #    log().error("truck file not found: %s" % fn)
    #    return
    p = rorparser()
    p.parse(fn)
    if not 'nodes' in p.tree.keys() or not 'beams' in p.tree.keys():
        log().error("error while processing truck file %s" % fn)
        return None, None, None
        
    try:
    
        myManualObject =  sceneManager.createManualObject(str(uuid)+"manual")

        #myManualObjectMaterial = ogre.MaterialManager.getSingleton().create("manualmaterial"+truckname+str(self.randomcounter),"debugger"); 
        #myManualObjectMaterial.setReceiveShadows(False)
        #myManualObjectMaterial.getTechnique(0).setLightingEnabled(True)
        #myManualObjectMaterial.getTechnique(0).getPass(0).setDiffuse(0,0,1,0)
        #myManualObjectMaterial.getTechnique(0).getPass(0).setAmbient(0,0,1)
        #myManualObjectMaterial.getTechnique(0).getPass(0).setSelfIllumination(0,0,1)
        #myManualObjectMaterial.getTechnique(0).getPass(0).setCullingMode(ogre.CULL_ANTICLOCKWISE)

        matname = "mysimple/water"

        myManualObject.useIndexes = True
        myManualObject.estimateVertexCount(2000)
        myManualObject.estimateIndexCount(2000)

        minPos = ogre.Vector3(999,999,999)
        maxPos = ogre.Vector3(-999,-999,-999)
        matname = p.tree['globals'][0]['data'][2]

        if len(p.tree['submeshgroups']) > 0:
            nodecounter = 0
            nodes = {}
            myManualObject.begin(matname, ogre.RenderOperation.OT_TRIANGLE_LIST) 
            for nodeobj in p.tree['nodes']:
                if nodeobj.has_key('type'):
                    continue
                node = nodeobj['data']
                nodes[nodecounter] = [float(node[1]),float(node[2]),float(node[3])]
                nodecounter +=1
                
                # get min/max positions
                if float(node[0]) < minPos.x: minPos.x = float(node[0])
                if float(node[1]) < minPos.y: minPos.y = float(node[1])
                if float(node[2]) < minPos.z: minPos.z = float(node[2])
                if float(node[0]) > maxPos.x: maxPos.x = float(node[0])
                if float(node[1]) > maxPos.y: maxPos.y = float(node[1])
                if float(node[2]) > maxPos.z: maxPos.z = float(node[2])
                
            nodecounter = 0
            #print len(p.tree['submeshgroups'])
            counter = 0
            if len(p.tree['submeshgroups']) > 0:
                faces = []
                for smobj in p.tree['submeshgroups']:
                    uv = {}
                    for data in smobj['texcoords']:
                        tex = data['data']
                        uv[int(tex[0])] = [float(tex[1]), float(tex[2])]
                    
                    for cabobj in smobj['cab']:
                        if cabobj.has_key('type'):
                            continue
                        cab = cabobj['data']
                        #print "########face"
                        if cab != []:
                            try:
                                myManualObject.position(nodes[int(cab[2])])
                                myManualObject.index(nodecounter)
                                nodecounter += 1                               
                                myManualObject.textureCoord(uv[int(cab[2])][0], uv[int(cab[2])][1])
                                
                                myManualObject.position(nodes[int(cab[1])])
                                myManualObject.index(nodecounter)
                                nodecounter += 1

                                myManualObject.textureCoord(uv[int(cab[1])][0], uv[int(cab[1])][1])

                                myManualObject.position(nodes[int(cab[0])])
                                myManualObject.index(nodecounter)
                                nodecounter += 1

                                myManualObject.textureCoord(uv[int(cab[0])][0], uv[int(cab[0])][1])

                            except:
                                print "error with cab: " + str(cab)
                                pass
            else:
                print "truck has no faces!"
                
            myManualObject.end()
            myManualObject.setCastShadows(False)
            mat = ogre.MaterialManager.getSingleton().getByName(matname)
            if not mat is None:
                mat.setCullingMode(ogre.CullingMode.CULL_NONE)
            # create the mesh now
            mesh = myManualObject.convertToMesh(str(uuid)+"manual")
        
        # add the lines!
        myManualObject.begin(matname, ogre.RenderOperation.OT_LINE_LIST) 
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
        
        entity = sceneManager.createEntity(str(uuid)+"entity", str(uuid)+"manual")
        
        myManualObjectNode = sceneManager.getRootSceneNode().createChildSceneNode(str(uuid)+"node")
        newpos = (minPos+maxPos)/2
        #print "min:", minPos, "max:", maxPos, "newpos:", newpos
        myManualObjectNode.setPosition(-newpos)
        myManualObjectNode.attachObject(entity) 
        myManualObjectNode.attachObject(myManualObject)

       
        return myManualObjectNode, entity, mesh
    except Exception, err:
        log().error("error while processing truck file %s" % fn)
        log().error(str(err))
        raise 
