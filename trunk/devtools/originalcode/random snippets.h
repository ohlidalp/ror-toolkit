#define MAX_NODES 1000
#define MAX_BEAMS 4000
#define MAX_CONTACTERS 200
#define MAX_HYDROS 40
#define MAX_WHEELS 16
#define MAX_SUBMESHES 500
#define MAX_TEXCOORDS 2000
#define MAX_CABS 2000
#define MAX_SHOCKS 20
#define MAX_ROPES 10
#define MAX_ROPABLES 20
#define MAX_TIES 10
#define MAX_FLARES 20
#define MAX_PROPS 40

#define MAX_CAMERAS 10

#define MAX_TURBOPROPS 8

#define MAX_SCREWPROPS 8

#define DEFAULT_SPRING 9000000.0
//should be 60000
#define DEFAULT_DAMP 12000.0
//#define DEFAULT_DAMP 60000.0
//mars
//#define DEFAULT_GRAVITY -3.8
//earth
#define DEFAULT_GRAVITY -9.8
#define DEFAULT_DRAG 0.05
#define DEFAULT_BEAM_DIAMETER 0.05
#define MAX_SPEED 140.0

#define DEFAULT_WATERDRAG 10.0
//buoyancy force per node in Newton
//#define DEFAULT_BUOYANCY 700.0


#define IRON_DENSITY 7874.0
#define BEAM_BREAK 1000000.0
#define BEAM_DEFORM 400000.0
#define BEAM_CREAK  100000.0
#define WHEEL_FRICTION_COEF 2.0
#define CHASSIS_FRICTION_COEF 0.05
#define SPEED_STOP 0.2

#define STAB_RATE 0.1

#define BEAM_NORMAL 0
#define BEAM_HYDRO 1
#define BEAM_VIRTUAL 2
#define BEAM_MARKED 3
#define BEAM_INVISIBLE 4
#define BEAM_INVISIBLE_HYDRO 5

#define NODE_NORMAL 0
#define NODE_LOADED 1

//leading truck
#define ACTIVATED 0
//not leading but active
#define DESACTIVATED 1
//static
#define SLEEPING 2
//network
#define NETWORKED 3

#define MAX_TRUCKS 64

#define MAX_WINGS 20

#define UNLOCKED 0
#define PRELOCK 1
#define LOCKED 2

#define NOT_DRIVEABLE 0
#define TRUCK 1
#define AIRPLANE 2
#define BOAT 3

#define DRY 0
#define DRIPPING 1
#define WET 2


typedef struct _node
{
	Real mass;
	Vector3 iPosition;
	Vector3 Position;
	Vector3 Velocity;
	Vector3 Forces;
	int locked;
	int iswheel;
	int masstype;
	int contactless;
	int contacted;
	Real friction;
	Real buoyancy;
	Vector3 lastdrag;
	Vector3 gravimass;
	int lockednode;
	Vector3 lockedPosition;
	Vector3 lockedVelocity;
	Vector3 lockedForces;
	int wetstate;
	float wettime;
	bool isHot;
	Vector3 buoyanceForce;
} node_t;

typedef struct _beam
{
	node_t *p1;
	node_t *p2;
	Real k; //tensile spring
	Real d; //damping factor
	Real L; //length
	Real refL; //reference length
	Real Lhydro;//hydro reference len
	Real hydroRatio;//hydro rotation ratio
	bool hydroSpeed;
	SceneNode *mSceneNode; //visual
	Entity *mEntity; //visual
	int type;
	int broken;
	int bounded;
	Real shortbound;
	Real longbound;
	Real commandRatio;
	Real commandShort;
	Real commandLong;
	Real stress;
	Real maxposstress;
	Real maxnegstress;
	Real strength;
	Vector3 lastforce;
	bool isrope;
	int disabled;
	float minendmass;
} beam_t;

