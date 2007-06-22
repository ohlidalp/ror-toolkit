#ifndef __FlexMesh_H__
#define __FlexMesh_H__

//wheels only!

#include "Ogre.h"
//#include "Beam.h"

using namespace Ogre;


//class Beam;

class FlexMesh
{
private:
typedef struct
{
	Vector3 vertex;
	Vector3 normal;
//	Vector3 color;
	Vector2 texcoord;
} CoVertice_t;

typedef struct
{
	Vector3 vertex;
} posVertice_t;

typedef struct
{
	Vector3 normal;
//	Vector3 color;
	Vector2 texcoord;
} norVertice_t;

	Ogre::MeshPtr msh;
	SubMesh* subface;
	SubMesh* subband;
	VertexDeclaration* decl;
	HardwareVertexBufferSharedPtr vbuf;

	size_t nVertices;
	size_t vbufCount;
	//shadow
	union
	{
	float *shadowposvertices;
	posVertice_t *coshadowposvertices;
	};
	union
	{
	float *shadownorvertices;
	norVertice_t *coshadownorvertices;
	};
	union
	{
	float *vertices;
	CoVertice_t *covertices;
	};
	//nodes
	int *nodeIDs;

	size_t ibufCount;
	unsigned short *facefaces;
	unsigned short *bandfaces;
	node_t *nodes;
	int nbrays;
	SceneManager *smanager;

public:


