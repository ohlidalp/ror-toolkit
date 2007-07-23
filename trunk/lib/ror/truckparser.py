#!/bin/env python
# Thomas Fischer 16/05/2007 thomas (at) thomasfischer.biz
import sys, os, os.path, tempfile, pickle
    ## default values: required:True
    ## please note: unkown args are marked with 'WHAT IS THIS'
class rorparser:
    ### This specifies all valid commands
    commands = {
                # set_beam_defaults changes the beams (but also the hydros and ropes) default characteristics that will be used for the beams declared after the line. You can use this line many times to make different groups of beams that have different characteristics (e.g. stronger chassis, softer cab, etc.). This method is better than the globeams command that is now deprecated. The parameters comes on the same line, after set_beam_defaults. You can use the first parameters (most usefull) and safely ignore the last parameters.
                'set_beam_defaults':[
                    # Spring constant (use -1 for the default, which is 9000000)
                    {'name':'spring constant','type':'float'},
                    # Damping constant (use -1 for the default, which is 12000)
                    {'name':'damping constant','type':'float'},
                    # Deformation threshold constant (use -1 for the default, which is 400000)
                    {'name':'deformation threshold','type':'float'},
                    # Breaking thresold constant (use -1 for the default, which is 1000000)
                    {'name':'breaking thresold','type':'float'},
                    # Beam diameter (use -1 for the default, which is 0.05)
                    {'name':'beam diameter','type':'float', 'required':False},
                    # Beam material (default: tracks/beam)
                    {'name':'beam material','type':'string', 'required':False},
                ],


                # Enables collision between wheels and the textured surfaces of a truck.
                'rollon':[],

                # Forwards the commandkeys pressed while riding a truck to loads in close proximity. It is used to remote control the commands of a load. The load must have the "importcommands" tag. 
                'forwardcommands':[],

                # Enables a load to receive commandkeys from a manned vehicle in close proximity. The controlling vehicle must have the "forwardcommands" tag. The load only receives the keys that are pressed by the player, it must contain a commands section. Commands section for loads is defined in the same manner as in manned trucks.
                'importcommands':[],

                # the triangles backsides of the submesh will be black instead of see-through.
                'backmesh':[],

                # rescue-truck?
                'rescuer':[],

                # end of file
                'end':[],


    }
    
    ### This specifies all valid sections und subsections
    sections = {
                # This section is the only that is not introduced by a keyword. It is the name of the truck, and it must absolutely be the first line of the file. e.g.
                'title':[
                    {'name':'title','type':'string'},
                ],


                # This section is very special and should not be used for most designs. It was created to make the bridge. It allows you to alter the default mechanical and visual beam properties. The parameters are: default stress at which beams deforms (in Newtons), default stress at which beams break, default beams diameter (in meter), default beams material. This section is deprecated and should not be used for truck designs. Use the more powerfull set_beam_defaults instead.
                'globals':[
                    {'name':'dry mass', 'type':'float'},
                    {'name':'cargo mass', 'type':'float'},
                    {'name':'material', 'type':'string'},
                ],


                # This section is very special and should not be used for most designs. It was created to make the bridge. It allows you to alter the default mechanical and visual beam properties. The parameters are: default stress at which beams deforms (in Newtons), default stress at which beams break, default beams diameter (in meter), default beams material. This section is deprecated and should not be used for truck designs. Use the more powerfull set_beam_defaults instead.
                'globeams':[
                    #default stress at which beams deforms (in Newtons)
                    {'name':'deform', 'type':'float'},
                    #default stress at which beams break
                    {'name':'break', 'type':'float'},
                    #default beams diameter (in meter)
                    {'name':'diameter', 'type':'float'},
                    #default beams material
                    {'name':'material', 'type':'string'},
                ],


                # The engine section contains the engine parameters.
                'engine':[
                    {'name':'min rpm', 'type':'float'},
                    {'name':'max rpm', 'type':'float'},
                    #torque (flat torque model, usually correct for large intercooled turbo diesels). This defines the engine power!
                    {'name':'torque', 'type':'float'},
                    #differential ratio (a global gear conversion ratio)
                    {'name':'differential ratio', 'type':'float'},
                    {'name':'rear gear', 'type':'float'},
                    {'name':'first gear', 'type':'float'},
                    {'name':'second gear', 'type':'float'},
                    {'name':'third gear', 'type':'float','required':False},
                    {'name':'fourth gear', 'type':'float','required':False},
                    {'name':'fifth gear', 'type':'float','required':False},
                    {'name':'sixth gear', 'type':'float','required':False},
                    {'name':'seventh gear', 'type':'float','required':False},
                    {'name':'eighth gear', 'type':'float','required':False},
                    {'name':'nineth gear', 'type':'float','required':False},
                    {'name':'tenth rpm', 'type':'float','required':False},
                    {'name':'eleventh rpm', 'type':'float','required':False},
                    {'name':'twelveth rpm', 'type':'float','required':False},
                    {'name':'thirteenth rpm', 'type':'float','required':False},
                    {'name':'fourteenth rpm', 'type':'float','required':False},
                    {'name':'fifteenth rpm', 'type':'float','required':False},
                    {'name':'sixteenth rpm', 'type':'float','required':False},
                    #The last gear must be followed by a -1 value.
                    {'name':'ending argument', 'type':'float','required':False},
                ],


                # Engoption sets optional parameters to the engine, mainly for car engines. Parameters are:
                'engoption':[
                    # Engine inertia: the default game value is 10.0, which is correct for a large diesel engine, but for smaller engines you might want smaller values, like 1.0 or 0.5 for small athmospheric engines.
                    {'name':'Engine inertia', 'type':'float'},

                    # Engine type: valid types are t for truck engine and c for car engine. This changes engine sound and other engine characteristics.
                    {'name':'Engine type', 'type':'string',
                                             'validvalues':[
                                                'c',    # truck engine
                                                't',    # car engine
                                            ]},
                ],


                # This allows you to change the default braking force value (the default is 30000), generally to a lower value for smaller trucks and cars.
                'brakes':[
                    # braking force
                    {'name':'braking force', 'type':'float'},
                ],

                # This section is important. It helps to position the truck in space, by defining a local direction reference. For example this is used to measure the pitch and the roll of the truck. The three parameters are node numbers (defined in the next section). The first if the reference and may be anywhere, the second must be behind the first (if you look at the front of the truck, it is hidden behind the first), and the third must be at the left of the first (if you look to the right of the truck, it is hidden by the first)
                'cameras':[
                    # The first if the reference and may be anywhere
                    {'name':'center node', 'type':'node'},
                    # The second must be behind the first
                    {'name':'back node', 'type':'node'},
                    # The third must be at the left of the first
                    {'name':'left node', 'type':'node'},
                ],

                # With this section begins the structural description. Each line defines a node. The first parameter is the node number, and must absolutely be consecutive. The three following parameters are the x,y,z coordinates, in meter. You can attach an optional option to a node by adding a single character. Recognized options are:
                'nodes':[
                    {'name':'id', 'type':'int'},
                    {'name':'x', 'type':'float'},
                    {'name':'y', 'type':'float'},
                    {'name':'z', 'type':'float'},
                    {'name':'options', 'type':'string',
                                             'required':False,
                                             'default':'n',
                                             'validvalues':[
                                                'n', # normal node, nothing special
                                                'l', # this node bears a part of the cargo load
                                                'f', # this node has extra friction with the ground (usefull for feets)
                                                'x', # this node is the exhaust point (requires a "y" node)
                                                'y', # exhaust reference point, this point is at the opposite of the direction of the exhaust
                                                'c', # this node will not detect contact with ground (can be used for optimization, on inner chassis parts)
                                                'h', # this node is a hook point (e.g. the extremity of a crane)
                                                'e', # this node is a terrain editing point (used in the terrain editor truck)
                                                'b', # this node is assigned an extra buoyancy force (experimental)
                                            ]},
                ],


                # Fixes are nodes that are fixed in place. That means that once put in place in the terrain, they will never move, whatever happens. This is usefull to make fixed scenery elements from beams, like bridges. Just add the node number that you want to fix.
                'fixes':[
                    # node number that you want to fix.
                    {'name':'node', 'type':'node'},
                ],


                # This section defines all the beams connecting nodes. Each line describes a beam. The two first parameters are the node number of the two connected nodes. Order has no importance. There is an optional 3rd parameter, composed of a single character.
                'beams':[
                    {'name':'first node', 'type':'node'},
                    {'name':'second node', 'type':'node'},
                    {'name':'options', 'type':'string',
                                             'required':False,
                                             'default':'n',
                                             'validvalues':[
                                                'n', # visible, default
                                                'v', # visible, default
                                                'i', # this beam is invisible. Very usefull to hide "cheating" structural beam, or to improve performances once the truck is textured.
                                                'r', # this beam is a rope (opposes no force to compression)
                                            ]}
                ],


                # Shocks can be seen as tunable beams, useful for suspensions.
                'shocks':[
                    # the two nodes connected by the shock
                    {'name':'first node', 'type':'node'},
                    {'name':'second node', 'type':'node'},
                    # spring rate: the stiffness
                    {'name':'spring rate', 'type':'float'},
                    # to adjust the amount of rebound: the best value is given by 2*sqrt(suspended mass*spring)
                    {'name':'dampening', 'type':'float'},
                    # shortbound, longbound: defines the amount of deformation the shock can support (beyond, it becomes rigid as a standard beam) when shortened and lengthened
                    {'name':'shortbound', 'type':'float'},
                    {'name':'longbound', 'type':'float'},
                    # allows to compress or depress the suspension (leave it to 1.0 for most cases).
                    {'name':'precomp', 'type':'float'},
                    # You can make the shocks stability-active with optional parameters:
                    {'name':'options', 'type':'string',
                                             'required':False,
                                             'default':None,
                                             'validvalues':[
                                                'n', # normal
                                                'l', # to make a left-hand active shock
                                                'r', # to make a right-hand active shock
                                                'i', # to make the shock invisible (AVAILABLE FROM VERSION 0.29).
                                            ]}
                ],


                # The hydros section concerns only the direction actuactors! They are beams that changes of length depending on the direction command.
                'hydros':[
                    # two node numbers
                    {'name':'first node', 'type':'node'},
                    {'name':'second node', 'type':'node'},
                    # lenghtening factor (negative or positive depending on wether you want to lenghten or shorten when turning left or the contrary)
                    {'name':'lenghtening factor', 'type':'float'},
                    # optional flags
                    {'name':'options', 'type':'string',
                                             'required':False,
                                             'default':None,
                                             'validvalues':[
                                                's', # WHAT IS THIS?
                                                'n', # normal
                                                'i', # make the hydro invisible.
                                            ]}
                ],


                # The commands section describes the "real" hydros, those you command with the function keys. They are like beams, but their length varies depending with the function keys you press.
                'commands':[
                    # two node numbers
                    {'name':'first node', 'type':'node'},
                    {'name':'second node', 'type':'node'},
                    # speed rate (how fast the hydro will change length)
                    {'name':'speed rate', 'type':'float'},
                    # the shortest length (1.0 is the startup length)
                    {'name':'shortest length', 'type':'float'},
                    # the longest length (1.0 is the startup length)
                    {'name':'longest length', 'type':'float'},
                    # the number of the shortening function key (between 1 and 12)
                    {'name':'shortening key', 'type':'int'},
                    # the number of the lengthtening function key (between 1 and 12)
                    {'name':'lengthtening key', 'type':'int'},
                    # optional flags
                    {'name':'options', 'type':'string',
                                             'required':False,
                                             'default':None,
                                             'validvalues':[
                                                'i', # make the hydro invisible.
                                                'r', # WHAT IS THIS
                                                'n', # WHAT IS THIS
                                                'v', # WHAT IS THIS
                                            ]}
                ],


                # Rotators are alternate commands(hydros) that allows you to do turntables, like in the base of a rotating crane. They use 10 reference nodes:  and  Then, in a similar way to commands, comes the , and the numbers of the left and right function keys.
                'rotators':[
                    # 2 nodes to define the axis of rotation
                    {'name':'axis1 node', 'type':'node'},
                    {'name':'axis2 node', 'type':'node'},
                    # 4 nodes (must be a square, centered with the axis), to define the baseplate
                    {'name':'base1 node', 'type':'node'},
                    {'name':'base2 node', 'type':'node'},
                    {'name':'base3 node', 'type':'node'},
                    {'name':'base4 node', 'type':'node'},
                    # 4 nodes (again, a square, centered with the axis) to define the rotating plate.
                    {'name':'rotbase1 node', 'type':'node'},
                    {'name':'rotbase2 node', 'type':'node'},
                    {'name':'rotbase3 node', 'type':'node'},
                    {'name':'rotbase4 node', 'type':'node'},
                    # speed rate (how fast the hydro will change length)
                    {'name':'speed rate', 'type':'float'},
                    # the number of the left key (between 1 and 12)
                    {'name':'left key', 'type':'int'},
                    # the number of the right key (between 1 and 12)
                    {'name':'right key', 'type':'int'},
                ],


                # The contacters section lists the nodes that may contact with cab triangle. This concerns only contacts with other trucks or loads. You can easily omit this section at first.
                'contacters':[
                    #node that may contact with cab triangle
                    {'name':'node', 'type':'node'},
                ],

                # The help section gives the name material used for the help panel on the dashboard. This material must be defined elsewhere in the MaterialFile. This is optional.
                'help':[
                    {'name':'dashboard material', 'type':'string'},
                ],


                # Ropes are special beams that have no compression strength (they can shorten easily) but have standard extension strength, like a cable or a chain. They have also another particularity: the second node can "grab" the nearest reachable ropable node with the 'O' key. Standard use is to use a chassis node as the first node, and a "free" node as the second node (free as in not attached by any other beam). The best example of this are the chains of the multibennes truck.
                'ropes':[
                    {'name':'first node', 'type':'node'},
                    {'name':'second node', 'type':'node'},
                ],


                # Ties are also special beams that have no compression strength (they can shorten easily) but have standard extension strength, like a cable or a chain. As the Ropes, they grab the nearest reachable ropable node with the 'O' key. But there is a twist: unlike the ropes, they disappear when not attached (because they have no extremity node at rest) and they automatically shorten until the extension forces reaches a thresold. They are very usefull to solidly strap a load to a chassis. The parameters are the number of the root node (the starting point of the beam), the maximum reach length, the rate of auto-shortening, the shortest length possible, and the last parameter... well... is probably not very usefull and should be kept as 1.0... You can make a tie invisible with the "i" option.
                'ties':[
                    {'name':'root node', 'type':'node'},
                    {'name':'max len', 'type':'float'},
                    {'name':'rate', 'type':'float'},
                    {'name':'short', 'type':'float'},
                    {'name':'long', 'type':'float'},
                    {'name':'options', 'type':'string',
                                             'required':False,
                                             'default':None,
                                             'validvalues':[
                                                'i', # make the hydro invisible.
                                            ]},
                ],


                # This section lists the nodes that can be catched by ropes or ties. Good use is to define some ropable nodes at the front and back of the truck to allow towing the truck.
                'ropables':[
                    {'name':'node', 'type':'node'},
                ],


                # This section is important, it defines the wheels! The order in which the wheel are declared is important: each consecutive pair of wheel is grouped into an axle.
                'wheels':[
                    # radius (in meter)
                    {'name':'radius', 'type':'float'},
                    # width (in meter)
                    {'name':'width', 'type':'float'},
                    # number of rays
                    {'name':'raycount', 'type':'int'},
                    # the numbers of two existing nodes that defines the wheel axis (the second node must have a larger Z coordinate than the first)
                    {'name':'node1', 'type':'node'},
                    {'name':'node2', 'type':'node'},
                    # the number of a special rigidity node (see explanation about Axle Rigidity) or 9999 if it is not used
                    {'name':'rigidity node', 'type':'node'},
                    # is the wheel braked (1) or not (0) (for directional braking, as found in planes, use 2 for left wheel and 3 for right wheel)
                    {'name':'braked', 'type':'int'},
                    # is the wheel propulsed (1) or not (0)
                    {'name':'propulsed', 'type':'int'},
                    # the number of a reference arm node for this wheel. This is where reaction torque is applied to the chassis. Should be on the rotation axis of the suspension arm.
                    {'name':'arm node', 'type':'node'},
                    # mass of the wheel (in kg)
                    {'name':'mass', 'type':'float'},
                    # spring factor of the wheel : the stiffiness of the wheel
                    {'name':'spring', 'type':'float'},
                    # damp factor : the reboundiness of the wheel
                    {'name':'damp', 'type':'float'},
                    # face material and band material (and no quote between them) if you don't know, use "tracks/wheelface" for the face and "tracks/wheelband1" for single wheel or "tracks/wheelband2" for dual mounted wheels.
                    {'name':'material', 'type':'string'},
                ],


                # This define the position of the in-truck cam. It is a special node suspended to eight chassis nodes. The parameters are the 3 coordinates of the point and the 8 nodes numbers to which it is binded.
                'cinecam':[
                    {'name':'x', 'type':'float'},
                    {'name':'y', 'type':'float'},
                    {'name':'z', 'type':'float'},
                    {'name':'node1', 'type':'node'},
                    {'name':'node2', 'type':'node'},
                    {'name':'node3', 'type':'node'},
                    {'name':'node4', 'type':'node'},
                    {'name':'node5', 'type':'node'},
                    {'name':'node6', 'type':'node'},
                    {'name':'node7', 'type':'node'},
                    {'name':'node8', 'type':'node'},
                ],


                # This defines where the light flares will be. It is positionned relative to 3 nodes of the chassis. One node is the reference node, and the two others define a base (x,y). So the flare is in the plane defined by the 3 nodes, and is placed relative to the reference node by adding a fraction of the vectors ref->x and ref->y. The three first parameters are the 3 nodes numbers (rex,x,y) and the two next gives what amount of ref->x and ref->y to add to displace the flare point (these two should be logically between 0 and 1, or else that means you use the wrong base triangle and if the body flexes too much the flare will not stick to the body correctly).
                'flares':[
                    {'name':'ref node', 'type':'node'},
                    {'name':'x node', 'type':'node'},
                    {'name':'y node', 'type':'node'},
                    {'name':'offsetx', 'type':'float'},
                    {'name':'offsety', 'type':'float'},
                ],


                #This allows you to "stick" any 3D mesh to a triangle of points of a truck. You can use it to stick air intakes, horns, seats, dashboard, bumbers, whatever to the truck (note that there will be no collision detection of these objects). They work the same way as the flares. It is positionned relative to 3 nodes of the chassis. One node is the reference node, and the two others define a base (x,y). So the prop is positionned relative to the plane defined by the 3 nodes, and is placed relative to the reference node by adding a fraction of the vectors ref->x and ref->y. Additionnally, you can displace the prop along the normal to the plane. The three first parameters are the 3 nodes numbers (rex,x,y) and the three next gives what amount of ref->x, ref->y and normal to add to displace the prop (the first two should be logically between 0 and 1, or else that means you use the wrong base triangle and if the body flexes too much the flare will not stick to the body correctly, the third is normalized, in meter). The next 3 parameters are rotation angles to apply to the mesh (in each 3 axis), and the last is the name of an Ogre3D mesh object. Note that meshes with the name beginning with "dashboard", "leftmirror", "rightmirror", "seat", "beacon", "pale" and "spinprop" are reserved as they employ some magic to work. The first "seat" mesh is made translucent, so it should be the driver's seat.
                'props':[
                    {'name':'ref node', 'type':'node'},
                    {'name':'x node', 'type':'node'},
                    {'name':'y node', 'type':'node'},
                    {'name':'offsetx', 'type':'float'},
                    {'name':'offsety', 'type':'float'},
                    {'name':'offsetz', 'type':'float'},
                    {'name':'rotx', 'type':'float'},
                    {'name':'roty', 'type':'float'},
                    {'name':'rotz', 'type':'float'},
                    {'name':'mesh', 'type':'string'},
                ],


                #This last part defines the most visible part of the truck: the body. It will dress the chassis with solid triangles. You must define each body panel (a continuous almost-flat section) in a different submesh section, in order to have sharp body angles, and to simplify texturing. A submesh has two subsection: the texcoords, that places nodes of the submesh on the texture image (coordinates between 0.0 and 1.0) , and then the cab subsection, that draws the triangles, with triplets of node numbers. The nodes used in the cab subsection must be present in the texcoord subsection. The order in which the three points forming the triangles is given is important, as its winding defines in which direction it will be visible. The winding must be counterclockwise to be visible (IIRC). There is an optional flag to the cab subsection: if you add "c" to the triangle, this triangle will be a contact triangle, that can contact with contacters nodes. mcreed has contributed a cool Texturing Tutorial that describes how to fill the submesh and cab parts of the truck file. When the tag "backmesh" is added, the triangles backsides of the submesh will be black instead of see-through.
                'submesh':[
                    {'name':'groupno', 'type':'int'},
                ],
                'texcoords':[
                    {'name':'node', 'type':'node'},
                    {'name':'u', 'type':'float'},
                    {'name':'v', 'type':'float'},
                ],
                'cab':[
                    {'name':'node1', 'type':'node'},
                    {'name':'node2', 'type':'node'},
                    {'name':'node3', 'type':'node'},
                    {'name':'options', 'type':'string',
                                             'required':False,
                                             'default':None,
                                             'validvalues':[
                                                'c', # triangle will be a contact triangle
                                                'n', # normal
                                                'b', # buoy
                                                'D', # WHAT IS THIS?
                                            ]},
                ],


                # This section declares parts of the chassis as wings, and that they should bear aerodynamic forces. Each line of this section designs a wing segment, that is a homogeneous part of a wing. You can (and you should!) make a plane's wing from several contiguous wing segments. Rudder and elevators are also made with one or more wing segments. Each wing segment is bounded by 8 nodes, that defines the "bounding box" of the wing, specifically its span, chord and thickness. You must ensure that these nodes are properly interconnected by beams to ensure the structural integrity of the wing. Notice that it is VERY IMPORTANT to declare contiguous wing segments (i.e. that shares nodes) IN SEQUENTIAL ORDER FROM RIGHT TO LEFT, and you should avoid cutting a wing in two at the fuselage, but make the whole wing continuous across the fuselage because it helps to compute whole-wing effects like induced drag and other things like wing lights. A very important aerodynamic parameter is the wing airfoil. The airfoil is the tear-like shape of the wing, and its exact geometry is very important for the characteristics and performances of real-world wings. RoR uses precomputed performances curves from standard airfoils, interpolated from wing tunnel tests. These curves are stored in .afl files. Standard aifoils provided in RoR are:
                'wings':[
                    # Front left down node number
                    {'name':'front left down node', 'type':'node'},
                    # Front right down node number
                    {'name':'front right down node', 'type':'node'},
                    # Front left up node number
                    {'name':'front left up node', 'type':'node'},
                    # Front right up node number
                    {'name':'front right up node', 'type':'node'},
                    # Back left down node number
                    {'name':'back left down node', 'type':'node'},
                    # Back right down node number
                    {'name':'back right down node', 'type':'node'},
                    # Back left up node number
                    {'name':'back left up node', 'type':'node'},
                    # Back right up node number
                    {'name':'back right up node', 'type':'node'},
                    # Texture X coordinate of the front left of the wing (in the texture defined in "globals")
                    {'name':'texture x front left', 'type':'float'},
                    # Texture Y coordinate of the front left of the wing (in the texture defined in "globals")
                    {'name':'texture y front left', 'type':'float'},
                    # Texture X coordinate of the front right of the wing (in the texture defined in "globals")
                    {'name':'texture x front right', 'type':'float'},
                    # Texture Y coordinate of the front right of the wing (in the texture defined in "globals")
                    {'name':'texture y front right', 'type':'float'},
                    # Texture X coordinate of the back left of the wing (in the texture defined in "globals")
                    {'name':'texture x back left', 'type':'float'},
                    # Texture Y coordinate of the back left of the wing (in the texture defined in "globals")
                    {'name':'texture y back left', 'type':'float'},
                    # Texture X coordinate of the back right of the wing (in the texture defined in "globals")
                    {'name':'texture x back right', 'type':'float'},
                    # Texture Y coordinate of the back right of the wing (in the texture defined in "globals")
                    {'name':'texture y back right', 'type':'float'},
                    # Type of control surface: 'n'=none, 'a'=right aileron, 'b'=left aileron, 'f'=flap, 'e'=elevator, 'r'=rudder
                    {'name':'controltype', 'type':'string',
                            'default':'n',
                            'validvalues':[
                            'n', # none
                            'a', # right aileron
                            'b', # left aileron
                            'f', # flap
                            'e', # elevator
                            'r', # rudder
                        ]},
                    # Relative chord point at which starts the control surface (between 0.5 and 1.0)
                    {'name':'chord point', 'type':'float'},
                    # Minimum deflection of the control surface, in degree (negative deflection)
                    {'name':'minimum deflection', 'type':'float'},
                    # Maximum deflection of the control surface, in degree (positive deflection)
                    {'name':'maximum deflection', 'type':'float'},
                    # Airfoil file to use
                    {'name':'airfoil filename', 'type':'string'},
                ],


                # The turboprops section defines the turboprop engines, and makes the truck a plane! It is important that this section comes AFTER the props section, becauses it will use props (as in accessories) elements to make props (as in propeller) (does this even make sense?). The props elements used by the turboprop are four pale.mesh (propeller blades) and one spinprop.mesh (translucent rotating disc), all having the same reference node as the turboprop. Easy, eh? Notice that currently turboprop have always 4 blades. Each prop blade is associated to a blade tip node, and you must ensure the blade nodes are correctly interconnected with beams so it will spin freely around its axis, while maintaining a rigid prop disc. See how the Antonov is made.
                'turboprops':[
                    # Reference node number (center of the prop)
                    {'name':'reference node', 'type':'node'},
                    # Prop axis node number (back of the prop)
                    {'name':'axis node', 'type':'node'},
                    # Blade 1 tip node number
                    {'name':'blade1 node', 'type':'node'},
                    # Blade 2 tip node number
                    {'name':'blade2 node', 'type':'node'},
                    # Blade 3 tip node number
                    {'name':'blade3 node', 'type':'node'},
                    # Blade 4 tip node number
                    {'name':'blade4 node', 'type':'node'},
                    # Power of the turbine (in kW)
                    {'name':'power', 'type':'float'},
                    # Airfoil of the blades
                    {'name':'airfoil filename', 'type':'string'},
                ],


                # The fusedrag section helps the correct modelling of the fuselage contribution to the aerodynamic drag of a plane. It makes also possible to "mask" the aerodynamic contribution of an object loaded inside the plane. It models the fuselage as a big wing section, with an airfoil (usually a symmetrical airfoil like NACA0009). The parameters are:
                'fusedrag':[
                    # Number of the front-most node of the fuselage
                    {'name':'front-most node', 'type':'node'},
                    # Number of the rear-most node of the fuselage
                    {'name':'rear-most node', 'type':'node'},
                    # Approximate width of the fuselage
                    {'name':'width', 'type':'float'},
                    # Airfoil name
                    {'name':'airfoil filename', 'type':'string'},
                ],


                #WHAT IS THIS
                #i think the screw position?
                'screwprops':[
                   {'name':'node1', 'type':'node'},
                   {'name':'node2', 'type':'node'},
                   {'name':'node3', 'type':'node'},
                   {'name':'factor', 'type':'float'},
                ],

                'comments':[
                   {'name':'commenttext', 'type':'string'},
                   {'name':'isattached', 'type':'int'},
                ],
                }

    # tree of the actual file's data
    tree = None
    ### this will hold all comments
    comments = None

    links = [
        {}
    ]

    def argIsRequired(self, arg):
        # simple wrapper, because if not otherwise defined, everthing is required
        if arg.has_key('required'):
            return arg['required']
        return True

    def errorMsg(self, filename, lineno, sectionname, sectiontype, argname, line, msgold):
        argpath = "/%s/%s/%s" % (sectiontype, sectionname, argname)
        msg = "%20s:%04d %-30s | %-40s | %s" % \
            (os.path.basename(filename), int(lineno) + 1, argpath,
             msgold, line)

        lineobj = self.getLine(lineno)
        if not lineobj is None:
            if not 'errors' in lineobj.keys():
                lineobj['errors'] = []
            lineobj['errors'].append(msg)

        if not 'errors' in self.tree.keys():
            self.tree['errors'] = []
        self.tree['errors'].append({'data':line, 'originline':lineno, 'file':filename, 'section':argpath,'error':msgold, 'line':line})

        sys.stderr.write(msg+"\n")

    def findNode(self, nodeNum):
        if int(nodeNum) == 9999:
            return True
        if not 'nodes' in self.tree.keys():
            # no nodes section!
            sys.stderr.write("node-list not initialized!\n")
            return False
        for nodeobj in self.tree['nodes']:
            if 'type' in nodeobj:
                continue
            node = nodeobj['data']
            # WHAT IS THIS? strange negative node number!
            try:
                if int(node[0]) == abs(int(nodeNum)):
                    return True
            except:
                return False
        return False

    def addComment(self, section, comment, lineno, attached):
        if not 'comments' in self.tree.keys():
            self.tree['comments'] = []
        newcomment = {'data':[comment, attached], 'originline':lineno, 'section':section, 'type':'comment'}
        self.tree['comments'].append(newcomment)

    def parse(self, filename, verbose = True):
        self.filename = filename
        content = None
        try:
            infile = open(filename,'r')
            content = infile.readlines()
            infile.close()
        except:
            sys.stderr.write("error while reading file %s!\n" % filename)
            sys.exit(1)

        if content is None:
            sys.stderr.write("error while reading file!\n")
            sys.exit(1)
        if verbose:
            sys.stderr.write("processing file %s\n" % filename)
        self.tree = {'title':[]}
        actualsection = "title"
        prevsection = ""
        currentsubmesh = None
        self.tree['submeshgroups'] = []
        for lineno in range(0, len(content)):
            line = content[lineno]
            # strip line-endings
            line = line.strip()
            #print lineno, line
            if line.strip() == "":
                # add blank lines to comments
                self.addComment(actualsection, line, lineno, False)
                continue

            #split comments out first
            if line.find(';') != -1:
                line1 = line.split(';')
                if line1[0] != '':
                    line = line1[0]
                    self.addComment(actualsection, line1[1], lineno, True)
                else:
                    self.addComment(actualsection, line1[1], lineno, False)
                    continue

            # test for new section
            if line in self.sections.keys():
                prevsection = actualsection
                actualsection = line
                if not currentsubmesh is None and len(currentsubmesh['texcoords'])>0 and len(currentsubmesh['cab'])>0:
                    self.tree['submeshgroups'].append(currentsubmesh)
                    currentsubmesh = None
                if actualsection == 'submesh' and currentsubmesh is None:
                    currentsubmesh = {'texcoords':[],'cab':[],'type':'submeshgroup'}
                # check if section is in the tree already
                if not actualsection in self.tree.keys():
                    self.tree[actualsection] = []
                continue

            # extract arguments
            args = line.split(',')

            # format args to have correct datatypes
            for argnum in range(0,len(args)):
                args[argnum] = args[argnum].strip()

            # check arguments

            #check if it is a command
            argumentsection = None

            cmdcheck = args[0].split(' ')[0]
            if cmdcheck in self.commands.keys():
                #construct new set of arguments if there are some
                if len(args[0].split(' ')) > 1:
                    newargs = []
                    newargs.append(args[0].split(' ')[1])
                    for argnum in range(1, len(args)):
                        newargs.append(args[argnum])
                    args = newargs
                    #ok
                else:
                    # no other args except the command itself
                    args = []
                argumentsection = self.commands[cmdcheck]
                argumentsection_str = "command"
            else:
                argumentsection = self.sections[actualsection]
                argumentsection_str = "section"
            argumenttree = []
            for argnum in range(0, len(argumentsection)):
                if argnum >= len(args) and not self.argIsRequired(argumentsection[argnum]):
                    continue
                elif argnum >= len(args):
                    self.errorMsg(filename, lineno, actualsection, argumentsection_str,
                            argumentsection[argnum]['name'], line, "too less args(%d/%d)"%(len(args), len(argumentsection)))
                    break
                arg = args[argnum]
                try:
                    if argumentsection[argnum]['type'] == 'string' and type(arg) == type("") or \
        (argumentsection[argnum]['type'] == 'int' or argumentsection[argnum]['type'] == 'node')    and type(int(arg)) == type(1) or \
                        argumentsection[argnum]['type'] == 'float'  and type(float(arg)) == type(0.1):
                        #check not for valid values

                        #if argumentsection[argnum]['type'] == 'node':
                            # this is being checked later if everything is read in!
                        if argumentsection[argnum].has_key('validvalues') and argumentsection[argnum]['type'] == 'string':
                            #check string valid values

                            #continue on empty optionals
                            if not self.argIsRequired(argumentsection[argnum]) and arg.strip() == "":
                                continue

                            if arg not in argumentsection[argnum]['validvalues']:
                                self.errorMsg(filename, lineno, actualsection, argumentsection_str,
                                            argumentsection[argnum]['name'], line, "invalid value of argument: %s" % arg)
                        #print "type ok"
                        argumenttree.append(arg)
                        continue
                except:
                    self.errorMsg(filename, lineno, actualsection, argumentsection_str,
                                argumentsection[argnum]['name'], line, "invalid type of argument, or unkown command")
                    break
            if len(args) > len(argumentsection):
                self.errorMsg(filename, lineno, actualsection, argumentsection_str,
                            None, line, "too much args(%d/%d)"%(len(args), len(argumentsection)))

            #append caps and textcoords to submesh section
            if (actualsection == 'texcoords' or actualsection == 'cab') and not currentsubmesh is None:
                currentsubmesh[actualsection].append({'data':argumenttree, 'originline':lineno, 'section':actualsection})
                continue
            # append argument list to the tree
            if len(argumenttree) > 0 or argumentsection_str == 'command':
                if argumentsection_str == 'command':
                    # prepend command again
                    argumenttree.insert(0,str(cmdcheck))
                    self.tree[actualsection].append({'data':argumenttree, 'originline':lineno, 'section':actualsection,'type':'command'})
                else:
                    self.tree[actualsection].append({'data':argumenttree, 'originline':lineno, 'section':actualsection})
            continue
        #self.checkNodes()
        #self.checkForDoubleNodes()
        #self.checkForDoubleBeams()
        if verbose:
            sys.stderr.write("finished processing of file %s\n" % filename)
        #self.printtree()
        #self.linearizetree()
        #print self.tree['errors']
        #self.save()
        

    def save(self):
        #(fid, filename) = tempfile.mkstemp(suffix='.RoRObject')
        filename = self.filename + "_pickle"
        print "trying to save Settings to file %s for file %s" % (filename, os.path.basename(self.filename))
        try:
            fh = open(filename, 'w')
            pickle.dump(self.tree, fh)
            fh.close()
            print "saving successfull!"
        except:
            print "error while saving settings"


    def isFloat(self, s):
        try:
            i = float(s)
        except ValueError:
            i = None
        return i

    def printtree(self):
        for s in self.tree.keys():
            if len(self.tree[s]) == 0:
                continue
            print ""
            print "==========================================================================================================================================================================="
            print "%s: %d" % (s, len(self.tree[s]))
            # for non original columns (generated ones)
            if not self.sections.has_key(s):
                print self.tree[s]
                continue
            for column in self.sections[s]:
                sys.stdout.write("| %-15s" % (column['name'][0:15]))
            sys.stdout.write("\n")
            print "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------"
            for line in self.tree[s]:
                for arg in line['data']:
                    try:
                        if arg.isdigit() or self.isFloat(arg):
                            sys.stdout.write("|%15.3f " % (round(float(arg),4)))
                        else:
                            sys.stdout.write("|%15s " % (str(arg)[0:15]))
                    except:
                        sys.stdout.write("|%15s " % (str(arg)[0:15]))
                if 'errors' in line.keys():
                    sys.stdout.write("[ERRORS: %d] "%(len(line['errors'])))
                sys.stdout.write("(origin: %d)\n"%(line['originline']))

    def getLine(self, lineno):
        for skey in self.tree.keys():
            for lineobj in self.tree[skey]:
                if lineobj.has_key('originline') and lineobj['originline'] == lineno:
                    return lineobj
        return None

    def linearizetree(self):
        result = []
        n = self.tree['title'][0]
        actualsection = ""
        while (not n is None): 
            if n['section'] != actualsection:
                # add section title
                newsection = n['section']
                if not newsection in ['title']:
                    actualsection = newsection
                    if newsection == "texcoords":
                        result.append("submesh")
                    result.append(actualsection)

            data = ""
            #print n['data']
            if 'type' in n.keys() and n['type'] == 'comment':
                # wheter to prepend the comment char
                if n['data'][0].strip() == "":
                    data = n['data'][0]
                else:
                    data = ';'+n['data'][0]
            else:
                data = ", ".join(n['data'])
            result.append(data)
            n = self.getnextLine(n['originline'])
        
        for r in result:
            print r

    def getnextLine(self, lineno):
        value = {'originline':9999999999}
        for skey in self.tree.keys():
            for lineobj in self.tree[skey]:
                if lineobj['originline'] > lineno and lineobj['originline'] < value['originline']:
                    value = lineobj
        if value['originline'] != 9999999999:
            return value
        return None

    def checkNodes(self):
        # check every argument of each line for missing nodes
        for skey in self.tree.keys():
            if skey in ['node','errors']:
                #do not check itself!
                continue
            for lineobj in self.tree[skey]:
                if lineobj.has_key('type'):
                    continue
                line = lineobj['data']
                lineno = lineobj['originline']
                if len(line) > len(self.sections[skey]):
                    self.errorMsg(self.filename, lineno, skey, 'section',
                        '', line, "too much arguments!")
                    continue
                
                for argnum in range(0, len(line)):
                    if self.sections[skey][argnum]['type'] == 'node':
                        if not self.findNode(line[argnum]):
                            self.errorMsg(self.filename, lineno, skey, 'section',
                            self.sections[skey][argnum]['name'], line, "node: %s not found!" % str(line[argnum]))


    def checkForDoubleNodes(self):
        if not 'nodes' in self.tree.keys():
            # no nodes section!
            return False
        for node1obj in self.tree['nodes']:
            if node1obj.has_key('type'):
                continue
            node1 = node1obj['data']
            for node2obj in self.tree['nodes']:
                if node2obj.has_key('type'):
                    continue
                node2 = node2obj['data']
                if node1[0] == node2[0]:
                    #found itself
                    continue
                if str(node1) == str(node2):
                    sys.stderr.write("node %s and %s are the same!\n" % (node1[0], node2[0]))

    def checkForDoubleBeams(self):
        if not 'beams' in self.tree.keys():
            # no beams section!
            return False
        beamcounter1 = 0
        ignorebeams = []
        for beam1obj in self.tree['beams']:
            if beam1obj.has_key('type'):
                continue
            beam1 = beam1obj['data']
            beamcounter1 += 1
            if str(beam1) in ignorebeams:
                # already marked as duplicate
                continue
            beamcounter2 = 0
            for beam2obj in self.tree['beams']:
                if beam2obj.has_key('type'):
                    continue
                beam2 = beam2obj['data']
                beamcounter2 += 1
                if str(beam2) in ignorebeams:
                    # already marked as duplicate
                    continue
                try:
                    if beam1[0] == beam2[0] and beam1[1] == beam2[1]:
                        # found equal beam, check if it found itself
                        if beamcounter1 != beamcounter2:
                            ignorebeams.append(str(beam2))
                            self.errorMsg(self.filename,beam1obj['originline'],'beams','section','beam',
                            str(beam1obj['originline'])+": "+str(beam1)+", "+str(beam2obj['originline'])+": "+str(beam2),
                             "duplicate beam found: %s and %s"%( beamcounter1,beamcounter2))
                            continue
                    if beam1[0] == beam2[1] and beam1[1] == beam2[0]:
                        ignorebeams.append(str(beam1))
                        ignorebeams.append(str(beam2))
                        # found inverse beam
                        self.errorMsg(self.filename,beam1obj['originline'],'beams','section','beam',
                        str(beam1obj['originline'])+": "+str(beam1)+", "+str(beam2obj['originline'])+": "+str(beam2),
                        "inverse beam found: %s and %s" %(beamcounter1,beamcounter2))
                        continue
                except:
                    self.errorMsg(self.filename,beam1obj['originline'],'beams','section','beam', str(beam1)+", "+str(beam2), "error while checking beams")
                    continue

def main():
    p = rorparser()
    for argno in range(1,len(sys.argv)):
        p.parse(sys.argv[argno])
    #p.printtree()
    
if __name__ == '__main__':
    main()