typedef struct _wheel
{
	int nbnodes;
	node_t* nodes[50];
	int braked;
	int propulsed;
	node_t* arm;
	node_t* near_attach;
	node_t* refnode0;
	node_t* refnode1;
	Real radius;
	Real speed;
} wheel_t;



	void calc_masses2(Real total)
	{
		int i;
		Real len=0.0;
		//reset
		for (i=0; i<free_node; i++)
		{
			if (!nodes[i].iswheel) 
			{
				if (!nodes[i].masstype==NODE_LOADED) nodes[i].mass=0;
				else nodes[i].mass=loadmass/(float)masscount;
			}
		}
		//average linear density
		for (i=0; i<free_beam; i++)
		{
			if (beams[i].type!=BEAM_VIRTUAL)
			{
				Real newlen=beams[i].L;
				if (!(beams[i].p1->iswheel)) len+=newlen/2.0;
				if (!(beams[i].p2->iswheel)) len+=newlen/2.0;
			};
		}
		for (i=0; i<free_beam; i++)
		{
			if (beams[i].type!=BEAM_VIRTUAL)
			{
				Real mass=beams[i].L*total/len;
				if (!(beams[i].p1->iswheel)) beams[i].p1->mass+=mass/2;
				if (!(beams[i].p2->iswheel)) beams[i].p2->mass+=mass/2;
			};
		}
		//fix rope masses
		for (i=0; i<free_rope; i++)
		{
			ropes[i].beam->p2->mass=100.0;
		}
		//fix camera mass
		for (i=0; i<freecinecamera; i++) nodes[cinecameranodepos[i]].mass=20;

		//hooks must be heavy
		if (hookId!=-1) nodes[hookId].mass=500.0;

		//update gravimass
		for (i=0; i<free_node; i++) 
		{
			//LogManager::getSingleton().logMessage("Nodemass "+StringConverter::toString(i)+"-"+StringConverter::toString(nodes[i].mass));
			//for stability
			if (!nodes[i].iswheel && nodes[i].mass<50.0) nodes[i].mass=50.0;
			nodes[i].gravimass=Vector3(0,DEFAULT_GRAVITY*nodes[i].mass,0);
		}
		//update minendmass
		for (i=0; i<free_beam; i++)
		{
			beams[i].minendmass=beams[i].p1->mass;
			if (beams[i].p2->mass<beams[i].minendmass) beams[i].minendmass=beams[i].p2->mass;
		}
	}

	//to load a truck file
	void loadTruck(char* fname, SceneManager *manager, SceneNode *parent, Real px, Real py, Real pz, Real ry, bool postload)
	{
		//FILE *fd;
		char line[1024];
		int mode=0;
		int hasfixes=0;
		int wingstart=-1;
		float wingarea=0.0;
		//convert ry
		ry=ry*3.14159/180.0;
		LogManager::getSingleton().logMessage("BEAM: Start of truck loading");
		ResourceGroupManager& rgm = ResourceGroupManager::getSingleton();
		DataStreamPtr ds=rgm.openResource(fname, "General");


//		fd=fopen(fname, "r");
//		if (!fd) {
//			LogManager::getSingleton().logMessage("Can't open truck file '"+String(fname)+"'");
//			exit(1);
//		};
		LogManager::getSingleton().logMessage("Parsing '"+String(fname)+"'");
		//skip first line
//		fscanf(fd," %[^\n\r]",line);
		ds->readLine(line, 1023);

//		while (!feof(fd))
		while (!ds->eof())
		{
			size_t ll=ds->readLine(line, 1023);
//			fscanf(fd," %[^\n\r]",line);
			//LogManager::getSingleton().logMessage(line);
			//        printf("Mode %i Line:'%s'\n",mode, line); 
			if (line[0]==';' || ll==0)
			{
				//    printf("%s\n", line+1);
				continue;
			};
			if (!strcmp("end",line)) 
			{
				LogManager::getSingleton().logMessage("BEAM: End of truck loading");
				loading_finished=1;break;
			};
			if (!strcmp("nodes",line)) {mode=1;continue;};
			if (!strcmp("beams",line)) {mode=2;continue;};
			if (!strcmp("fixes",line)) {mode=3;continue;};
			if (!strcmp("shocks",line)) {mode=4;continue;};
			if (!strcmp("hydros",line)) {mode=5;continue;};
			if (!strcmp("wheels",line)) {mode=6;continue;};
			if (!strcmp("globals",line)) {mode=7;continue;};
			if (!strcmp("cameras",line)) {mode=8;continue;};
			if (!strcmp("engine",line)) {mode=9;continue;};
			if (!strcmp("texcoords",line)) {mode=10;continue;};
			if (!strcmp("cab",line)) {mode=11;continue;};
			if (!strcmp("commands",line)) {mode=12;continue;};
			if (!strcmp("forwardcommands",line)) {forwardcommands=1;continue;};
			if (!strcmp("importcommands",line)) {importcommands=1;continue;};
			if (!strcmp("rollon",line)) {wheel_contact_requested=true;continue;};
			if (!strcmp("rescuer",line)) {rescuer=true;continue;};
			if (!strcmp("contacters",line)) {mode=13;continue;};
			if (!strcmp("ropes",line)) {mode=14;continue;};
			if (!strcmp("ropables",line)) {mode=15;continue;};
			if (!strcmp("ties",line)) {mode=16;continue;};
			if (!strcmp("help",line)) {mode=17;continue;};
			if (!strcmp("cinecam",line)) {mode=18;continue;};
			if (!strcmp("flares",line)) {mode=19;continue;};
			if (!strcmp("props",line)) {mode=20;continue;};
			if (!strcmp("globeams",line)) {mode=21;continue;};
			if (!strcmp("wings",line)) {mode=22;continue;};
			if (!strcmp("turboprops",line)) {mode=23;continue;};
			if (!strcmp("fusedrag",line)) {mode=24;continue;};
			if (!strcmp("engoption",line)) {mode=25;continue;};
			if (!strcmp("brakes",line)) {mode=26;continue;};
			if (!strcmp("rotators",line)) {mode=27;continue;};
			if (!strcmp("screwprops",line)) {mode=28;continue;};
			if (!strncmp("set_beam_defaults", line, 17))
			{
				sscanf(line,"set_beam_defaults %f, %f, %f, %f, %f, %s", &default_spring, &default_damp, &default_deform,&default_break,&default_beam_diameter, default_beam_material);
				if (default_spring<0) default_spring=DEFAULT_SPRING;
				if (default_damp<0) default_damp=DEFAULT_DAMP;
				if (default_deform<0) default_deform=BEAM_DEFORM;
				if (default_break<0) default_break=BEAM_BREAK;
				if (default_beam_diameter<0) default_beam_diameter=DEFAULT_BEAM_DIAMETER;
				continue;
			}
			if (!strcmp("backmesh",line)) 
			{
				//close the current mesh
				subtexcoords[free_sub]=free_texcoord;
				subcabs[free_sub]=free_cab;
				//make it normal
				subisback[free_sub]=0;
				free_sub++;

				//add an extra front mesh
				int i;
				int start;
				//texcoords
				if (free_sub==1) start=0; else start=subtexcoords[free_sub-2];
				for (i=start; i<subtexcoords[free_sub-1]; i++)
				{
					texcoords[free_texcoord]=texcoords[i];;
					free_texcoord++;
				}
				//cab
				if (free_sub==1) start=0; else start=subcabs[free_sub-2];
				for (i=start; i<subcabs[free_sub-1]; i++)
				{
					cabs[free_cab*3]=cabs[i*3];
					cabs[free_cab*3+1]=cabs[i*3+1];
					cabs[free_cab*3+2]=cabs[i*3+2];
					free_cab++;
				}
				//finish it, this is a window
				subisback[free_sub]=2;
				//close the current mesh
				subtexcoords[free_sub]=free_texcoord;
				subcabs[free_sub]=free_cab;
				//make is transparent
				free_sub++;


				//add an extra back mesh
				//texcoords
				if (free_sub==1) start=0; else start=subtexcoords[free_sub-2];
				for (i=start; i<subtexcoords[free_sub-1]; i++)
				{
					texcoords[free_texcoord]=texcoords[i];;
					free_texcoord++;
				}
				//cab
				if (free_sub==1) start=0; else start=subcabs[free_sub-2];
				for (i=start; i<subcabs[free_sub-1]; i++)
				{
					cabs[free_cab*3]=cabs[i*3+1];
					cabs[free_cab*3+1]=cabs[i*3];
					cabs[free_cab*3+2]=cabs[i*3+2];
					free_cab++;
				}
				//we don't finish, there will be a submesh statement later
				subisback[free_sub]=1;
				continue;
			};
			if (!strcmp("submesh",line)) 
			{
				subtexcoords[free_sub]=free_texcoord;
				subcabs[free_sub]=free_cab;
				free_sub++;
				//initialize the next
				subisback[free_sub]=0;
				continue;
			};
			if (mode==1)
			{
				//parse nodes
				int id;
				float x,y,z;
				char load='n';
				int type=NODE_NORMAL;
				sscanf(line,"%i, %f, %f, %f, %c",&id,&x,&y,&z,&load);
				if (load=='l') type=NODE_LOADED;
				//            printf("node %i : %f %f %f\n", id, x,y,z);
				if (id!=free_node)
				{
					LogManager::getSingleton().logMessage("Error: lost sync in nodes numbers after node "
						+StringConverter::toString(free_node)+"(got "+StringConverter::toString(id)+"instead)");
					exit(2);
				};
				init_node(id, px+x*cos(ry)+z*sin(ry), py+y , pz+x*cos(ry+3.14159/2.0)+z*sin(ry+3.14159/2.0),type);
				//friction
				if (load=='f') nodes[id].friction=100.0;
				//exhaust
				if (load=='x' && !disable_smoke)
				{
					smokeId=id;
					smokeNode = parent->createChildSceneNode();
					//ParticleSystemManager *pSysM=ParticleSystemManager::getSingletonPtr();
					char wname[256];
					sprintf(wname, "exhaust-%s",truckname);
					//if (pSysM) smoker=pSysM->createSystem(wname, "tracks/Smoke");
					smoker=manager->createParticleSystem(wname, "tracks/Smoke");
					//				ParticleSystem* pSys = ParticleSystemManager::getSingleton().createSystem("exhaust", "tracks/Smoke");
					if (smoker) 
					{
						smokeNode->attachObject(smoker);
						smokeNode->setPosition(nodes[smokeId].Position);
					}
					nodes[id].isHot=true;
				}
				//exhaust reference
				if (load=='y' && !disable_smoke) 
				{
					smokeRef=id;
					nodes[id].isHot=true;
				}
				//contactless
				if (load=='c') nodes[id].contactless=1;
				//hook
				if (load=='h') hookId=id;
				//editor
				if (load=='e') editorId=id;
				//buoy
				if (load=='b') nodes[id].buoyancy=10000.0;
				free_node++; 
			}
			if (mode==2)
			{
				//parse beams
				int id1, id2;
				char visible='v';
				int type=BEAM_NORMAL;
				sscanf(line,"%i, %i, %c",&id1,&id2,&visible);
				if (visible=='i') type=BEAM_INVISIBLE;
				if (id1>=free_node || id2>=free_node)
				{
					LogManager::getSingleton().logMessage("Error: unknown node number in beams section ("
						+StringConverter::toString(id1)+","+StringConverter::toString(id2)+")");
					exit(3);
				};
				//skip if a beam already exists
				int i;
				for (i=0; i<free_beam; i++)
				{
					if ((beams[i].p1==&nodes[id1] && beams[i].p2==&nodes[id2]) || (beams[i].p1==&nodes[id2] && beams[i].p2==&nodes[id1]))
					{
						LogManager::getSingleton().logMessage("Skipping duplicate beam");
						continue;
					}
				}
				//            printf("beam : %i %i\n", id1, id2);
				/*
				if (visible=='r')
				{
				//this is a rope, add extra nodes
				int numropeseg=5;
				int i;
				int lastid=id1;
				int lastlastid=-1;
				for (i=0; i<numropeseg-1; i++)
				{
				//insert a node
				Vector3 nodep=nodes[id1].Position+(float)(i+1)*(nodes[id2].Position-nodes[id1].Position)/(float)numropeseg;
				init_node(free_node, nodep.x, nodep.y, nodep.z,NODE_NORMAL);
				init_beam(free_beam , &nodes[lastid], &nodes[free_node], manager, parent, type, BEAM_BREAK);
				//beams[free_beam].isrope=true;
				beams[free_beam].k/=100.0;
				beams[free_beam].d/=100.0;
				free_beam++;
				//if (lastlastid!=-1)
				//{
				//extra reinforcement beams
				//	init_beam(free_beam , &nodes[lastlastid], &nodes[free_node], manager, parent, BEAM_INVISIBLE, BEAM_BREAK);
				//beams[free_beam].isrope=true;
				//	beams[free_beam].k/=100.0;
				//	beams[free_beam].d/=100.0;
				//   free_beam++;
				//}
				lastlastid=lastid;
				lastid=free_node;
				free_node++;
				}
				//last segment
				init_beam(free_beam , &nodes[lastid], &nodes[id2], manager, parent, type, BEAM_BREAK);
				//beams[free_beam].isrope=true;
				beams[free_beam].k/=100.0;
				beams[free_beam].d/=100.0;
				free_beam++;
				//init_beam(free_beam , &nodes[lastlastid], &nodes[id2], manager, parent, BEAM_INVISIBLE, BEAM_BREAK);
				//beams[free_beam].isrope=true;
				//beams[free_beam].k/=100.0;
				//beams[free_beam].d/=100.0;
				//free_beam++;
				}
				else
				{
				init_beam(free_beam , &nodes[id1], &nodes[id2], manager, parent, type, BEAM_BREAK);
				free_beam++;
				}
				*/
				init_beam(free_beam , &nodes[id1], &nodes[id2], manager, parent, type, default_break, default_spring, default_damp);
				beams[free_beam].isrope=(visible=='r');
				free_beam++;
			}
			if (mode==4)
			{
				//parse shocks
				int id1, id2;
				float s, d, sbound,lbound,precomp;
				char type='n';
				sscanf(line,"%i, %i, %f, %f, %f, %f, %f, %c",&id1,&id2, &s, &d, &sbound, &lbound,&precomp,&type);
				if (id1>=free_node || id2>=free_node)
				{
					LogManager::getSingleton().logMessage("Error: unknown node number in shocks section ("
						+StringConverter::toString(id1)+","+StringConverter::toString(id2)+")");
					exit(4);
				};
				//            printf("beam : %i %i\n", id1, id2);
				//bounded beam
				int htype=BEAM_HYDRO;
				if (type=='i') htype=BEAM_INVISIBLE_HYDRO;

				init_beam(free_beam , &nodes[id1], &nodes[id2], manager, parent, htype, default_break*4.0, s, d, -1.0, sbound, lbound,precomp);
				if (type!='n' && type!='i')
				{
					active_shocks[free_active_shock]=free_beam;
					free_active_shock++;
				};
				free_beam++;
			}
			if (mode==3)
			{
				//parse fixes
				int id;
				sscanf(line,"%i",&id);
				if (id>=free_node)
				{
					LogManager::getSingleton().logMessage("Error: unknown node number in fixes section ("
						+StringConverter::toString(id)+")");
					exit(5);
				};
				nodes[id].locked=1;
				hasfixes=1;
			}
			if (mode==5)
			{
				//parse hydros
				int id1, id2;
				float ratio;
				char option='n';
				sscanf(line,"%i, %i, %f, %c",&id1,&id2,&ratio, &option);
				int htype=BEAM_HYDRO;
				if (option=='i') htype=BEAM_INVISIBLE_HYDRO;
				if (id1>=free_node || id2>=free_node)
				{
					LogManager::getSingleton().logMessage("Error: unknown node number in hydros section ("
						+StringConverter::toString(id1)+","+StringConverter::toString(id2)+")");
					exit(6);
				};
				//            printf("beam : %i %i\n", id1, id2);
				init_beam(free_beam , &nodes[id1], &nodes[id2], manager, parent, htype, default_break, default_spring, default_damp);
				hydro[free_hydro]=free_beam;free_hydro++;
				beams[free_beam].Lhydro=beams[free_beam].L;
				beams[free_beam].hydroRatio=ratio;
				beams[free_beam].hydroSpeed=(option=='s');
				free_beam++;
			}
			if (mode==6)
			{
				//parse wheels
				float radius, width, mass, spring, damp;
				int rays, node1, node2, snode, braked, propulsed, torquenode;
				sscanf(line,"%f, %f, %i, %i, %i, %i, %i, %i, %i, %f, %f, %f, %s %s",&radius,&width,&rays,&node1,&node2,&snode,&braked,&propulsed,&torquenode,&mass,&spring,&damp, texf, texb);
				addWheel(manager, parent, radius,width,rays,node1,node2,snode,braked,propulsed, torquenode, mass, spring, damp, texf, texb);
			}
			if (mode==7)
			{
				//parse globals
				sscanf(line,"%f, %f, %s",&truckmass, &loadmass, texname);
				//
				LogManager::getSingleton().logMessage("BEAM: line: '"+String(line)+"'");
				LogManager::getSingleton().logMessage("BEAM: texname: '"+String(texname)+"'");

				//we clone the material
				char clonetex[256];
				sprintf(clonetex, "%s-%s",texname,truckname);
				MaterialPtr mat=(MaterialPtr)(MaterialManager::getSingleton().getByName(texname));
				mat->clone(clonetex);
				strcpy(texname, clonetex);
			}
			if (mode==8)
			{
				//parse cameras
				int nodepos, nodedir, dir;
				sscanf(line,"%i, %i, %i",&nodepos,&nodedir,&dir);
				addCamera(nodepos, nodedir, dir);
			}
			if (mode==9)
			{
				//parse engine
				float minrpm, maxrpm, torque, dratio, rear;
				float gears[16];
				int numgears;
				driveable=TRUCK;
				sscanf(line,"%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f", &minrpm, &maxrpm, &torque, &dratio, &rear, &gears[0],&gears[1],&gears[2],&gears[3],&gears[4],&gears[5],&gears[6],&gears[7],&gears[8],&gears[9],&gears[10],&gears[11],&gears[12],&gears[13],&gears[14],&gears[15]);
				for (numgears=0; numgears<16; numgears++) if (gears[numgears]==-1.0) break;
				if (audio) audio->setupEngine();
				engine=new BeamEngine(minrpm, maxrpm, torque, rear, numgears, gears, dratio, audio);
				//engine->start();
			}

			if (mode==10)
			{
				//parse texcoords
				int id;
				float x, y;
				sscanf(line,"%i, %f, %f", &id, &x, &y);
				texcoords[free_texcoord]=Vector3(id, x, y);
				free_texcoord++;
			}

			if (mode==11)
			{
				//parse cab
				char type='n';
				int id1, id2, id3;
				sscanf(line,"%i, %i, %i, %c", &id1, &id2, &id3,&type);
				cabs[free_cab*3]=id1;
				cabs[free_cab*3+1]=id2;
				cabs[free_cab*3+2]=id3;
				if (type=='c') {collcabs[free_collcab]=free_cab; free_collcab++;};
				if (type=='b') {buoycabs[free_buoycab]=free_cab; free_buoycab++; if (!buoyance) buoyance=new Buoyance(water, splashp, ripplep);};
				if (type=='D')
				{
					collcabs[free_collcab]=free_cab; free_collcab++;
					buoycabs[free_buoycab]=free_cab; free_buoycab++; if (!buoyance) buoyance=new Buoyance(water, splashp, ripplep);
				}
				free_cab++;
			}

			if (mode==12)
			{
				//parse commands
				int id1, id2,keys,keyl;
				float rate, shortl, longl;
				char option='n';
				hascommands=1;
				sscanf(line,"%i, %i, %f, %f, %f, %i, %i, %c", &id1, &id2, &rate, &shortl, &longl, &keys, &keyl,&option);
				int htype=BEAM_HYDRO;
				if (option=='i') htype=BEAM_INVISIBLE_HYDRO;
				init_beam(free_beam , &nodes[id1], &nodes[id2], manager, parent, htype, default_break, default_spring, default_damp);
				if (option=='r') beams[free_beam].isrope=true;
				beams[free_beam].Lhydro=beams[free_beam].L;
				//add short key
				commandkey[keys].beams[commandkey[keys].bfree]=-free_beam;
				commandkey[keys].bfree++;
				//add long key
				commandkey[keyl].beams[commandkey[keyl].bfree]=free_beam;
				commandkey[keyl].bfree++;
				beams[free_beam].commandRatio=rate;
				beams[free_beam].commandShort=shortl;
				beams[free_beam].commandLong=longl;
				free_beam++;

			}

			if (mode==13)
			{
				//parse contacters
				int id1;
				sscanf(line,"%i", &id1);
				contacters[free_contacter].nodeid=id1;
				contacters[free_contacter].contacted=0;
				contacters[free_contacter].opticontact=0;
				free_contacter++;;
			}
			if (mode==14)
			{
				//parse ropes
				int id1, id2;
				sscanf(line,"%i, %i", &id1, &id2);
				//add beam
				if (id1>=free_node || id2>=free_node)
				{
					LogManager::getSingleton().logMessage("Error: unknown node number in ropes section ("
						+StringConverter::toString(id1)+","+StringConverter::toString(id2)+")");
					exit(7);
				};
				init_beam(free_beam , &nodes[id1], &nodes[id2], manager, parent, BEAM_NORMAL, default_break, default_spring, default_damp);
				beams[free_beam].isrope=1;
				//register rope
				ropes[free_rope].beam=&beams[free_beam];
				ropes[free_rope].lockedto=0;
				free_beam++;
				free_rope++;
			}
			if (mode==15)
			{
				//parse ropables
				int id1;
				sscanf(line,"%i", &id1);
				ropables[free_ropable]=id1;
				free_ropable++;;
			}
			if (mode==16)
			{
				//parse ties
				int id1;
				float maxl, rate, shortl, longl;
				char option='n';
				hascommands=1;
				sscanf(line,"%i, %f, %f, %f, %f, %c", &id1, &maxl, &rate, &shortl, &longl, &option);
				int htype=BEAM_HYDRO;
				if (option=='i') htype=BEAM_INVISIBLE_HYDRO;
				init_beam(free_beam , &nodes[id1], &nodes[0], manager, parent, htype, default_break, default_spring, default_damp);
				beams[free_beam].L=maxl;
				beams[free_beam].refL=maxl;
				beams[free_beam].Lhydro=maxl;
				beams[free_beam].isrope=1;
				beams[free_beam].disabled=1;
				beams[free_beam].mSceneNode->detachAllObjects();
				//add short key
				commandkey[0].beams[commandkey[0].bfree]=-free_beam;
				commandkey[0].bfree++;
				//add long key
				//			commandkey[keyl].beams[commandkey[keyl].bfree]=free_beam;
				//			commandkey[keyl].bfree++;
				beams[free_beam].commandRatio=rate;
				beams[free_beam].commandShort=shortl;
				beams[free_beam].commandLong=longl;
				//register tie
				ties[free_tie]=free_beam;
				free_tie++;
				free_beam++;

			}

			if (mode==17)
			{
				//help material
				strcpy(helpmat,line);
				hashelp=1;
			}
			if (mode==18)
			{
				//cinecam
				float x,y,z;
				int n1, n2, n3, n4, n5, n6, n7, n8;
				sscanf(line,"%f, %f, %f, %i, %i, %i, %i, %i, %i, %i, %i", &x,&y,&z,&n1,&n2,&n3,&n4,&n5,&n6,&n7,&n8);
				//add node
				cinecameranodepos[freecinecamera]=free_node;
				init_node(cinecameranodepos[freecinecamera], px+x*cos(ry)+z*sin(ry), py+y , pz+x*cos(ry+3.14159/2.0)+z*sin(ry+3.14159/2.0));
				free_node++;
				//add beams
				float spring=8000.0;
				float damp=800.0;
				init_beam(free_beam , &nodes[cinecameranodepos[freecinecamera]], &nodes[n1], manager, parent, BEAM_INVISIBLE, default_break, spring, damp);
				free_beam++;
				init_beam(free_beam , &nodes[cinecameranodepos[freecinecamera]], &nodes[n2], manager, parent, BEAM_INVISIBLE, default_break, spring, damp);
				free_beam++;
				init_beam(free_beam , &nodes[cinecameranodepos[freecinecamera]], &nodes[n3], manager, parent, BEAM_INVISIBLE, default_break, spring, damp);
				free_beam++;
				init_beam(free_beam , &nodes[cinecameranodepos[freecinecamera]], &nodes[n4], manager, parent, BEAM_INVISIBLE, default_break, spring, damp);
				free_beam++;
				init_beam(free_beam , &nodes[cinecameranodepos[freecinecamera]], &nodes[n5], manager, parent, BEAM_INVISIBLE, default_break, spring, damp);
				free_beam++;
				init_beam(free_beam , &nodes[cinecameranodepos[freecinecamera]], &nodes[n6], manager, parent, BEAM_INVISIBLE, default_break, spring, damp);
				free_beam++;
				init_beam(free_beam , &nodes[cinecameranodepos[freecinecamera]], &nodes[n7], manager, parent, BEAM_INVISIBLE, default_break, spring, damp);
				free_beam++;
				init_beam(free_beam , &nodes[cinecameranodepos[freecinecamera]], &nodes[n8], manager, parent, BEAM_INVISIBLE, default_break, spring, damp);
				free_beam++;
				freecinecamera++;
			}

			if (mode==19)
			{
				//parse flares
				int ref, nx, ny;
				float ox, oy;
				sscanf(line,"%i, %i, %i, %f, %f", &ref,&nx,&ny, &ox, &oy);
				flares[free_flare].noderef=ref;
				flares[free_flare].nodex=nx;
				flares[free_flare].nodey=ny;
				flares[free_flare].offsetx=ox;
				flares[free_flare].offsety=oy;
				flares[free_flare].snode = manager->getRootSceneNode()->createChildSceneNode();
				char flarename[256];
				sprintf(flarename, "flare-%s-%i", truckname, free_flare);
				flares[free_flare].bbs=manager->createBillboardSet(flarename,1);
				flares[free_flare].bbs->createBillboard(0,0,0);
				flares[free_flare].bbs->setMaterialName("tracks/flare");
				flares[free_flare].snode->attachObject(flares[free_flare].bbs);

				flares[free_flare].light=manager->createLight(flarename);
				flares[free_flare].light->setType(Light::LT_SPOTLIGHT);
				flares[free_flare].light->setDiffuseColour( ColourValue(1.0, 1.0, 0.8));
				flares[free_flare].light->setSpecularColour( ColourValue(1.0, 1.0, 1.0));
				flares[free_flare].light->setAttenuation(500.0, 1.0, 0.1, 0.0);
				flares[free_flare].light->setSpotlightRange( Degree(35), Degree(45) );
				//flares[free_flare].lnode->attachObject(flares[free_flare].light);
				flares[free_flare].light->setCastShadows(false);
				free_flare++;
			}
			if (mode==20)
			{
				//parse props
				int ref, nx, ny;
				float ox, oy, oz;
				float rx, ry, rz;
				char meshname[256];
				sscanf(line,"%i, %i, %i, %f, %f, %f, %f, %f, %f, %s", &ref,&nx,&ny, &ox, &oy, &oz, &rx, &ry, &rz, meshname);
				props[free_prop].noderef=ref;
				props[free_prop].nodex=nx;
				props[free_prop].nodey=ny;
				props[free_prop].offsetx=ox;
				props[free_prop].offsety=oy;
				props[free_prop].offsetz=oz;
				props[free_prop].rot=Quaternion(Degree(rz), Vector3::UNIT_Z);
				props[free_prop].rot=props[free_prop].rot*Quaternion(Degree(ry), Vector3::UNIT_Y);
				props[free_prop].rot=props[free_prop].rot*Quaternion(Degree(rx), Vector3::UNIT_X);
				props[free_prop].wheel=0;
				props[free_prop].mirror=0;
				props[free_prop].pale=0;
				props[free_prop].spinner=0;
				if (!strncmp("leftmirror", meshname, 10)) props[free_prop].mirror=1;
				if (!strncmp("rightmirror", meshname, 11)) props[free_prop].mirror=-1;
				if (!strncmp("dashboard", meshname, 9))
				{
					//create a wheel
					char propname[256];
					sprintf(propname, "prop-%s-%i-wheel", truckname, free_prop);
					Entity *te = manager->createEntity(propname, "dirwheel.mesh");
					props[free_prop].wheel=manager->getRootSceneNode()->createChildSceneNode();
					props[free_prop].wheel->attachObject(te);
					props[free_prop].wheelpos=Vector3(-0.67, -0.61,0.24);
					if (!strncmp("dashboard-rh", meshname, 12)) props[free_prop].wheelpos=Vector3(0.67, -0.61,0.24);
				}
				char propname[256];
				sprintf(propname, "prop-%s-%i", truckname, free_prop);
				Entity *te = manager->createEntity(propname, meshname);
				props[free_prop].snode=manager->getRootSceneNode()->createChildSceneNode();
				props[free_prop].snode->attachObject(te);
				//hack for the spinprops
				if (!strncmp("spinprop", meshname, 8)) 
				{
					props[free_prop].spinner=1;
					props[free_prop].snode->getAttachedObject(0)->setCastShadows(false);
					props[free_prop].snode->setVisible(false);
				}
				if (!strncmp("pale", meshname, 4)) 
				{
					props[free_prop].pale=1;
				}
				//hack for the translucent drivers seat
				if (!strncmp("seat", meshname, 4) && !driversseatfound) {driversseatfound=true; te->setMaterialName("driversseat");};
				props[free_prop].beacontype='n';
				if (!strncmp("beacon", meshname, 6)) 
				{
					props[free_prop].bpos[0]=2.0*3.14*((Real)rand()/(Real)RAND_MAX);
					props[free_prop].brate[0]=4.0*3.14+((Real)rand()/(Real)RAND_MAX)-0.5;
					props[free_prop].beacontype='b';
					props[free_prop].bbs[0]=0;
					//the light
					props[free_prop].light[0]=manager->createLight(propname);
					props[free_prop].light[0]->setType(Light::LT_SPOTLIGHT);
					props[free_prop].light[0]->setDiffuseColour( ColourValue(1.0, 0.5, 0.0));
					props[free_prop].light[0]->setSpecularColour( ColourValue(1.0, 0.5, 0.0));
					props[free_prop].light[0]->setAttenuation(50.0, 1.0, 0.3, 0.0);
					props[free_prop].light[0]->setSpotlightRange( Degree(35), Degree(45) );
					props[free_prop].light[0]->setCastShadows(false);
					props[free_prop].light[0]->setVisible(false);
					//the flare billboard
					props[free_prop].bbsnode[0] = manager->getRootSceneNode()->createChildSceneNode();
					props[free_prop].bbs[0]=manager->createBillboardSet(propname,1);
					props[free_prop].bbs[0]->createBillboard(0,0,0);
					props[free_prop].bbs[0]->setMaterialName("tracks/beaconflare");
					props[free_prop].bbsnode[0]->attachObject(props[free_prop].bbs[0]);
					props[free_prop].bbsnode[0]->setVisible(false);
				}
				if (!strncmp("redbeacon", meshname, 9)) 
				{
					props[free_prop].bpos[0]=0.0;
					props[free_prop].brate[0]=1.0;
					props[free_prop].beacontype='r';
					props[free_prop].bbs[0]=0;
					//the light
					props[free_prop].light[0]=manager->createLight(propname);
					props[free_prop].light[0]->setType(Light::LT_POINT);
					props[free_prop].light[0]->setDiffuseColour( ColourValue(1.0, 0.0, 0.0));
					props[free_prop].light[0]->setSpecularColour( ColourValue(1.0, 0.0, 0.0));
					props[free_prop].light[0]->setAttenuation(50.0, 1.0, 0.3, 0.0);
					props[free_prop].light[0]->setCastShadows(false);
					props[free_prop].light[0]->setVisible(false);
					//the flare billboard
					props[free_prop].bbsnode[0] = manager->getRootSceneNode()->createChildSceneNode();
					props[free_prop].bbs[0]=manager->createBillboardSet(propname,1);
					props[free_prop].bbs[0]->createBillboard(0,0,0);
					props[free_prop].bbs[0]->setMaterialName("tracks/redbeaconflare");
					props[free_prop].bbsnode[0]->attachObject(props[free_prop].bbs[0]);
					props[free_prop].bbsnode[0]->setVisible(false);
					props[free_prop].bbs[0]->setDefaultDimensions(1.0, 1.0);
				}
				if (!strncmp("lightbar", meshname, 6)) 
				{
					int k;
					ispolice=true;
					props[free_prop].beacontype='p';
					for (k=0; k<4; k++)
					{
						props[free_prop].bpos[k]=2.0*3.14*((Real)rand()/(Real)RAND_MAX);
						props[free_prop].brate[k]=4.0*3.14+((Real)rand()/(Real)RAND_MAX)-0.5;
						props[free_prop].bbs[k]=0;
						//the light
						char rpname[256];
						sprintf(rpname,"%s-%i", propname, k);
						props[free_prop].light[k]=manager->createLight(rpname);
						props[free_prop].light[k]->setType(Light::LT_SPOTLIGHT);
						if (k>1)
						{
							props[free_prop].light[k]->setDiffuseColour( ColourValue(1.0, 0.0, 0.0));
							props[free_prop].light[k]->setSpecularColour( ColourValue(1.0, 0.0, 0.0));
						}
						else
						{
							props[free_prop].light[k]->setDiffuseColour( ColourValue(0.0, 0.5, 1.0));
							props[free_prop].light[k]->setSpecularColour( ColourValue(0.0, 0.5, 1.0));
						}
						props[free_prop].light[k]->setAttenuation(50.0, 1.0, 0.3, 0.0);
						props[free_prop].light[k]->setSpotlightRange( Degree(35), Degree(45) );
						props[free_prop].light[k]->setCastShadows(false);
						props[free_prop].light[k]->setVisible(false);
						//the flare billboard
						props[free_prop].bbsnode[k] = manager->getRootSceneNode()->createChildSceneNode();
						props[free_prop].bbs[k]=manager->createBillboardSet(rpname,1);
						props[free_prop].bbs[k]->createBillboard(0,0,0);
						if (k>1)
							props[free_prop].bbs[k]->setMaterialName("tracks/brightredflare");
						else
							props[free_prop].bbs[k]->setMaterialName("tracks/brightblueflare");
						props[free_prop].bbsnode[k]->attachObject(props[free_prop].bbs[k]);
						props[free_prop].bbsnode[k]->setVisible(false);
					}
				}

				free_prop++;
			}
			if (mode==21)
			{
				//parse globeams
				sscanf(line,"%f, %f, %f, %s", &default_deform,&default_break,&default_beam_diameter, default_beam_material);
				fadeDist=1000.0;
			}
			if (mode==22)
			{
				//parse wings
				int nds[8];
				float txes[8];
				char type;
				float cratio, mind, maxd;
				char afname[256];
				sscanf(line,"%i, %i, %i, %i, %i, %i, %i, %i, %f, %f, %f, %f, %f, %f, %f, %f, %c, %f, %f, %f, %s", 
					&nds[0],
					&nds[1],
					&nds[2],
					&nds[3],
					&nds[4],
					&nds[5],
					&nds[6],
					&nds[7],
					&txes[0],
					&txes[1],
					&txes[2],
					&txes[3],
					&txes[4],
					&txes[5],
					&txes[6],
					&txes[7],
					&type,
					&cratio,
					&mind,
					&maxd,
					afname
					);
				//visuals
				char wname[256];
				sprintf(wname, "wing-%s-%i",truckname, free_wing);
				char wnamei[256];
				sprintf(wnamei, "wingobj-%s-%i",truckname, free_wing);
				wings[free_wing].fa=new FlexAirfoil(manager, wname, nodes, nds[0], nds[1], nds[2], nds[3], nds[4], nds[5], nds[6], nds[7], texname, Vector2(txes[0], txes[1]), Vector2(txes[2], txes[3]), Vector2(txes[4], txes[5]), Vector2(txes[6], txes[7]), type, cratio, mind, maxd, afname, turboprops );
				Entity *ec = manager->createEntity(wnamei, wname);
				wings[free_wing].cnode = manager->getRootSceneNode()->createChildSceneNode();
				wings[free_wing].cnode->attachObject(ec);
				//induced drag
				if (wingstart==-1) {wingstart=free_wing;wingarea=warea(nodes[wings[free_wing].fa->nfld].Position, nodes[wings[free_wing].fa->nfrd].Position, nodes[wings[free_wing].fa->nbld].Position, nodes[wings[free_wing].fa->nbrd].Position);}
				else
				{
					if (nds[1]!=wings[free_wing-1].fa->nfld)
					{
						//discontinuity
						//inform wing segments
						float span=(nodes[wings[wingstart].fa->nfrd].Position-nodes[wings[free_wing-1].fa->nfld].Position).length();
						//					float chord=(nodes[wings[wingstart].fa->nfrd].Position-nodes[wings[wingstart].fa->nbrd].Position).length();
						LogManager::getSingleton().logMessage("BEAM: Full Wing "+StringConverter::toString(wingstart)+"-"+StringConverter::toString(free_wing-1)+" SPAN="+StringConverter::toString(span)+" AREA="+StringConverter::toString(wingarea));
						wings[wingstart].fa->enableInducedDrag(span,wingarea, false);
						wings[free_wing-1].fa->enableInducedDrag(span,wingarea, true);
						//we want also to add positional lights for first wing
						if (!hasposlights)
						{
							//Left green
							props[free_prop].noderef=wings[free_wing-1].fa->nfld;
							props[free_prop].nodex=wings[free_wing-1].fa->nflu;
							props[free_prop].nodey=wings[free_wing-1].fa->nfld; //ignored
							props[free_prop].offsetx=0.5;
							props[free_prop].offsety=0.0;
							props[free_prop].offsetz=0.0;
							props[free_prop].rot=Quaternion::IDENTITY;
							props[free_prop].wheel=0;
							props[free_prop].mirror=0;
							props[free_prop].pale=0;
							props[free_prop].spinner=0;
							props[free_prop].snode=NULL; //no visible prop
							props[free_prop].bpos[0]=0.0;
							props[free_prop].brate[0]=1.0;
							props[free_prop].beacontype='L';
							//no light
							props[free_prop].light[0]=0;
							//the flare billboard
							char propname[256];
							sprintf(propname, "prop-%s-%i", truckname, free_prop);
							props[free_prop].bbsnode[0] = manager->getRootSceneNode()->createChildSceneNode();
							props[free_prop].bbs[0]=manager->createBillboardSet(propname,1);
							props[free_prop].bbs[0]->createBillboard(0,0,0);
							props[free_prop].bbs[0]->setMaterialName("tracks/greenflare");
							props[free_prop].bbsnode[0]->attachObject(props[free_prop].bbs[0]);
							props[free_prop].bbsnode[0]->setVisible(false);
							props[free_prop].bbs[0]->setDefaultDimensions(0.5, 0.5);
							free_prop++;
							//Left flash
							props[free_prop].noderef=wings[free_wing-1].fa->nbld;
							props[free_prop].nodex=wings[free_wing-1].fa->nblu;
							props[free_prop].nodey=wings[free_wing-1].fa->nbld; //ignored
							props[free_prop].offsetx=0.5;
							props[free_prop].offsety=0.0;
							props[free_prop].offsetz=0.0;
							props[free_prop].rot=Quaternion::IDENTITY;
							props[free_prop].wheel=0;
							props[free_prop].mirror=0;
							props[free_prop].pale=0;
							props[free_prop].spinner=0;
							props[free_prop].snode=NULL; //no visible prop
							props[free_prop].bpos[0]=0.5; //alt
							props[free_prop].brate[0]=1.0;
							props[free_prop].beacontype='w';
							//light
							sprintf(propname, "prop-%s-%i", truckname, free_prop);
							props[free_prop].light[0]=manager->createLight(propname);
							props[free_prop].light[0]->setType(Light::LT_POINT);
							props[free_prop].light[0]->setDiffuseColour( ColourValue(1.0, 1.0, 1.0));
							props[free_prop].light[0]->setSpecularColour( ColourValue(1.0, 1.0, 1.0));
							props[free_prop].light[0]->setAttenuation(50.0, 1.0, 0.3, 0.0);
							props[free_prop].light[0]->setCastShadows(false);
							props[free_prop].light[0]->setVisible(false);
							//the flare billboard
							props[free_prop].bbsnode[0] = manager->getRootSceneNode()->createChildSceneNode();
							props[free_prop].bbs[0]=manager->createBillboardSet(propname,1);
							props[free_prop].bbs[0]->createBillboard(0,0,0);
							props[free_prop].bbs[0]->setMaterialName("tracks/flare");
							props[free_prop].bbsnode[0]->attachObject(props[free_prop].bbs[0]);
							props[free_prop].bbsnode[0]->setVisible(false);
							props[free_prop].bbs[0]->setDefaultDimensions(1.0, 1.0);
							free_prop++;
							//Right red
							props[free_prop].noderef=wings[wingstart].fa->nfrd;
							props[free_prop].nodex=wings[wingstart].fa->nfru;
							props[free_prop].nodey=wings[wingstart].fa->nfrd; //ignored
							props[free_prop].offsetx=0.5;
							props[free_prop].offsety=0.0;
							props[free_prop].offsetz=0.0;
							props[free_prop].rot=Quaternion::IDENTITY;
							props[free_prop].wheel=0;
							props[free_prop].mirror=0;
							props[free_prop].pale=0;
							props[free_prop].spinner=0;
							props[free_prop].snode=NULL; //no visible prop
							props[free_prop].bpos[0]=0.0;
							props[free_prop].brate[0]=1.0;
							props[free_prop].beacontype='R';
							//no light
							props[free_prop].light[0]=0;
							//the flare billboard
							sprintf(propname, "prop-%s-%i", truckname, free_prop);
							props[free_prop].bbsnode[0] = manager->getRootSceneNode()->createChildSceneNode();
							props[free_prop].bbs[0]=manager->createBillboardSet(propname,1);
							props[free_prop].bbs[0]->createBillboard(0,0,0);
							props[free_prop].bbs[0]->setMaterialName("tracks/redflare");
							props[free_prop].bbsnode[0]->attachObject(props[free_prop].bbs[0]);
							props[free_prop].bbsnode[0]->setVisible(false);
							props[free_prop].bbs[0]->setDefaultDimensions(0.5, 0.5);
							free_prop++;
							//Right flash
							props[free_prop].noderef=wings[wingstart].fa->nbrd;
							props[free_prop].nodex=wings[wingstart].fa->nbru;
							props[free_prop].nodey=wings[wingstart].fa->nbrd; //ignored
							props[free_prop].offsetx=0.5;
							props[free_prop].offsety=0.0;
							props[free_prop].offsetz=0.0;
							props[free_prop].rot=Quaternion::IDENTITY;
							props[free_prop].wheel=0;
							props[free_prop].mirror=0;
							props[free_prop].pale=0;
							props[free_prop].spinner=0;
							props[free_prop].snode=NULL; //no visible prop
							props[free_prop].bpos[0]=0.5; //alt
							props[free_prop].brate[0]=1.0;
							props[free_prop].beacontype='w';
							//light
							sprintf(propname, "prop-%s-%i", truckname, free_prop);
							props[free_prop].light[0]=manager->createLight(propname);
							props[free_prop].light[0]->setType(Light::LT_POINT);
							props[free_prop].light[0]->setDiffuseColour( ColourValue(1.0, 1.0, 1.0));
							props[free_prop].light[0]->setSpecularColour( ColourValue(1.0, 1.0, 1.0));
							props[free_prop].light[0]->setAttenuation(50.0, 1.0, 0.3, 0.0);
							props[free_prop].light[0]->setCastShadows(false);
							props[free_prop].light[0]->setVisible(false);
							//the flare billboard
							props[free_prop].bbsnode[0] = manager->getRootSceneNode()->createChildSceneNode();
							props[free_prop].bbs[0]=manager->createBillboardSet(propname,1);
							props[free_prop].bbs[0]->createBillboard(0,0,0);
							props[free_prop].bbs[0]->setMaterialName("tracks/flare");
							props[free_prop].bbsnode[0]->attachObject(props[free_prop].bbs[0]);
							props[free_prop].bbsnode[0]->setVisible(false);
							props[free_prop].bbs[0]->setDefaultDimensions(1.0, 1.0);
							free_prop++;
							hasposlights=true;
						}
						wingstart=free_wing;
						wingarea=warea(nodes[wings[free_wing].fa->nfld].Position, nodes[wings[free_wing].fa->nfrd].Position, nodes[wings[free_wing].fa->nbld].Position, nodes[wings[free_wing].fa->nbrd].Position);
					}
					else wingarea+=warea(nodes[wings[free_wing].fa->nfld].Position, nodes[wings[free_wing].fa->nfrd].Position, nodes[wings[free_wing].fa->nbld].Position, nodes[wings[free_wing].fa->nbrd].Position);
				}

				free_wing++;
			}
			if (mode==23)
			{
				//parse turboprops
				int ref,back,p1,p2,p3,p4;
				float power;
				char propfoil[256];
				sscanf(line,"%i, %i, %i, %i, %i, %i, %f, %s", &ref,&back,&p1, &p2, &p3, &p4, &power, propfoil);
				char propname[256];
				sprintf(propname, "turboprop-%s-%i", truckname, free_turboprop);
				turboprops[free_turboprop]=new Turboprop(manager, propname, nodes, ref, back,p1,p2,p3,p4, power, propfoil, free_turboprop, audio, disable_smoke);
				driveable=AIRPLANE;
				if (audio) audio->setupTurboprops();
				//setup visual
				int i;
				float pscale=(nodes[ref].Position-nodes[p1].Position).length()/2.25;
				for (i=0; i<free_prop; i++)
				{
					if (props[i].pale && props[i].noderef==ref) 
					{
						//setup size
						props[i].snode->scale(pscale,pscale,pscale);
						turboprops[free_turboprop]->addPale(props[i].snode);
					}
					if (props[i].spinner && props[i].noderef==ref) 
					{
						props[i].snode->scale(pscale,pscale,pscale);
						turboprops[free_turboprop]->addSpinner(props[i].snode);
					}
				}
				free_turboprop++;
			}
			if (mode==24)
			{
				//parse fusedrag
				int front,back;
				float width;
				char fusefoil[256];
				sscanf(line,"%i, %i, %f, %s", &front,&back,&width, fusefoil);
				fuseAirfoil=new Airfoil(fusefoil);
				fuseFront=&nodes[front];
				fuseBack=&nodes[front];
				fuseWidth=width;
			}
			if (mode==25)
			{
				//parse engoption
				float inertia;
				char type;
				sscanf(line,"%f, %c", &inertia, &type);
				if (engine) engine->setOptions(inertia, type);
			}
			if (mode==26)
			{
				//parse brakes
				sscanf(line,"%f", &brakeforce);
			}
			if (mode==27)
			{
				//parse rotators
				int axis1, axis2,keys,keyl;
				int p1[4], p2[4];
				float rate;
				hascommands=1;
				sscanf(line,"%i, %i, %i, %i, %i, %i, %i, %i, %i, %i, %f, %i, %i", &axis1, &axis2, &p1[0], &p1[1], &p1[2], &p1[3], &p2[0], &p2[1], &p2[2], &p2[3], &rate, &keys, &keyl);
				rotators[free_rotator].angle=0;
				rotators[free_rotator].rate=rate;
				rotators[free_rotator].axis1=axis1;
				rotators[free_rotator].axis2=axis2;
				int i;
				for (i=0; i<4; i++)
				{
					rotators[free_rotator].nodes1[i]=p1[i];
					rotators[free_rotator].nodes2[i]=p2[i];
				}
				//add short key
				commandkey[keys].rotators[commandkey[keys].rotfree]=-(free_rotator+1);
				commandkey[keys].rotfree++;
				//add long key
				commandkey[keyl].rotators[commandkey[keyl].rotfree]=free_rotator+1;
				commandkey[keyl].rotfree++;
				free_rotator++;
			}
			if (mode==28)
			{
				//parse screwprops
				int ref,back,up;
				float power;
				sscanf(line,"%i, %i, %i, %f", &ref,&back,&up, &power);
				if (audio) audio->setupBoat(truckmass);
				screwprops[free_screwprop]=new Screwprop(nodes, ref, back, up, power, water, splashp, ripplep, audio);
				driveable=BOAT;
				free_screwprop++;
			}

		};
		ds->close();
//		fclose(fd);
		//wing closure
		if (wingstart!=-1)
		{
			//inform wing segments
			float span=(nodes[wings[wingstart].fa->nfrd].Position-nodes[wings[free_wing-1].fa->nfld].Position).length();
			//		float chord=(nodes[wings[wingstart].fa->nfrd].Position-nodes[wings[wingstart].fa->nbrd].Position).length();
			LogManager::getSingleton().logMessage("BEAM: Full Wing "+StringConverter::toString(wingstart)+"-"+StringConverter::toString(free_wing-1)+" SPAN="+StringConverter::toString(span)+" AREA="+StringConverter::toString(wingarea));
			wings[wingstart].fa->enableInducedDrag(span,wingarea, false);
			wings[free_wing-1].fa->enableInducedDrag(span,wingarea, true);
			//wash calculator
			wash_calculator();
		}
		//add the cab visual
		LogManager::getSingleton().logMessage("BEAM: creating cab");
		if (free_texcoord>0 && free_cab>0)
		{
			//closure
			subtexcoords[free_sub]=free_texcoord;
			subcabs[free_sub]=free_cab;
			char wname[256];
			sprintf(wname, "cab-%s",truckname);
			char wnamei[256];
			sprintf(wnamei, "cabobj-%s",truckname);
			//the cab materials are as follow:
			//texname: base texture with emissive(2 pass) or without emissive if none available(1 pass), alpha cutting
			//texname-trans: transparency texture (1 pass)
			//texname-back: backface texture: black+alpha cutting (1 pass)
			//texname-noem: base texture without emissive (1 pass), alpha cutting

			//material passes must be:
			//0: normal texture
			//1: transparent (windows)
			//2: emissive
			/*strcpy(texname, "testtex");
			char transmatname[256];
			sprintf(transmatname, "%s-trans", texname);
			char backmatname[256];
			sprintf(backmatname, "%s-back", texname);
			hasEmissivePass=1;*/

			MaterialPtr mat=(MaterialPtr)(MaterialManager::getSingleton().getByName(texname));

			//-trans
			char transmatname[256];
			sprintf(transmatname, "%s-trans", texname);
			MaterialPtr transmat=mat->clone(transmatname);
			if (mat->getTechnique(0)->getNumPasses()>1) transmat->getTechnique(0)->removePass(1);
			transmat->getTechnique(0)->getPass(0)->setAlphaRejectSettings(CMPF_LESS_EQUAL, 128);
			transmat->getTechnique(0)->getPass(0)->setDepthWriteEnabled(false);
			transmat->getTechnique(0)->getPass(0)->getTextureUnitState(0)->setTextureFiltering(TFO_NONE);
			transmat->compile();

			//-back
			char backmatname[256];
			sprintf(backmatname, "%s-back", texname);
			MaterialPtr backmat=mat->clone(backmatname);
			if (mat->getTechnique(0)->getNumPasses()>1) backmat->getTechnique(0)->removePass(1);
			backmat->getTechnique(0)->getPass(0)->getTextureUnitState(0)->setColourOperationEx(LBX_SOURCE1, LBS_MANUAL, LBS_MANUAL, ColourValue(0,0,0),ColourValue(0,0,0));
			backmat->setReceiveShadows(false);
			//just in case
			//backmat->getTechnique(0)->getPass(0)->setSceneBlending(SBT_TRANSPARENT_ALPHA);
			//backmat->getTechnique(0)->getPass(0)->setAlphaRejectSettings(CMPF_GREATER, 128);
			backmat->compile();

			//-noem and -noem-trans
			if (mat->getTechnique(0)->getNumPasses()>1)
			{
				hasEmissivePass=1;
				char clomatname[256];
				sprintf(clomatname, "%s-noem", texname);
				MaterialPtr clomat=mat->clone(clomatname);
				clomat->getTechnique(0)->removePass(1);
				clomat->compile();
			}

			//base texture is not modified
			//	mat->compile();


			LogManager::getSingleton().logMessage("BEAM: creating mesh");
			cabMesh=new FlexObj(manager, nodes, free_texcoord, texcoords, free_cab, cabs, free_sub, subtexcoords, subcabs, texname, wname, subisback, backmatname, transmatname);
			LogManager::getSingleton().logMessage("BEAM: creating entity");
			Entity *ec = manager->createEntity(wnamei,wname);
			//		ec->setRenderQueueGroup(RENDER_QUEUE_6);
			LogManager::getSingleton().logMessage("BEAM: creating node");
			cabNode = manager->getRootSceneNode()->createChildSceneNode();
			LogManager::getSingleton().logMessage("BEAM: attaching");
			cabNode->attachObject(ec);
		};
		LogManager::getSingleton().logMessage("BEAM: cab ok");
		//	mWindow->setDebugText("Beam number:"+ StringConverter::toString(free_beam));

		//place correctly
		if (!hasfixes) 
		{
			//check if oversized
			calcBox();
			if ((maxz-minz-0.6>5.0 || maxy-miny-0.6>4.5) && postload)
				resetPosition(px-10.0-(maxx-minx), pz, true);
			else resetPosition(px, pz, true);

		}
		//compute collision box
		calcBox();

	}

	void addWheel(SceneManager *manager, SceneNode *parent, Real radius, Real width, int rays, int node1, int node2, int snode, int braked, int propulsed, int torquenode, float mass, float wspring, float wdamp, char* texf, char* texb)
	{
		int i;
		int nodebase=free_node;
		int node3;
		int contacter_wheel=1;
		//ignore the width parameter
		width=(nodes[node1].Position-nodes[node2].Position).length();
		//enforce the "second node must have a larger Z coordinate than the first" constraint
		if (nodes[node1].Position.z>nodes[node2].Position.z)
		{
			//swap
			node3=node1;
			node1=node2;
			node2=node3;
		}
		//ignore the sign of snode, just do the thing automatically
		//if (snode<0) node3=-snode; else node3=snode;
		if (snode<0) snode=-snode;
		bool closest1=false;
		if (snode!=9999) closest1=(nodes[snode].Position-nodes[node1].Position).length()<(nodes[snode].Position-nodes[node2].Position).length();
		Real px=nodes[node1].Position.x;
		Real py=nodes[node1].Position.y;
		Real pz=nodes[node1].Position.z;
		for (i=0; i<rays; i++)
		{
			//with propnodes and variable friction
			init_node(nodebase+i*2, px+radius*sin((Real)i*6.283185307179/(Real)rays), py+radius*cos((Real)i*6.283185307179/(Real)rays), pz, NODE_NORMAL, mass/(2.0*rays),1, WHEEL_FRICTION_COEF*width);
			if (contacter_wheel)
			{
				contacters[free_contacter].nodeid=nodebase+i*2;
				contacters[free_contacter].contacted=0;
				contacters[free_contacter].opticontact=0;
				free_contacter++;;
			}
			init_node(nodebase+i*2+1, px+radius*sin((Real)i*6.283185307179/(Real)rays), py+radius*cos((Real)i*6.283185307179/(Real)rays), pz+width, NODE_NORMAL, mass/(2.0*rays),1, WHEEL_FRICTION_COEF*width);
			if (contacter_wheel)
			{
				contacters[free_contacter].nodeid=nodebase+i*2+1;
				contacters[free_contacter].contacted=0;
				contacters[free_contacter].opticontact=0;
				free_contacter++;;
			}
			//wheel object
			wheels[free_wheel].nodes[i*2]=&nodes[nodebase+i*2];
			wheels[free_wheel].nodes[i*2+1]=&nodes[nodebase+i*2+1];
		}
		free_node+=2*rays;
		for (i=0; i<rays; i++)
		{
			//bounded
			init_beam(free_beam , &nodes[node1], &nodes[nodebase+i*2], manager, parent, BEAM_INVISIBLE, default_break, wspring, wdamp, -1.0, 0.66, 0.0);free_beam++;
			//bounded
			init_beam(free_beam , &nodes[node2], &nodes[nodebase+i*2+1], manager, parent, BEAM_INVISIBLE, default_break, wspring, wdamp, -1.0, 0.66, 0.0);free_beam++;
			init_beam(free_beam , &nodes[node2], &nodes[nodebase+i*2], manager, parent, BEAM_INVISIBLE, default_break, wspring, wdamp);free_beam++;
			init_beam(free_beam , &nodes[node1], &nodes[nodebase+i*2+1], manager, parent, BEAM_INVISIBLE, default_break, wspring, wdamp);free_beam++;
			//reinforcement
			init_beam(free_beam , &nodes[node1], &nodes[nodebase+i*2], manager, parent, BEAM_INVISIBLE, default_break, wspring, wdamp);free_beam++;
			init_beam(free_beam , &nodes[nodebase+i*2], &nodes[nodebase+i*2+1], manager, parent, BEAM_INVISIBLE, default_break, wspring, wdamp);free_beam++;
			init_beam(free_beam , &nodes[nodebase+i*2], &nodes[nodebase+((i+1)%rays)*2], manager, parent, BEAM_INVISIBLE, default_break, wspring, wdamp);free_beam++;
			init_beam(free_beam , &nodes[nodebase+i*2+1], &nodes[nodebase+((i+1)%rays)*2+1], manager, parent, BEAM_INVISIBLE, default_break, wspring, wdamp);free_beam++;
			init_beam(free_beam , &nodes[nodebase+i*2], &nodes[nodebase+((i+1)%rays)*2+1], manager, parent, BEAM_INVISIBLE, default_break, wspring, wdamp);free_beam++;
			//reinforcement
			init_beam(free_beam , &nodes[nodebase+i*2+1], &nodes[nodebase+((i+1)%rays)*2], manager, parent, BEAM_INVISIBLE, default_break, wspring, wdamp);free_beam++;
			if (snode!=9999)
			{
				//back beams
				if (closest1) {init_beam(free_beam , &nodes[snode], &nodes[nodebase+i*2], manager, parent, BEAM_VIRTUAL, default_break, wspring, wdamp);free_beam++;}
				else         {init_beam(free_beam , &nodes[snode], &nodes[nodebase+i*2+1], manager, parent, BEAM_VIRTUAL, default_break, wspring, wdamp);free_beam++;};
			}
		}
		//wheel object
		wheels[free_wheel].braked=braked;
		wheels[free_wheel].propulsed=propulsed;
		wheels[free_wheel].nbnodes=2*rays;
		wheels[free_wheel].refnode0=&nodes[node1];
		wheels[free_wheel].refnode1=&nodes[node2];
		wheels[free_wheel].radius=radius;
		wheels[free_wheel].speed=0.0;
		wheels[free_wheel].arm=&nodes[torquenode];
		if (propulsed)
		{
			//for inter-differential locking
			proppairs[proped_wheels]=free_wheel;
			proped_wheels++;
		}
		if (braked) braked_wheels++;
		//find near attach
		Real l1=(nodes[node1].Position-nodes[torquenode].Position).length();
		Real l2=(nodes[node2].Position-nodes[torquenode].Position).length();
		if (l1<l2) wheels[free_wheel].near_attach=&nodes[node1]; else wheels[free_wheel].near_attach=&nodes[node2];
		//visuals
		char wname[256];
		sprintf(wname, "wheel-%s-%i",truckname, free_wheel);
		char wnamei[256];
		sprintf(wnamei, "wheelobj-%s-%i",truckname, free_wheel);
		//	strcpy(texf, "tracks/wheelface,");
		vwheels[free_wheel].fm=new FlexMesh(manager, wname, nodes, node1, node2, nodebase, rays, texf, texb);
		Entity *ec = manager->createEntity(wnamei, wname);
		//	ec->setMaterialName("tracks/wheel");
		//ec->setMaterialName("Test/ColourTest");
		vwheels[free_wheel].cnode = manager->getRootSceneNode()->createChildSceneNode();
		vwheels[free_wheel].cnode->attachObject(ec);
		//	cnode->setPosition(1000,2,940);
		free_wheel++;
	}

	void init_node(int pos, Real x, Real y, Real z, int type=NODE_NORMAL, Real m=10.0, int iswheel=0, Real friction=CHASSIS_FRICTION_COEF)
	{
		nodes[pos].Position=Vector3(x,y,z);
		nodes[pos].iPosition=Vector3(x,y,z);
		nodes[pos].Velocity=Vector3::ZERO;
		nodes[pos].Forces=Vector3::ZERO;
		nodes[pos].locked=m<0.0;
		nodes[pos].mass=m;
		nodes[pos].iswheel=iswheel;
		nodes[pos].friction=friction;
		nodes[pos].masstype=type;
		nodes[pos].contactless=0;
		nodes[pos].contacted=0;
		nodes[pos].lockednode=0;
		nodes[pos].buoyanceForce=Vector3::ZERO;
		nodes[pos].buoyancy=truckmass/15.0;//DEFAULT_BUOYANCY;
		nodes[pos].lastdrag=Vector3(0,0,0);
		nodes[pos].gravimass=Vector3(0,DEFAULT_GRAVITY*m,0);
		nodes[pos].wetstate=DRY;
		nodes[pos].isHot=false;
		if (type==NODE_LOADED) masscount++;
	}

	void init_beam(int pos, node_t *p1, node_t *p2, SceneManager *manager, SceneNode *parent, int type, Real strength, Real spring, Real damp, Real length=-1.0, float shortbound=-1.0, float longbound=-1.0, float precomp=1.0)
	{
		beams[pos].p1=p1;
		beams[pos].p2=p2;
		beams[pos].type=type;
		if (length<0.0)
		{
			//calculate the length
			Vector3 t;
			t=p1->Position;
			t=t-p2->Position;
			beams[pos].L=precomp*t.length();
		} else beams[pos].L=length;
		beams[pos].k=spring;
		beams[pos].d=damp;
		beams[pos].broken=0;
		beams[pos].Lhydro=beams[pos].L;
		beams[pos].refL=beams[pos].L;
		beams[pos].hydroRatio=0.0;
		beams[pos].hydroSpeed=false;
		beams[pos].stress=0.0;
		beams[pos].strength=strength;
		beams[pos].lastforce=Vector3(0,0,0);
		beams[pos].isrope=0;
		beams[pos].disabled=0;
		beams[pos].maxposstress=default_deform;
		beams[pos].maxnegstress=-default_deform;
		beams[pos].minendmass=1.0;
		if (shortbound!=-1.0)
		{
			beams[pos].bounded=1;
			beams[pos].shortbound=shortbound;
			beams[pos].longbound=longbound;

		} else beams[pos].bounded=0;

		if (beams[pos].L<0.01)
		{
			LogManager::getSingleton().logMessage("Error: beam "
				+StringConverter::toString(pos)+" is too short ("+StringConverter::toString(beams[pos].L)+"m)");
			exit(8);
		};

		//        if (type!=BEAM_VIRTUAL && type!=BEAM_INVISIBLE)
		if (type!=BEAM_VIRTUAL)
		{
			//setup visuals
			//the cube is 100x100x100
			char bname[255];
			sprintf(bname, "beam-%s-%i", truckname, pos);
			beams[pos].mEntity = manager->createEntity(bname, "beam.mesh");
			//		ec->setCastShadows(false);
			if (type==BEAM_HYDRO || type==BEAM_MARKED) beams[pos].mEntity->setMaterialName("tracks/Chrome");
			else beams[pos].mEntity->setMaterialName(default_beam_material);
			beams[pos].mSceneNode = beamsRoot->createChildSceneNode();
			//            beams[pos].mSceneNode->attachObject(ec);
			//            beams[pos].mSceneNode->setScale(default_beam_diameter/100.0,length/100.0,default_beam_diameter/100.0);
			beams[pos].mSceneNode->setScale(default_beam_diameter,length,default_beam_diameter);
			//register a material for skeleton view
			sprintf(bname, "mat-beam-%s-%i", truckname, pos);
			MaterialPtr mat=(MaterialPtr)(MaterialManager::getSingleton().create(bname, "Skel"));
			Technique* technique = mat->getTechnique(0);
			Pass* pass = technique->getPass(0); 
			//			TextureUnitState* tunit=pass->getTextureUnitState(0);
			TextureUnitState* tunit=pass->createTextureUnitState();
			tunit->setColourOperationEx(LBX_MODULATE, LBS_MANUAL, LBS_CURRENT, ColourValue(0.0, 0.0, 1.0));
		}
		else {beams[pos].mSceneNode=0;beams[pos].mEntity=0;};
		if (beams[pos].mSceneNode && beams[pos].mEntity && !(type==BEAM_VIRTUAL || type==BEAM_INVISIBLE || type==BEAM_INVISIBLE_HYDRO)) beams[pos].mSceneNode->attachObject(beams[pos].mEntity);//beams[pos].mSceneNode->setVisible(0);
	}



	void updateVisual()
	{
		int i;
		Vector3 ref=Vector3(0.0,1.0,0.0);
		//dust
		if (dustp && state==ACTIVATED) dustp->update(WheelSpeed);
		if (dripp) dripp->update(WheelSpeed);
		if (splashp) splashp->update(WheelSpeed);
		if (ripplep) ripplep->update(WheelSpeed);
		if (smokeNode && smokeRef && engine) 
		{
			Vector3 dir=nodes[smokeId].Position-nodes[smokeRef].Position;
			//			dir.normalise();
			ParticleEmitter *emit=smoker->getEmitter(0);
			smokeNode->setPosition(nodes[smokeId].Position);
			emit->setDirection(dir);
			if (engine->getSmoke()!=-1.0) 
			{
				emit->setEnabled(true);
				emit->setColour(ColourValue(0.0,0.0,0.0,0.02+engine->getSmoke()*0.06));
				emit->setTimeToLive((0.02+engine->getSmoke()*0.06)/0.04);
			}
			else 
			{
				emit->setEnabled(false);
			};
			emit->setParticleVelocity(1.0+engine->getSmoke()*2.0, 2.0+engine->getSmoke()*3.0);
		}

		updateProps();

		for (i=0; i<free_turboprop; i++) turboprops[i]->updateVisuals();

		if (!skeleton)
		{
			for (i=0; i<free_beam; i++)
			{
				if (beams[i].broken==1 && beams[i].mSceneNode) {beams[i].mSceneNode->detachAllObjects();beams[i].broken=2;}
				if (beams[i].mSceneNode!=0 && beams[i].type!=BEAM_INVISIBLE && beams[i].type!=BEAM_INVISIBLE_HYDRO && beams[i].type!=BEAM_VIRTUAL && !beams[i].disabled)
				{
					beams[i].mSceneNode->setPosition(beams[i].p1->Position.midPoint(beams[i].p2->Position));
					beams[i].mSceneNode->setOrientation(specialGetRotationTo(ref,beams[i].p1->Position-beams[i].p2->Position));
					//					beams[i].mSceneNode->setScale(default_beam_diameter/100.0,(beams[i].p1->Position-beams[i].p2->Position).length()/100.0,default_beam_diameter/100.0);
					beams[i].mSceneNode->setScale(default_beam_diameter,(beams[i].p1->Position-beams[i].p2->Position).length(),default_beam_diameter);
				};
			}
			for (i=0; i<free_wheel; i++)
			{
				vwheels[i].cnode->setPosition(vwheels[i].fm->flexit());
			}
			if (cabMesh) cabNode->setPosition(cabMesh->flexit());
			//wings
			for (i=0; i<free_wing; i++)
			{
				if (wings[i].fa->type=='a') wings[i].fa->setControlDeflection(aileron);
				if (wings[i].fa->type=='b') wings[i].fa->setControlDeflection(-aileron);
				if (wings[i].fa->type=='r') wings[i].fa->setControlDeflection(rudder);
				if (wings[i].fa->type=='e') wings[i].fa->setControlDeflection(elevator);
				if (wings[i].fa->type=='f') wings[i].fa->setControlDeflection(flapangles[flap]);
				wings[i].cnode->setPosition(wings[i].fa->flexit());
			}
		}
		else
		{
			for (i=0; i<free_beam; i++)
			{
				if (beams[i].mSceneNode!=0 && !beams[i].disabled)
				{
					beams[i].mSceneNode->setPosition(beams[i].p1->Position.midPoint(beams[i].p2->Position));
					beams[i].mSceneNode->setOrientation(specialGetRotationTo(ref,beams[i].p1->Position-beams[i].p2->Position));
					beams[i].mSceneNode->setScale(default_beam_diameter,(beams[i].p1->Position-beams[i].p2->Position).length(),default_beam_diameter);
					//					beams[i].mSceneNode->setScale(default_beam_diameter/100.0,(beams[i].p1->Position-beams[i].p2->Position).length()/100.0,default_beam_diameter/100.0);
				};
			}
		}

	}

	Quaternion specialGetRotationTo(const Vector3& src, const Vector3& dest) const
	{
		// Based on Stan Melax's article in Game Programming Gems
		Quaternion q;
		// Copy, since cannot modify local
		Vector3 v0 = src;
		Vector3 v1 = dest;
		v0.normalise();
		v1.normalise();

		Vector3 c = v0.crossProduct(v1);

		// NB if the crossProduct approaches zero, we get unstable because ANY axis will do
		// when v0 == -v1
		Real d = v0.dotProduct(v1);
		// If dot == 1, vectors are the same
		if (d >= 1.0f)
		{
			return Quaternion::IDENTITY;
		}
		Real s = Math::Sqrt( (1+d)*2 );
		if (s==0) return Quaternion::IDENTITY; 
		Real invs = 1 / s;


		q.x = c.x * invs;
		q.y = c.y * invs;
		q.z = c.z * invs;
		q.w = s * 0.5;
		return q;
	}