	FlexMesh(SceneManager *manager, char* name, node_t *nds, int n1, int n2, int nstart, int nrays, char* texface, char* texband)
    {
        smanager=manager;
		nbrays=nrays;
		nodes=nds;
		/// Create the mesh via the MeshManager
        msh = MeshManager::getSingleton().createManual(name, "General");

        /// Create submeshes
        subface = msh->createSubMesh();
        subband = msh->createSubMesh();

		//materials
		subface->setMaterialName(texface);
		subband->setMaterialName(texband);

        /// Define the vertices (8 vertices, each consisting of 3 groups of 3 floats
        nVertices = 4*nrays+2;
        vbufCount = (2*3+2)*nVertices;
		vertices=(float*)malloc(vbufCount*sizeof(float));
		//shadow
		shadownorvertices=(float*)malloc(nVertices*(3+2)*sizeof(float));
		shadowposvertices=(float*)malloc(nVertices*3*2*sizeof(float));
		nodeIDs=(int*)malloc(nVertices*sizeof(int));

		//define node ids
		nodeIDs[0]=n1;
		nodeIDs[1]=n2;
		int i;
		for (i=0; i<nrays; i++)
		{
			nodeIDs[2+i*2]=nstart+i*2;
			nodeIDs[2+i*2+1]=nstart+i*2+1;
			nodeIDs[2+2*nrays+i*2]=nstart+i*2;
			nodeIDs[2+2*nrays+i*2+1]=nstart+i*2+1;
		}
		//color fix to remove
//		for (i=0; i<(int)nVertices; i++) 
//		{
//			covertices[i].color=Vector3(0.0, 0.0, 0.0);
//		};
		//textures coordinates
		covertices[0].texcoord=Vector2(0.5, 0.5);
		covertices[1].texcoord=Vector2(0.5, 0.5);
		for (i=0; i<nrays; i++)
		{
			//face
			covertices[2+i*2].texcoord=Vector2(0.5+0.5*sin(i*2.0*3.14159/nrays), 0.5+0.5*cos(i*2.0*3.14159/nrays));
			covertices[2+i*2+1].texcoord=covertices[2+i*2].texcoord;
			//band
			covertices[2+2*nrays+(i/2)*4].texcoord=Vector2(0.0, 0.0);
			covertices[2+2*nrays+(i/2)*4+1].texcoord=Vector2(0.0, 1.0);
			covertices[2+2*nrays+(i/2)*4+2].texcoord=Vector2(1.0, 0.0);
			covertices[2+2*nrays+(i/2)*4+3].texcoord=Vector2(1.0, 1.0);
		}

        /// Define triangles
        /// The values in this table refer to vertices in the above table
        ibufCount = 3*2*nrays;
        facefaces=(unsigned short*)malloc(ibufCount*sizeof(unsigned short));
        bandfaces=(unsigned short*)malloc(ibufCount*sizeof(unsigned short));
		for (i=0; i<nrays; i++)
		{
			//wheel sides
			facefaces[3*(i*2)]=0; facefaces[3*(i*2)+1]=2+i*2; facefaces[3*(i*2)+2]=2+((i+1)%nrays)*2;
			facefaces[3*(i*2+1)]=1; facefaces[3*(i*2+1)+2]=2+i*2+1; facefaces[3*(i*2+1)+1]=2+((i+1)%nrays)*2+1;
			//wheel band
			bandfaces[3*(i*2)]=2+2*nrays+i*2; bandfaces[3*(i*2)+1]=2+2*nrays+i*2+1; bandfaces[3*(i*2)+2]=2+2*nrays+((i+1)%nrays)*2+1;
			bandfaces[3*(i*2+1)]=2+2*nrays+((i+1)%nrays)*2+1; bandfaces[3*(i*2+1)+2]=2+2*nrays+i*2; bandfaces[3*(i*2+1)+1]=2+2*nrays+((i+1)%nrays)*2;
		}

		//update coords
		updateVertices();



        /// Create vertex data structure for 8 vertices shared between submeshes
        msh->sharedVertexData = new VertexData();
        msh->sharedVertexData->vertexCount = nVertices;

        /// Create declaration (memory format) of vertex data
        decl = msh->sharedVertexData->vertexDeclaration;
        size_t offset = 0;
        decl->addElement(0, offset, VET_FLOAT3, VES_POSITION);
        offset += VertexElement::getTypeSize(VET_FLOAT3);
        decl->addElement(0, offset, VET_FLOAT3, VES_NORMAL);
        offset += VertexElement::getTypeSize(VET_FLOAT3);
//        decl->addElement(0, offset, VET_FLOAT3, VES_DIFFUSE);
//        offset += VertexElement::getTypeSize(VET_FLOAT3);
        decl->addElement(0, offset, VET_FLOAT2, VES_TEXTURE_COORDINATES, 0);
        offset += VertexElement::getTypeSize(VET_FLOAT2);

        /// Allocate vertex buffer of the requested number of vertices (vertexCount) 
        /// and bytes per vertex (offset)
        vbuf = 
          HardwareBufferManager::getSingleton().createVertexBuffer(
              offset, msh->sharedVertexData->vertexCount, HardwareBuffer::HBU_DYNAMIC_WRITE_ONLY_DISCARDABLE);

        /// Upload the vertex data to the card
        vbuf->writeData(0, vbuf->getSizeInBytes(), vertices, true);

        /// Set vertex buffer binding so buffer 0 is bound to our vertex buffer
        VertexBufferBinding* bind = msh->sharedVertexData->vertexBufferBinding; 
        bind->setBinding(0, vbuf);

        //for the face
		/// Allocate index buffer of the requested number of vertices (ibufCount) 
        HardwareIndexBufferSharedPtr faceibuf = HardwareBufferManager::getSingleton().
         createIndexBuffer(
             HardwareIndexBuffer::IT_16BIT, 
                ibufCount, 
                HardwareBuffer::HBU_STATIC_WRITE_ONLY);

        /// Upload the index data to the card
        faceibuf->writeData(0, faceibuf->getSizeInBytes(), facefaces, true);

        /// Set parameters of the submesh
        subface->useSharedVertices = true;
        subface->indexData->indexBuffer = faceibuf;
        subface->indexData->indexCount = ibufCount;
        subface->indexData->indexStart = 0;

        //for the band
		/// Allocate index buffer of the requested number of vertices (ibufCount) 
        HardwareIndexBufferSharedPtr bandibuf = HardwareBufferManager::getSingleton().
         createIndexBuffer(
             HardwareIndexBuffer::IT_16BIT, 
                ibufCount, 
                HardwareBuffer::HBU_STATIC_WRITE_ONLY);

        /// Upload the index data to the card
        bandibuf->writeData(0, bandibuf->getSizeInBytes(), bandfaces, true);

        /// Set parameters of the submesh
        subband->useSharedVertices = true;
        subband->indexData->indexBuffer = bandibuf;
        subband->indexData->indexCount = ibufCount;
        subband->indexData->indexStart = 0;
        
        /// Set bounding information (for culling)
        msh->_setBounds(AxisAlignedBox(-1,-1,0,1,1,0));
        msh->_setBoundingSphereRadius(Math::Sqrt(1*1+1*1));

        /// Notify Mesh object that it has been loaded
msh->buildEdgeList();
//msh->buildTangentVectors();
/*unsigned short src, dest;
if (!msh->suggestTangentVectorBuildParams(src, dest))
{
    msh->buildTangentVectors(src, dest);
}
*/

msh->load();
//msh->touch(); 
//        msh->load();

		//msh->buildEdgeList();
    }


Vector3 updateVertices()
{
	 int i;
	Vector3 center;
	center=(nodes[nodeIDs[0]].Position+nodes[nodeIDs[1]].Position)/2.0;
	//optimization possible here : just copy bands on face
	covertices[0].vertex=nodes[nodeIDs[0]].Position-center;
		//normals
	covertices[0].normal=nodes[nodeIDs[0]].Position-nodes[nodeIDs[1]].Position;
	covertices[0].normal.normalise();

	covertices[1].vertex=nodes[nodeIDs[1]].Position-center;
		//normals
	covertices[1].normal=-covertices[0].normal;
//	covertices[1].normal.normalise();
	for (i=0; i<nbrays*2; i++)
	{
		covertices[2+i].vertex=nodes[nodeIDs[2+i]].Position-center;
		//normals
		if ((i%2)==0)
		{
			covertices[2+i].normal=nodes[nodeIDs[2+i]].Position-nodes[nodeIDs[2+i+1]].Position;
			covertices[2+i].normal.normalise();
		} else covertices[2+i].normal=-covertices[2+i-1].normal;
		//bands
		covertices[2+2*nbrays+i].vertex=covertices[2+i].vertex;
		covertices[2+2*nbrays+i].normal=covertices[2+i].vertex;
		covertices[2+2*nbrays+i].normal.normalise();
	}
	return center;
}


Vector3 updateShadowVertices()
{
	 int i;
	Vector3 center;
//msh->buildEdgeList();
	center=(nodes[nodeIDs[0]].Position+nodes[nodeIDs[1]].Position)/2.0;

	coshadowposvertices[0].vertex=nodes[nodeIDs[0]].Position-center;
	//normals
	coshadownorvertices[0].normal=nodes[nodeIDs[0]].Position-nodes[nodeIDs[1]].Position;
//	coshadownorvertices[0].normal=nodes[nodeIDs[0]].Position-center;
	coshadownorvertices[0].normal.normalise();

	coshadowposvertices[1].vertex=nodes[nodeIDs[1]].Position-center;
	//normals
	coshadownorvertices[1].normal=-coshadownorvertices[0].normal;
//	coshadownorvertices[1].normal=nodes[nodeIDs[1]].Position-center;
//	coshadownorvertices[1].normal.normalise();

	for (i=0; i<nbrays*2; i++)
	{
		coshadowposvertices[2+i].vertex=nodes[nodeIDs[2+i]].Position-center;

		coshadownorvertices[2+i].normal=nodes[nodeIDs[2+i]].Position-center;
		coshadownorvertices[2+i].normal.normalise();
		//normals
		if ((i%2)==0)
		{
			coshadownorvertices[2+i].normal=nodes[nodeIDs[2+i]].Position-nodes[nodeIDs[2+i+1]].Position;
			coshadownorvertices[2+i].normal.normalise();
		} else 
		{
			coshadownorvertices[2+i].normal=-coshadownorvertices[2+i-1].normal;
		}
		//bands
		coshadowposvertices[2+2*nbrays+i].vertex=coshadowposvertices[2+i].vertex;
		if ((i%2)==0)
		{
			coshadownorvertices[2+2*nbrays+i].normal=nodes[nodeIDs[2+i]].Position-nodes[nodeIDs[0]].Position;
		} else
		{
			coshadownorvertices[2+2*nbrays+i].normal=nodes[nodeIDs[2+i]].Position-nodes[nodeIDs[1]].Position;
		};
//		coshadownorvertices[2+2*nbrays+i].normal=coshadowposvertices[2+i].vertex;
		coshadownorvertices[2+2*nbrays+i].normal.normalise();

	}

	for (i=0; i<2+nbrays*4; i++)
	{
		coshadowposvertices[i+2+nbrays*4].vertex=coshadowposvertices[i].vertex;
		coshadownorvertices[i].texcoord=covertices[i].texcoord;
	}
//msh->touch();
	return center;
}

/*
Vector3 updateShadowVertices()
{
	 int i;
	Vector3 center;
	center=(nodes[nodeIDs[0]].Position+nodes[nodeIDs[1]].Position)/2.0;

	coshadowposvertices[0].vertex=nodes[nodeIDs[0]].Position-center;
		//normals
	coshadownorvertices[0].normal=coshadowposvertices[0].vertex;
	coshadownorvertices[0].normal.normalise();

	coshadowposvertices[1].vertex=nodes[nodeIDs[1]].Position-center;
		//normals
	coshadownorvertices[1].normal=coshadowposvertices[1].vertex;
	coshadownorvertices[1].normal.normalise();
	//texcoords
	coshadownorvertices[0].texcoord=covertices[0].texcoord;
	coshadownorvertices[1].texcoord=covertices[1].texcoord;
	for (i=0; i<nbrays*2; i++)
	{
		coshadowposvertices[2+i].vertex=nodes[nodeIDs[2+i]].Position-center;
		//normals
		coshadownorvertices[2+i].normal=coshadowposvertices[2+i].vertex;
		coshadownorvertices[2+i].normal.normalise();
		//optimization
		coshadowposvertices[2+2*nbrays+i].vertex=coshadowposvertices[2+i].vertex;
		coshadownorvertices[2+2*nbrays+i].normal=coshadownorvertices[2+i].normal;

		//texcoords
		coshadownorvertices[2+i].texcoord=covertices[2+i].texcoord;
		coshadownorvertices[2+2*nbrays+i].texcoord=covertices[2+2*nbrays+i].texcoord;
	}
	return center;
}
*/

Vector3 flexit()
{
	Vector3 center;
	if (smanager->getShadowTechnique()==SHADOWTYPE_STENCIL_MODULATIVE || smanager->getShadowTechnique()==SHADOWTYPE_STENCIL_ADDITIVE)
	{
		center=updateShadowVertices();
		//find the binding
		unsigned posbinding=msh->sharedVertexData->vertexDeclaration->findElementBySemantic(VES_POSITION)->getSource();
		HardwareVertexBufferSharedPtr pbuf=msh->sharedVertexData->vertexBufferBinding->getBuffer(posbinding);
		pbuf->lock(HardwareBuffer::HBL_DISCARD);
		pbuf->writeData(0, pbuf->getSizeInBytes(), shadowposvertices, true);
		pbuf->unlock();
		//find the binding
		unsigned norbinding=msh->sharedVertexData->vertexDeclaration->findElementBySemantic(VES_NORMAL)->getSource();
		HardwareVertexBufferSharedPtr nbuf=msh->sharedVertexData->vertexBufferBinding->getBuffer(norbinding);
		nbuf->lock(HardwareBuffer::HBL_DISCARD);
		nbuf->writeData(0, nbuf->getSizeInBytes(), shadownorvertices, true);
		nbuf->unlock();

		EdgeData * 	ed=msh->getEdgeList();
		ed->updateFaceNormals(0, pbuf);
	}
		else
	{
		center=updateVertices();
		vbuf->lock(HardwareBuffer::HBL_DISCARD);
		vbuf->writeData(0, vbuf->getSizeInBytes(), vertices, true);
		vbuf->unlock();
		//msh->sharedVertexData->vertexBufferBinding->getBuffer(0)->writeData(0, vbuf->getSizeInBytes(), vertices, true);
	}
	return center;
}


};



#endif
