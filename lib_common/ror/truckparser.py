#!/bin/env python
# Thomas Fischer 16/05/2007 thomas (at) thomasfischer.biz
# Lepes update parser from latest wiki webpage (truck definition file latest update: 28 feb 2010

#author, forset and submesh doesn't work


import sys, os, os.path, tempfile, pickle

#import inspect
from string import capwords, lower
from types import *
from compiler.ast import Assert
from math import modf
from roreditor.RoRConstants import *
from ror.logger import log
#from ror.settingsManager import rorSettings
#from ror.rorcommon import *

	# default values: required:True
	# please note: unkown args are marked with 'WHAT IS THIS'


def getContent(filename):
	""" return a python list with each line in a different column
	
	ex: ['my Truck name', '', 'globals', '11000.0, 1000.0, MAZ206', ...]
	"""
	file = open(filename, 'r') 	
	content = file.readlines()
	file.close()
	return content

def saveContent(content, filename):
	""" supplying a python list and a valid filename will save the content 
	"""
	file = open(filename, 'w')
	file.writelines(content)
	file.close()
	
class lineOfSection(object):
	""" one line of a particular section of TDF is translate into a python object
	
	ror TDF:
		nodes
		;id	x	y	z
		0, 0.4, 1.0, 3, options
		
	is converted into:
	
	class lineOfSection(object)
		__init__(self):
			self.section = <actualsection> (string)
			self.isCommand = <True/False>  (boolean)
			
			self.id	= 0  			(int)
			self.x 	= 0.4			(float)
			self.y 	= 1.0			(float)
			self.z 	= 3.0			(float)
			self.options = <all letters> (string)
			self.inlineComment = <without semicolon>
	"""
	def __init__(self):
		self.columnIndex = []
		self.columnNames = {}
		self.parent = None #to access some properties of the parser
		self.inlineComment = ""
		self.isHeader = False #new section begin here
	
	def setSection(self, sectionName):
		parser = self.parent
		if parser.commands.has_key(sectionName):
			value = True
			columnlist = parser.commands[sectionName]
		elif parser.sections.has_key(sectionName):
			value = False
			if sectionName not in parser.truckSections: parser.truckSections.append(sectionName)
			columnlist = parser.sections[sectionName]
		else:
			idx = list_has_value(self.parser.sectionfooter, sectionName)
			if idx > -1:
				self.isHeader = True
				value = False
			else:
				raise Exception('%s is neither a valid command nor section nor sectionfooter' % sectionName)

		setattr(self, 'isCommand', value)
		setattr(self, 'section', sectionName)
		if not self.isHeader:
			if len(columnlist) > 0: #python list
				for i in range(len(columnlist)):
					if columnlist[i].has_key('name'):
						attrname = columnlist[i]['name'].replace(" ", "_") 
						self.columnIndex.append(attrname)
						self.columnNames[attrname] = i
						if columnlist[i].has_key('type'):
							if columnlist[i]['type'] == 'string' : attrvalue = ''
							elif columnlist[i]['type'] == 'int' : attrvalue = 0
							elif columnlist[i]['type'] == 'node': attrvalue = 0
							elif columnlist[i]['type'] == 'float' : attrvalue = 0.0
							elif columnlist[i]['type'] == 'shortcut' : attrvalue = 0
							else: attrvalue = None
						else : raise Exception('section %s column %d does not have a data type' % (sectionName, i))
						setattr(self, attrname, attrvalue)
					else: raise Exception('section %s column %d does not have a "name" dictionary key' % (sectionName, i))
				self.columnIndex.append('inlineComment')
				self.columnNames['inlineComment'] = len(self.columnIndex)

	def getDefinition(self, column= -1):
		""" return section definition
		if column is a valid column, it returns the Column definition instead
		"""
		if column == -1:
			return self.parent.sectionDef(self.section)
		else:
			return self.parent.getColOfSection(self.section, column) 
	
	def getColValue(self, idxOrName):
		""" try to get the value of the column passed in parameter
			idxOrName could be the index of the column or the name (with/out) spaces
		"""
		if isinstance(idxOrName, StringType):
			idx = self.getColIndex(idxOrName)
		elif isinstance(idxOrName, IntType):
			idx = idxOrName
		else: return None
			 	
		if idx >= len(self.columnIndex) : return None #raise Exception("index out of bounds in section %s. Accessing to index %d but the list has length of %d" % (self.section, idx, len(self.columnIndex)))
		return getattr(self, self.columnIndex[idx]) 

	def getColName(self, idx):
		return self.columnIndex[idx]
	
	def getMaxCols(self):
		return len(self.columnIndex)
	
	def getColIndex(self, attrName):
		""" return the columnIndex for the attrName
			attrName can contains spaces or not.
		"""
		copyname = attrName.replace(" ", "_")
		if not self.columnNames.has_key(copyname): raise Exception("%s is not a valid columnname for section %s" % (copyname, self.section))
		return self.columnNames[copyname]
	
	def getTruckLine(self):
		parser = self.parent
		if parser is None: parser = rorparser()
#		print "-- obj dictionary --"
#		for k, v in self.__dict__.iteritems():
#			print "key %s, value %s" % (k, v)
#		print "-- end dictionary --"
		if self.isCommand	: colsdef = parser.commands[self.section]  
		else				: colsdef = parser.sections[self.section]
		result = ""
		sep = ""
		if self.inlineComment == RWHEELS and self.section in ['nodes', 'beams']: return result
		prevSplittedSpace = False
		if self.isHeader:
			if parser.blankLineBeforeSection: result += '\n'
			result += self.section
		else : 
			for col in colsdef: #col is a dict inside colsdef python list
				format = None # delete previous col value ;)
				attrName = col['name'].replace(" ", "_")
				if not self.__dict__.has_key(attrName):
					raise Exception("lineOfSection doesn't have a needed attribute: %s" % attrName)
				value = self.__dict__[attrName]
				
				if isinstance(value, NoneType):
					format = None
				elif isinstance(value, IntType):
					if self.parent.formatOutput: format = "%10d"
					else: format = "%d"
				elif isinstance(value, FloatType):
					if self.parent.formatOutput: format = "%.3f"
					else: 
						format = "%.3f"
						str = format % value
						frac, number = modf(float(str))
						if frac == 0.0:
							format = "%0.0f"
				elif isinstance(value, StringType):
					format = "%s"
				else: raise Exception("type is not valid in lineOfSection. section %s, attrName %s \n line until now: %s" % (self.section, attrName, result))
				
				
				if format is not None:
					if result != "":
						if prevSplittedSpace: 
							sep = ' '
							prevSplittedSpace = False
						else:
							sep = ', '
	
					if col.has_key('splitspaces'): 
						prevSplittedSpace = col['splitspaces']
					result += sep + (format % value)

		if self.isCommand and not result.startswith(self.section): result = self.section + ' ' + result
		if self.inlineComment != "" and self.inlineComment is not None : result += ';' + self.inlineComment
		if self.parent.tabBeforeLine and not self.isHeader: result = '    ' + result
		return result
				
				
#------------------------------------------------------------------------------ 
# Lepes
# FIXME: some options separated by spaces should be cut i.e.: commands2 "options  description" ==> 'splitspaces':True
# FIXME: add default values to some sections to auto complete?? is it posible?
#------------------------------------------------------------------------------ 

managedMaterialEffect = ['flexmesh_standard', 'flexmesh_transparent', 'mesh_transparent', 'mesh_standard']


# shared with newterrain parser
Author_def = [
						{'name':'author', 'type':'string', 'splitspaces':True},
						  {'name':'author of', 'type':'string', 'splitspaces':True, 'help': 'author of what? recommended values: chassis, texture, support'},
						  {'name':'forum id', 'type':'int', 'splitspaces':True, 'help': 'id of the members forum account, so the user may write him a message'},
						  {'name':'author name', 'type':'string', 'splitspaces':True, 'help': 'name of the author'},
						  {'name':'author email', 'type':'string', 'splitspaces':True, 'restofline':True, 'help': 'email address of the author (this is optional and can be left out)',
																  'required':False}
				]

FileInfo_def = [
							# uniqueid: this field specifies the unique file ID (you get one by uploading it to the repository). -1 for none
						  {'name': 'fileinfo', 'type':'string', 'splitspaces':True},
						  {'name':'unique id', 'type':'string', 'help': 'this field specifies the unique file ID (you get one by uploading it to the repository). -1 for none'
						  },
						  {'name':'repository category', 'type':'int', 'help': 'this is the category number from the repository. -1 for none o you can find a list of valid numbers there: Truck Categories'
						  },
						  {'name':'file version', 'type':'int', 'help': 'this opens the possibility to update this mod. the version should be simple integers: 1 for version one, 2 for version two and so on. The version number is an integer number, so do not use character other than 0-9'
						  }
				]

set_beam_defaults = [
					# 
					{'name':'set beam defaults', 'type':'string', 'splitspaces':True, 'help': 'command to modify beams'
					},
					{'name':'spring constant', 'type':'float', 'help': 'Spring constant (use -1 for the default, which is 9000000)'
					},
					# 
					{'name':'damping constant', 'type':'float', 'required':False, 'help': 'Damping constant (use -1 for the default, which is 12000)'
					},
					# 
					{'name':'deformation threshold', 'type':'float', 'required':False, 'help': 'Deformation threshold constant (use -1 for the default, which is 400000)'},
					# 
					{'name':'breaking thresold', 'type':'float', 'required':False, 'help': 'Breaking thresold constant (use -1 for the default, which is 1000000)'},
					# 
					{'name':'beam diameter', 'type':'float', 'required':False, 'help': 'Beam diameter (use -1 for the default, which is 0.05)'},
					# 
					{'name':'beam material', 'type':'string', 'required':False, 'help': 'Beam material (default: tracks/beam)'},
				] 

set_skeleton_settings = [
							{'name': 'set skeleton settings', 'type':'string', 'splitspaces':True},
							{'name': 'sight range', 'type':'float', 'help': 'visible distance'}, #
						 	{'name': 'beam diameter', 'type':'float', 'help': 'beam width in meters', 'required':False}# 
						]

rollon = [
			{'name':'rollon', 'type':'string', 'required': False, 'help': ' Enables collision between wheels and the textured surfaces of a truck'}
		  ]
forwardcommands = [
					{'name':'forwardcommands', 'type':'string', 'help': ' Forwards the commandkeys pressed while riding a truck to loads in close proximity. It is used to remote control the commands of a load. The load must have the "importcommands" tag.'}
					]
backmesh = [
			{'name':'backmesh', 'type':'string', 'required': False, 'help': 'the triangles backsides of the submesh will be black instead of see-through.'}
		]
importcommands = [
					{'name':'importcommands', 'type':'string', 'required': False, 'help': 'Enables a load to receive commandkeys from a manned vehicle in close proximity. The controlling vehicle must have the "forwardcommands" tag. The load only receives the keys that are pressed by the player, it must contain a commands section. Commands section for loads is defined in the same manner as in manned trucks.'}
				]
rescuer = [
			{'name':'rescuer', 'type':'string', 'required': False, 'help': 'This truck is a rescuer. Whenever ingame user press "R" key, RoRbot will be teletransported to this truck'}
			]
end = [
		{'name':'end', 'type':'string', 'required': False, 'help': 'End of truck file'}
		]
fileformatversion = [
						{'name':'fileformatversion', 'type':'string', 'splitspaces':True},
						  {'name':'version', 'type':'int',
															'default':'2',
															'validvalues':[
																			'1', # pre 0.32
																			'2', # post 0.32
																			'3'  # post 0.36
																		   ]
															}
				]
enable_advanced_deformation = [
							{'name':'enable advanced deformation', 'type': 'string', 'required':False, 'help': 'Use this only once per truck file, its a general activation and setting of advanced beam physics . Its recommended to place the enable_advanced_deformation before the first beams section in your truck-file.'}
							] 
# used on nodes section and set_node_defaults
node_options_dictionary = 					{'name':'options', 'type':'string',
											  'splitspaces':True,
											 'required':False,
											 'default':'n',
											 'validmultiplevalues':[
												{'name':'normal', 'option':'n', 'help': 'normal node, nothing special'},
												{'name':'cargo load', 'option':'l', 'help':'this node bears a part of the cargo load'},
												{'name':'friction', 'option':'f', 'help':'this node has extra friction with the ground (usefull for feets)'},
												{'name':'exhaust', 'option':'x', 'help':'this node is the exhaust point (requires a "y" node)'},
												{'name':'ref exhaust', 'option':'y', 'help': 'exhaust reference point, this point is at the opposite of the direction of the exhaust'},
												{'name':'no ground contact', 'option': 'c', 'help':'this node will not detect contact with ground (can be used for optimization, on inner chassis parts)'},
												{'name':'hook point', 'option':'h', 'help':'this node is a hook point (e.g. the extremity of a crane)'},
												{'name':'editor', 'option': 'e', 'help':'this node is a terrain editing point (used in the terrain editor truck)'},
												{'name':'buoyancy', 'option': 'b', 'help':'this node is assigned an extra buoyancy force (experimental)'}
											
											]}
uhoh = 'huh?..oh!'

class rorparser(object):
	# This specifies all valid commands
	sectionfooter = [{'comment':'end_comment'},
					 {'description':'end_description'}
					]
	commands = {
				# set_beam_defaults changes the beams (but also the hydros and ropes) default characteristics that will be used for the beams declared after the line. You can use this line many times to make different groups of beams that have different characteristics (e.g. stronger chassis, softer cab, etc.). This method is better than the globeams command that is now deprecated. The parameters comes on the same line, after set_beam_defaults. You can use the first parameters (most usefull) and safely ignore the last parameters.
				'set_beam_defaults': set_beam_defaults,
				'set_skeleton_settings':set_skeleton_settings,
				'rollon':rollon,
				'forwardcommands':forwardcommands,
				'importcommands':importcommands,
				'rescuer':rescuer,
				# end of file
				'backmesh':backmesh,
				'end':end,
				# begin Lepes  
				'author':Author_def,
				'fileformatversion': fileformatversion,
				'disabledefaultsounds':[{'name':'disable defaults sounds', 'type':'string', 'required':False}],
				'fileinfo':FileInfo_def,
				'set_node_defaults':[
					{'name':'set node defaults', 'type':'string', 'splitspaces':True},
					{'name':'load weight', 'type':'float'},
					{'name':'friction', 'type':'float'},
					{'name':'volume', 'type':'float'},
					{'name':'surface', 'type':'float'},
					node_options_dictionary
				],

				# this line MUST be after flexbodies 
				'forset':[
						{'name':'forset', 'type':'string'},
						{'name':'node list', 'type':'string', 'restofline':True} # Behind the word forset, you declare all nodes used for the deformation of the mesh (ranges are supported). These nodes should be outer nodes of the vehicle, those that are close to the mesh. 
				],

				';':[
						{'name':';', 'type':'string'},
						{'name':'comment line', 'type':'string'}
				]
				
				# end Lepes
	}
	
	### This specifies all valid sections und subsections
	sections = {
				uhoh: [
						{'name':'unknown line', 'type':'string', 'restofline':True}
				],
				# 
				'title':[
					{'name':'title', 'type':'string', 'help': 'This section is the only that is not introduced by a keyword. It is the name of the truck, and it must absolutely be the first line of the file. e.g.'}
				],
				'description': [
							{'name':'description', 'type':'string', 'required':False, 'hasfooter':True, 'help':'Description of the truck, only the first 3 lines will be shown on HUD'},
							{'name':'full text', 'type':'string', 'required':False, 'restofline':True}
				],
				# This section is very special and should not be used for most designs. It was created to make the bridge. It allows you to alter the default mechanical and visual beam properties. 				The parameters are: default stress at which beams deforms (in Newtons), default stress at which beams break, default beams diameter (in meter), default beams material. This section is deprecated and should not be used for truck designs. Use the more powerfull set_beam_defaults instead.
				'globals':[
					{'name':'dry mass', 'type':'float', 'help': 'The weight RoR will try to give the truck (affected by minimum node weight, see below). Weight is measured in kilograms '},
					{'name':'cargo mass', 'type':'float', 'help': 'mass of the nodes marked "l" '},
					{'name':'material', 'type':'string', 'help':'The name of the material that will be used to texture the truck. This must be one of the material names specified in the material files. One of the existing materials can be used if you do not have your own material for the truck '}
				],
				'soundsources':[
					{'name':'node number', 'type':'node', 'help':'node number (the place where your sound will com from)'},
					{'name':'sound file name', 'type':'string', 'help':'sound script name. Sound scripts are defined in soundscript files. You can use game-defined sound scripts or your own sound scripts'}
				],
				# This section is very special and should not be used for most designs. It was created to make the bridge. It allows you to alter the default mechanical and visual beam properties. The parameters are: default stress at which beams deforms (in Newtons), default stress at which beams break, default beams diameter (in meter), default beams material. This section is deprecated and should not be used for truck designs. Use the more powerfull set_beam_defaults instead.
				# 
				'globeams':[
					#default stress at which beams deforms (in Newtons)
					{'name':'deform', 'type':'float', 'help': 'deprecated section since set_beam_defaults'},
					#default stress at which beams break
					{'name':'break', 'type':'float'},
					#default beams diameter (in meter)
					{'name':'diameter', 'type':'float'},
					#default beams material
					{'name':'material', 'type':'string'}
				],


				# The engine section contains the engine parameters.
				'engine':[
					{'name':'min rpm', 'type':'float', 'help':'The engine speed in which the automatic transmission downshifts and the clutch engages. '},
					{'name':'max rpm', 'type':'float', 'help':'The engine speed in which the automatic transmission upshifts. Actual redline is +20 percent rpm. '},
					#torque (!
					{'name':'torque', 'type':'float', 'help': 'Torque - A number representing the "torque" of the engine. The higher the value, the faster a truck will accelerate. RoR uses a Flat torque model, usually correct for large intercooled turbo diesels. The units of torque are in Newton*Meters (N*m)'},
					#differential ratio ()
					{'name':'differential ratio', 'type':'float', 'help': 'a global gear conversion ratio'},
					{'name':'rear gear', 'type':'float'},
					# Lepes : neutral gear missing why?
					{'name':'neutral gear', 'type':'float'},
					{'name':'first gear', 'type':'float'},
					{'name':'second gear', 'type':'float'},
					{'name':'third gear', 'type':'float', 'required':False},
					{'name':'fourth gear', 'type':'float', 'required':False},
					{'name':'fifth gear', 'type':'float', 'required':False},
					{'name':'sixth gear', 'type':'float', 'required':False},
					{'name':'seventh gear', 'type':'float', 'required':False},
					{'name':'eighth gear', 'type':'float', 'required':False},
					{'name':'nineth gear', 'type':'float', 'required':False},
					{'name':'tenth rpm', 'type':'float', 'required':False},
					{'name':'eleventh rpm', 'type':'float', 'required':False},
					{'name':'twelveth rpm', 'type':'float', 'required':False},
					{'name':'thirteenth rpm', 'type':'float', 'required':False},
					{'name':'fourteenth rpm', 'type':'float', 'required':False},
					{'name':'fifteenth rpm', 'type':'float', 'required':False},
					{'name':'sixteenth rpm', 'type':'float', 'required':False},
					#The last gear must be followed by a -1 value.
					{'name':'ending argument', 'type':'float', 'required':False}
				],

				# Engoption sets optional parameters to the engine, mainly for car engines. Parameters are:
				'engoption':[
					# Engine inertia: 
					{'name':'Engine inertia', 'type':'float', 'help': 'the default game value is 10.0, which is correct for a large diesel engine, but for smaller engines you might want smaller values, like 1.0 or 0.5 for small athmospheric engines.'},

					# Engine type: .
					{'name':'Engine type', 'type':'string',
								   		 	 'help': 'valid types are t for truck engine and c for car engine. This changes engine sound and other engine characteristics',
											 'validvalues':[
												'c', 	# car engine
												't', 	# truck engine
											]},
					{'name':'clutch force', 'type':'float', 'required': False},
					{'name':'shift time', 'type':'float', 'required': False},
					{'name':'clutch time', 'type':'float', 'required': False},
					{'name':'post shift time', 'type':'float', 'required': False}
				],


				# 
				'brakes':[
					# braking force
					{'name':'braking force', 'type':'float', 'help': 'This allows you to change the default braking force value (the default is 30000), generally to a lower value for smaller trucks and cars.'}
				],

#				'set_beam_defaults': set_beam_defaults,
#				'set_skeleton_settings':set_skeleton_settings,
#				'rollon':rollon,
#				'forwardcommands':forwardcommands,
#				'importcommands':importcommands,
#				'rescuer':rescuer,
#				'enable_advanced_deformation': enable_advanced_deformation,

				# With this section begins the structural description. Each line defines a node. The first parameter is . The three following parameters are the x,y,z coordinates, in meter. You can attach an optional option to a node by adding a single character. Recognized options are:
				'nodes':[
					{'name':'id', 'type':'node', 'help': 'the node number, and must absolutely be consecutive'},
					{'name':'x', 'type':'float', 'help': 'the x coordinate'},
					{'name':'y', 'type':'float', 'help': 'the y coordenate'},
					{'name':'z', 'type':'float', 'help': 'the z coordenate'},
					node_options_dictionary,
					{'name':'kg node', 'type':'float', 'required':False}
				],

				# This section is important. It helps to position the truck in space, by defining a local direction reference. For example this is used to measure the pitch and the roll of the truck. The three parameters are node numbers (defined in the next section). 
				'cameras':[
					# The first if the reference and may be anywhere, the second must be behind the first (if you look at the front of the truck, it is hidden behind the first),  
					{'name':'center node', 'type':'node', 'help': 'the reference and may be anywhere'},
					# 
					{'name':'back node', 'type':'node', 'help': 'The second must be behind the first (if you look at the front of the truck, it is hidden behind the first)'},
					# The third 
					{'name':'left node', 'type':'node', 'help': 'must be at the left of the first (if you look to the right of the truck, it is hidden by the first)'}
				],


				# .
				'fixes':[
					# node number that you want to fix.
					{'name':'node', 'type':'node', 'help': 'Fixes are nodes that are fixed in place. That means that once put in place in the terrain, they will never move, whatever happens. This is usefull to make fixed scenery elements from beams, like bridges. Just add the node number that you want to fix'}
				],


				# This section  There is an optional 3rd parameter, composed of a single character.
				'beams':[
					{'name':'first node', 'type':'node', 'help': 'defines all the beams connecting nodes. Each line describes a beam. The two first parameters are the node number of the two connected nodes. Order has no importance.'},
					{'name':'second node', 'type':'node'},
					{'name':'options', 'type':'string',
											 'required':False,
											 'default':'n',
											 'help': 'an optional parameter, composed of a single character.',
											 'validmultiplevalues':[
												{'name':'visible', 'option':'n', 'help':'visible, default'},
												{'name':'visible 2', 'option':'v', 'help': 'visible, default'},
												{'name':'invisible', 'option':'i', 'help':'this beam is invisible. Very usefull to hide "cheating" structural beam, or to improve performances once the truck is textured.'},
												{'name':'is rope', 'option': 'r', 'help':'this beam is a rope (opposes no force to compression)'}
											]}
				],

				#Exhausts
				'exhausts':[
							{'name':'ref node', 'type':'node'},
							{'name':'direction node', 'type':'node', 'help': 'The direction node is behind the ref node'},
							{'name':'factor', 'type':'int', 'splitspaces':True, 'help': 'The factor should be one, as it is not used yet'}, # Lepes asks: wiki says it is not used yet, and should be 1 !!
							{'name':'material', 'type':'string', 'help': ' The material should be "default" or any other custom created one. (You could create your own particle emitter based on the default one: data / smoke.particle)'} # material
				],
				
				#GuideSettings: By using this section you can set some parameters of the Truck GUI. This can be helpful if you're building a vehicle that has a relatively higher or lower speed than average. 
				'guisettings':[
							{'name':'gui settings', 'type': 'string'}
							],
				'tachoMaterial':[
								 {'name':'tachoMaterial', 'type': 'string', 'splitspaces':True},
								 {'name':'material', 'type':'string' , 'help': 'The name of the tachometer face (must be defined in a material file). Default: tracks/Tacho'}
				],
				'speedoMaterial':[
								 {'name':'speedoMaterial', 'type': 'string', 'splitspaces':True},
								 {'name':'material', 'type':'string', 'help': 'The name of the speedometer face (must be defined in a material file). Default: tracks/Speedo'}
				],
				'speedoMax':[
								 {'name':'speedoMax', 'type': 'string', 'splitspaces':True},
								 {'name':'max value', 'type':'float', 'help': 'The highest number that is on the speedometer (values 10-32000) Speedometer needle goes from -140 degree to 140 degree. Default: 140 (kph)'}
				],
				'useMaxRPM':[
								 {'name':'useMaxRPM', 'type': 'string', 'splitspaces':True},
								 {'name':'use max rpm', 'type':'integer', 'help': 'Whether or not to use the max rpm (in the engine section) as the highest number on the tachometer. Note that your actual max rpm is MaxRPM +20 percent. Do not include the 20 percent on your tachometer or it will be inaccurate. Tachometer needle is from -120 degree to 120 degree. Default is 0 (off).'}
				],
				#(>0.36) interactiveOverviewMap - enables / disables the activation of the interactive map for the truck. possible arguments: off, simple, zoom 
				'interactiveOverviewMap':[
								{'name':'interactiveOverviewMap', 'type':'string', 'required':True, 'help': 'enables / disables the activation of the interactive map for the truck'},
								{'name':'value', 'type':'string', 'required':False, 'validvalues':['off', 'simple', 'zoom']}
				],
				
				# (>0.36) debugBeams : enables certain beam/node debug options for the truck. Valid options:
				'debugBeams':[
								{'name':'debugBeams', 'type':'string', 'required':True, 'splitspaces':True},
								{'name':'node - numbers', 'type':'string', 'required':False, 'help': 'node - numbers : displays labels with node numbers'},
								{'name':'beam - numbers', 'type':'string', 'required':False, 'help': 'beam - numbers : displays labels with beam numbers'},
								{'name':'node - and - beam - numbers', 'type':'string', 'required':False, 'help': 'node - and - beam - numbers : both node and beam ids'},
								{'name':'node - mass', 'type':'string', 'required':False, 'help': 'node - mass : node mass in kg'},
								{'name':'node - locked', 'type':'string', 'required':False, 'help': 'node - locked : node locked?'},
								{'name':'beam - compression', 'type':'string', 'required':False, 'help': 'beam - compression : compression of the beam'},
								{'name':'beam - broken', 'type':'string', 'required':False, 'help': 'beam - broken : displays if a beam is broken, if not, displays nothing'},
								{'name':'beam - stress', 'type':'string', 'required':False, 'help': 'beam - stress : displays stress of a beam'},
								{'name':'beam - strength', 'type':'string', 'required':False, 'help': 'beam - strength : displays strength of a beam'},
								{'name':'beam - hydros', 'type':'string', 'required':False, 'help': 'beam - hydros : displays hydro position'},
								{'name':'beam - commands', 'type':'string', 'required':False, 'help': 'beam - commands : displays commands position'}
				], 				
				# end guidesettings

				# Shocks can be seen as tunable beams, useful for suspensions.
				'shocks':[
					# the two nodes connected by the shock
					{'name':'first node', 'type':'node', 'help': 'The node where the shock starts.'},
					{'name':'second node', 'type':'node', 'help': 'The node where the shock ends'},
					# spring rate: the stiffness
					{'name':'spring rate', 'type':'float', 'help': ' the stiffness off the shock. The higher the value, the less the shock will move for a given bump.'},
					# to adjust the amount of rebound: the best value is given by 2*sqrt(suspended mass*spring)
					{'name':'dampening', 'type':'float', 'help': ' The resistance to motion of the shock. The best value is given by 2 * sqrt(suspended mass * spring)'},
					# shortbound, longbound: defines the amount of deformation the shock can support (beyond, it becomes rigid as a standard beam) when shortened and lengthened
					{'name':'shortbound', 'type':'float', 'help': 'The shortest length the shock can be, as a proportion of its original length. (0) means the shock will not be able to contract at all, (1) will let it contract all the way to zero length. If the shock tries to shorten more than this this value allows, it will become as rigid as a normal beam'},
					{'name':'longbound', 'type':'float', 'help': 'The longest length a shock can be, as a proportion of its original length. (0) means the shock will not be able to extend at all. (1) means the shock will be able to double its length. Higher values allow for longer extension.'},
					# allows to compress or depress the suspension (leave it to 1.0 for most cases).
					{'name':'precomp', 'type':'float', 'help': 'Changes compression or extension of the suspension when the truck spawns. This can be used to level the suspension of a truck if it sags in game (1.0 is the default'},
					# You can make the shocks stability-active with optional parameters:
					{'name':'options', 'type':'string',
											 'required':False,
											 'default':None,
											 'validvalues':[
												{'option':'n', 'help':'normal'},
												{'option':'l', 'help':'to make a left-hand active shock'},
												{'option':'r', 'help':'to make a right-hand active shock'},
												{'option':'i', 'help':'to make the shock invisible (AVAILABLE FROM VERSION 0.29)'}
											]}
				],


				# 
				'hydros':[
					# two node numbers
					{'name':'first node', 'type':'node', 'help': 'The hydros section concerns only the direction actuactors ! They are beams that changes of length depending on the direction command.'},
					{'name':'second node', 'type':'node'},
					# lenghtening factor 
					{'name':'lenghtening factor', 'type':'float', 'help': '(negative or positive depending on wether you want to lenghten or shorten when turning left or the contrary)'},
					# optional flags
					{'name':'options', 'type':'string',
											 'required':False,
											 'default':None,
											 'validmultiplevalues':[
												{'name':'high speed', 'option':'s', 'help': 'disables the hydro at high speed (as seen sometimes with rear steering axles on large trucks)'},
												{'name':'normal', 'option': 'n', 'help':'normal node'},
												{'name':'invisible', 'option':'i', 'help':'make the hydro invisible'}
											]
					}
				],


				# The commands section 
				'commands':[
					{'name':'first node', 'type':'node', 'help': 'describes the "real" hydros, those you command with the function keys. They are like beams, but their length varies depending with the function keys you press.'},
					{'name':'second node', 'type':'node'},
					{'name':'speed rate', 'type':'float', 'help': '(how fast the hydro will change length)'},
					{'name':'shortest length', 'type':'float', 'help': 'the shortest length (1.0 is the startup length)'},
					{'name':'longest length', 'type':'float', 'help': 'the longest length (1.0 is the startup length)'},
					{'name':'shortening key', 'type':'shortcut', 'help': 'the number of the shortening function key (between 1 and 48)'},
					{'name':'lengthtening key', 'type':'shortcut', 'help': 'the number of the lengthtening function key (between 1 and 48)'},
					{'name':'options', 'type':'string',
											 'required':False,
											 'default':None,
											 'help': 'optional flags',
											 'validvalues':[
												'i', # make the hydro invisible.
												'r', # makes the command behave like a rope or a winch (no compression strength)
												'n', # should be used as a filler when a description field is needed
												'v', # WHAT IS THIS
											]},
					{'name':'description text', 'type':'string', 'required':False, 'help': 'A text description that tells the user what the command beam does when the it is activated. There is no need to put a key in front of the text (like F1:_do_something) this will be done automatically ! '}
					
				],

				# The commands2 section is an improved commands section. Its main differences: 
				'commands2':[
					# two node numbers
					{'name':'first node', 'type':'node', 'help': 'The node where the command beam starts'},
					{'name':'second node', 'type':'node', 'help': ' The node where the command beam ends'},
					# rate short
					{'name':'rate short', 'type':'float', 'help': 'How fast the command beam shortens'},
					# rate long
					{'name':'rate long', 'type':'float', 'help': ' How fast the command beam lengthens'},
					# short (1.0 is the startup length)
					{'name':'short', 'type':'float', 'help': 'Maximum contraction - The shortest length that the command beam will try to be, as a proportion of its startup length'},
					# long
					{'name':'long', 'type':'float', 'help': 'Maximum extension - The longest length the command beam will try to be, as a proportion of its startup length'},
					# the number of the shortening function key (between 1 and 48)
					{'name':'shortening key', 'type':'shortcut', 'help': 'A number representing the function key needed to compress the command beam. More than one can be controlled with the same key'},
					# the number of the lengthtening function key (between 1 and 48)
					{'name':'lengthtening key', 'type':'shortcut', 'help': ' The key used to extend the command beam.'},
					# optional flags
					{'name':'options', 'type':'string',
											 'required':False,
											 'default':None,
											 'splitspaces':True,
											 'validmultiplevalues':[
												{'name':'invisible', 'option': 'i', 'help':'make the hydro invisible.'},
												{'name':'as rope', 'option':'r', 'help':'makes the command behave like a rope or a winch (no compression strength)'},
												{'name':'description suplied', 'option':'n', 'help':'should be used as a filler when a description field is needed'},
												{'name':'unknown', 'option':'v', 'help':'WHAT IS THIS ! ?'},
												{'name':'auto center', 'option':'c', 'help':'auto centering command: the command beam will try to center back to its middle length, if no key is pressed'}, 	
												{'name':'no RPM', 'option':'f', 'help':'force restricted command: the Engine RPM will not increase the ratio of the command over 100 % (as it is the normal usecase)'},
												{'name':'press once', 'option':'p', 'help':'press once command: the command function key has only to be pressed once. The command will fully extend into the pressed direction. Another Keypress of the same direction stops the automatic movement.'},
												{'name':'three states', 'option':'o', 'help': 'press once command with center position: like the p option, but it will stop in the middle. (like a 3 way switch)'} 
											]},
					{'name':'description text', 'type':'string', 'required':False, 'splitspaces':True, 'help': 'A text description that tells the user what the command beam does when it is activated. There is no need to put a key in front of the text (like F1:_do_something): this will be done automatically ! . Note that there is no comma between the option flags and the description'},
					{'name':'start delay', 'type':'float', 'required':False},
					{'name':'stop delay', 'type':'float', 'required':False},
					{'name':'start function', 'type':'string', 'splitspaces':True, 'required':False},
					{'name':'stop function', 'type':'string', 'splitspaces':True, 'required':False}
					
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
					{'name':'left key', 'type':'shortcut'},
					# the number of the right key (between 1 and 12)
					{'name':'right key', 'type':'shortcut'}
				],


				# The contacters section lists the nodes that may contact with cab triangle. This concerns only contacts with other trucks or loads. You can easily omit this section at first.
				'contacters':[
					#node that may contact with cab triangle
					{'name':'node', 'type':'node'}
				],

				# The help section gives the name material used for the help panel on the dashboard. This material must be defined elsewhere in the MaterialFile. This is optional.
				'help':[
					{'name':'dashboard material', 'type':'string'}
				],


				# Ropes are special beams that have no compression strength (they can shorten easily) but have standard extension strength, like a cable or a chain. They have also another particularity: the second node can "grab" the nearest reachable ropable node with the 'O' key. Standard use is to use a chassis node as the first node, and a "free" node as the second node (free as in not attached by any other beam). The best example of this are the chains of the multibennes truck.
				'ropes':[
					{'name':'first node', 'type':'node'},
					{'name':'second node', 'type':'node'}
				],
				
				#Minimass :This sets the minimum node mass. Usefull for very light vehicles with lots of nodes (e.g. small airplanes). 
				'minimass':[{'name':'min mass', 'type':'float'}
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
												'n', # make visible
											]},
					{'name':'maxforce', 'type':'float', 'required':False} #(optional) the force (in Newtons) when the ties stop to shorten. Default is 12000.
				],


				# This section lists the nodes that can be catched by ropes or ties. Good use is to define some ropable nodes at the front and back of the truck to allow towing the truck.
				'ropables':[
					{'name':'rope node', 'type':'node'},
					{'name':'group', 'type':'int', 'required':False},
					{'name':'multilock', 'type':'int', 'required':False}
				],

				# particles: This enables/disables a particle cannon in the game (use the 'G' key).
				'particles':[
							 {'name':'source', 'type':'node'},
							 {'name':'back ref', 'type':'node'},
							 {'name':'particle system', 'type':'string'}
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
					# is the wheel propulsed (1) or not (0); (2) for wheels driven backwards
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
					{'name':'face material', 'type':'string', 'splitspaces':True, 'default':'tracks/wheelface', 'help':'face material', },
					{'name':'band material', 'type':'string', 'default':'tracks/wheelband1', 'help':'"tracks/wheelband1" for single wheel or "tracks/wheelband2" for dual mounted wheels'}
				],
				# This section improves wheels by simulating both wheel tyres and rims. The player is able to set tire pressure via key input. 
				'wheels2':[
					# Rim radius - The radius of the wheel rim
					{'name':'rim raius', 'type':'float'},
					# Tyre radius - The radius of the tyre, measured from the centre of the wheel.
					{'name':'tyre radius', 'type':'float'},
					# Width - This value has been ignored since 0.32, but is still required for compatibility reasons. Wheels now occupy the full distance between node1 and node2.
					{'name':'width', 'type':'float'},
					# Number of rays - The number of 'pie pieces' that make up the wheel. (3) makes thw wheel triangular abd (4) makes the wheel square. Recommended values are between 10 and 16.
					{'name':'raycount', 'type':'float'},
					# Node 1 - The node where the wheel starts
					{'name':'node1', 'type':'node'},
					# Node 2 - The node where the wheel ends
					{'name':'node2', 'type':'node'},
					# Rigidity Node - The number of a special rigidity node (see explanation about Axle Rigidity). Use (9999) if there is no rigidity node.
					{'name':'rigidity node', 'type':'node'},
					# Wheel Braking - (0) for unbraked wheels, (1) for brakes wheels. For directional braking, as found in the planes, use (2) for a left wheel and (3) for a right wheel.
					{'name':'braked', 'type':'int'},
					# is the wheel propulsed (1) or not (0); (2) for wheels driven backwards
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
					{'name':'material', 'type':'string'}
				],
				#Mesh wheels allows you to do very nice wheels. It takes an Ogre3D mesh 
				'meshwheels':[
					# Tyre radius - The radius of the tyre, measured from the centre of the wheel.
					{'name':'tyre radius', 'type':'float'},
					# Rim radius - The radius of the wheel rim
					{'name':'rim radius', 'type':'float'},
					# Width - This value has been ignored since 0.32, but is still required for compatibility reasons. Wheels now occupy the full distance between node1 and node2.
					{'name':'width', 'type':'float'},
					# Number of rays - The number of 'pie pieces' that make up the wheel. (3) makes thw wheel triangular abd (4) makes the wheel square. Recommended values are between 10 and 16.
					{'name':'raycount', 'type':'int'},
					# Node 1 - The node where the wheel starts
					{'name':'node1', 'type':'node'},
					# Node 2 - The node where the wheel ends
					{'name':'node2', 'type':'node'},
					# Rigidity Node - The number of a special rigidity node (see explanation about Axle Rigidity). Use (9999) if there is no rigidity node.
					{'name':'rigidity node', 'type':'node'},
					# Wheel Braking - (0) for unbraked wheels, (1) for brakes wheels. For directional braking, as found in the planes, use (2) for a left wheel and (3) for a right wheel.
					{'name':'braked', 'type':'int'},
					# is the wheel propulsed (1) or not (0); (2) for wheels driven backwards
					{'name':'propulsed', 'type':'int'},
					# the number of a reference arm node for this wheel. This is where reaction torque is applied to the chassis. Should be on the rotation axis of the suspension arm.
					{'name':'arm node', 'type':'node'},
					# mass of the wheel (in kg)
					{'name':'mass', 'type':'float'}, 	
					# spring factor of the wheel : the stiffiness of the wheel
					{'name':'spring', 'type':'float'},
					# damp factor : the reboundiness of the wheel
					{'name':'damp', 'type':'float'},
					# side l = left, r = right
					{'name':'side', 'type':'string', 'validvalues':['l', 'r']},
					# meshname
					{'name':'meshname', 'type':'string', 'splitspaces':True},
					# face material and band material (and no quote between them) if you don't know, use "tracks/wheelface" for the face and "tracks/wheelband1" for single wheel or "tracks/wheelband2" for dual mounted wheels.
					{'name':'material', 'type':'string', 'splitspaces':True}
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
					# default spring 8000
					{'name':'spring', 'type':'float', 'required':False},
					# default damping 8000
					{'name':'damping', 'type':'float', 'required':False}
				],

				#Rigidifiers: Rigidifiers enforces the relative angle of two interconnected beams. Say you have three nodes: a, b, c with two beams "ab" and "bc". This operator applied to a,b,c will have a similar effect of trussing with an "ac" beam, but it will work in any configuration, including if a,b,c are aligned. 
				'rigidifiers':[
							   {'name':'node1', 'type':'node'},
							   {'name':'node2', 'type':'node'},
							   {'name':'node3', 'type':'node'},
							   {'name':'spring', 'type':'float'},
							   {'name':'damping', 'type':'float'}
				],
				# This defines where the light flares will be. It is positionned relative to 3 nodes of the chassis. One node is the reference node, and the two others define a base (x,y). So the flare is in the plane defined by the 3 nodes, and is placed relative to the reference node by adding a fraction of the vectors ref->x and ref->y. The three first parameters are the 3 nodes numbers (rex,x,y) and the two next gives what amount of ref->x and ref->y to add to displace the flare point (these two should be logically between 0 and 1, or else that means you use the wrong base triangle and if the body flexes too much the flare will not stick to the body correctly).
				'flares':[
					{'name':'ref node', 'type':'node'},
					{'name':'x node', 'type':'node'},
					{'name':'y node', 'type':'node'},
					{'name':'offsetx', 'type':'float'},
					{'name':'offsety', 'type':'float'},
					{'name':'typefield', 'type':'string',
														 'validvalues':[
																		'f', #	f (default mode when not stated): frontlight
																		'b', #	b : brakelight
																		'l', #	l : left blinker
																		'r', #	r : right blinker
																		'R', #	R : reverse light (on when driving in R gear)
																		'u'  #	u : user controlled light (i.e. fog light) (see controlnumber)) 
																		]
																		},
					{'name':'control number', 'type':'int', 'required':False, 'help':'Control Number - This determines how this light is switched on and off, if you chose a user controlled light. Valid user defined control numbers are 0-500. If you chose a non-user controlled light(i.e. brake light) you should say -1 here.'},
					{'name':'blink delay', 'type':'float', 'required':False, 'help': 'Blinkdelay - This defines how long the delay is between the light changes in Milliseconds. A value of 500 means that the light is 500ms on and 500ms off. Use a value of -1 to use the default value of 500ms. Use a value of 0 to create a non-blinking light.'},
					{'name':'size', 'type':'float', 'required':False, 'splitspaces':True, 'help':'Size - This determines how big the flare will be. Reasonable values are between 0.1 and 5 (0.1 = 10% of default size). If the size is smaller then 0, then the flare will be independent of the camera angle. (So the flare does not get smaller when you move the camera)'},
					{'name':'material', 'type':'string', 'required':False, 'help': 'Material Name - This field determines what material should be used for the flare display. If you want to use the standard material, use default. Please note that there is not comma between the material name and the size Argument. You can use tracks/aimflare to position your flare.'} 
																	
				],
				'flares2':[
					{'name':'ref node', 'type':'node'},
					{'name':'x node', 'type':'node'},
					{'name':'y node', 'type':'node'},
					{'name':'offset x', 'type':'float'},
					{'name':'offset y', 'type':'float'},
					{'name':'offset z', 'type':'float'},
					{'name':'typefield', 'type':'string',
														 'validvalues':[
																		'f', #	f (default mode when not stated): frontlight
																		'b', #	b : brakelight
																		'l', #	l : left blinker
																		'r', #	r : right blinker
																		'R', #	R : reverse light (on when driving in R gear)
																		'u'  #	u : user controlled light (i.e. fog light) (see controlnumber)) 
																		]
																		},
					{'name':'control number', 'type':'int', 'required':False, 'help':'Control Number - This determines how this light is switched on and off, if you chose a user controlled light. Valid user defined control numbers are 0-500. If you chose a non-user controlled light(i.e. brake light) you should say -1 here.'},
					{'name':'blink delay', 'type':'float', 'required':False, 'help': 'Blinkdelay - This defines how long the delay is between the light changes in Milliseconds. A value of 500 means that the light is 500ms on and 500ms off. Use a value of -1 to use the default value of 500ms. Use a value of 0 to create a non-blinking light.'},
					{'name':'size', 'type':'float', 'required':False, 'splitspaces':True, 'help':'Size - This determines how big the flare will be. Reasonable values are between 0.1 and 5 (0.1 = 10% of default size). If the size is smaller then 0, then the flare will be independent of the camera angle. (So the flare does not get smaller when you move the camera)'},
					{'name':'material', 'type':'string', 'required':False, 'help': 'Material Name - This field determines what material should be used for the flare display. If you want to use the standard material, use default. Please note that there is not comma between the material name and the size Argument. You can use tracks/aimflare to position your flare.'} 
																	
				],


				
				# Dashboard (to add a custom direction wheel to your dashboard) 
				'dashboard':[
							 {'name':'ref', 'type':'node'},
							 {'name':'x', 'type':'node'},
							 {'name':'y', 'type':'node'},
							 {'name':'offsetx', 'type':'float'},
							 {'name':'offsety', 'type':'float'},
							 {'name':'offsetz', 'type':'float'},
							 {'name':'rotx', 'type':'float'},
							 {'name':'roty', 'type':'float'},
							 {'name':'rotz', 'type':'float', 'splitspaces':True},
							 {'name':'dashboard mesh', 'type':'string'},
							 {'name':'dir wheel', 'type':'string'},
							 {'name':'x offset', 'type':'float'},
							 {'name':'y offset', 'type':'float'},
							 {'name':'z offset', 'type':'float'}
				],
				'beacon':[
							 {'name':'ref', 'type':'node'},
							 {'name':'x', 'type':'node'},
							 {'name':'y', 'type':'node'},
							 {'name':'offsetx', 'type':'float'},
							 {'name':'offsety', 'type':'float'},
							 {'name':'offsetz', 'type':'float'},
							 {'name':'rotx', 'type':'float'},
							 {'name':'roty', 'type':'float'},
							 {'name':'rotz', 'type':'float'},
							 {'name':'beacon mesh', 'type':'string', 'splitspaces':True},
							 {'name':'material', 'type':'string'},
							 {'name':'color red', 'type':'float'},
							 {'name':'color blue', 'type':'float'},
							 {'name':'color green', 'type':'float'}
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
					{'name':'mesh', 'type':'string', 'splitspaces':True},
					{'name':'wheel mesh', 'type':'string', 'splitspaces':True, 'required': False},
					{'name':'Red color', 'type':'float', 'required':False},
					{'name':'Green color', 'type':'float', 'required':False},
					{'name':'Blue color', 'type':'float', 'required':False},
					{'name':'wheel degree', 'type':'float', 'required':False} 
				],
				
				# Flexbodies are pretty much the same as props. The only difference between them is that flexbodies deform. The first line of this section is exactly the same format as on the props section
				'flexbodies':[
							 {'name':'ref node', 'type':'node'},
							 {'name':'x node', 'type':'node'},
							 {'name':'y node', 'type':'node'},
							 {'name':'offsetx', 'type':'float'},
							 {'name':'offsety', 'type':'float'},
							 {'name':'offsetz', 'type':'float'},
							 {'name':'rotx', 'type':'float'},
							 {'name':'roty', 'type':'float'},
							 {'name':'rotz', 'type':'float'},
							 {'name':'mesh', 'type':'string'}
				], 				

				#This last part defines the most visible part of the truck: the body. It will dress the chassis with solid triangles. You must define each body panel (a continuous almost-flat section) in a different submesh section, in order to have sharp body angles, and to simplify texturing. A submesh has two subsection: the texcoords, that places nodes of the submesh on the texture image (coordinates between 0.0 and 1.0) , and then the cab subsection, that draws the triangles, with triplets of node numbers. The nodes used in the cab subsection must be present in the texcoord subsection. The order in which the three points forming the triangles is given is important, as its winding defines in which direction it will be visible. The winding must be counterclockwise to be visible (IIRC). There is an optional flag to the cab subsection: if you add "c" to the triangle, this triangle will be a contact triangle, that can contact with contacters nodes. mcreed has contributed a cool Texturing Tutorial that describes how to fill the submesh and cab parts of the truck file. When the tag "backmesh" is added, the triangles backsides of the submesh will be black instead of see-through.
				# more info texturing http://wiki.rigsofrods.com/pages/Texturing_Tutorial
				'submesh':[
					{'name':'groupno', 'type':'int'}
				],
				# the texcoords, that places nodes of the submesh on the texture image (coordinates between 0.0 and 1.0)
				'texcoords':[
					{'name':'node', 'type':'node'},
					{'name':'u', 'type':'float'},
					{'name':'v', 'type':'float'}
				],
				# cab subsection, that draws the triangles, with triplets of node numbers
				'cab':[
					{'name':'node1', 'type':'node'},
					{'name':'node2', 'type':'node'},
					{'name':'node3', 'type':'node'},
					{'name':'options', 'type':'string',
											 'required':False,
											 'default':None,
											 'validvalues':[
												'c', # this triangle will be a contact triangle, that can contact with contacters nodes. 
												'n', # normal
												'b', # this triangle will be part of a buoyant hull. 
												'D', # this triangle will be both a contact triangle AND a buoyant hull part (combination of the b and c flags). 
												'p', # p: force required to pierce through is ten times bigger
												'u', # u: impossible to pierce
												'F', # F: force required to pierce through is ten times bigger plus boat hull (D)
												'S'  # S: impossible to pierce plus boat hull (D) 
											]}
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
							'S', # 'S',=stabilator with right hand axis (full body elevator), useful for e.g. a Mig25
							'T', # 'T'=stabilator with left hand axis (full body elevator), useful for e.g. a Mig25 
							'c', # 'c'=right elevon (right aileron + elevator), useful for e.g. Concorde
							'd', # 'd'=left elevon (left aileron + elevator), useful for e.g. Concorde
							'g', # 'g'=right flaperon (right aileron + flap)
							'h', # 'h'=left flaperon (left aileron + flap)
							'U', # 'U'=taileron with right hand axis (full body elevator+aileron), useful for e.g. a F-15
							'V', # 'V'=taileron with left hand axis (full body elevator+aileron), useful for e.g. a F-15
							'i', # 'i'=right ruddervator (rudder + elevator), useful for V-tails like the Bonanza
							'j'  # 'j'=left ruddervator (rudder + elevator), useful for V-tails like the Bonanza							 
						]},
					# Relative chord point at which starts the control surface (between 0.5 and 1.0)
					{'name':'chord point', 'type':'float'},
					# Minimum deflection of the control surface, in degree (negative deflection)
					{'name':'minimum deflection', 'type':'float'},
					# Maximum deflection of the control surface, in degree (positive deflection)
					{'name':'maximum deflection', 'type':'float'},
					# Airfoil file to use
					{'name':'airfoil filename', 'type':'string'}
				],
				
				# An airbrakes is a moving panel used to slow down an airplane (key bindings: "3" and "4"). It is positionned similarly to a "props", with noderef, nodex, nodey, offsetx, offsety, offsetz. nodea is an additional node to make the braking forces symmetric (they are applied to noderef, nodex, nodey and nodea). Width and length define the dimension of the panel, and max angle the maximum inclination angle. Then comes two texture coordinates that apply to the main texture of the vehicle. These airbrakes can be easily added to a wing box, with noderef, nodex, nodey and nodea being the four upper nodes of a box. 
				'airbrakes':[
					 {'name':'ref', 'type':'node'},
					 {'name':'node x', 'type':'node'},
					 {'name':'node y', 'type':'node'},
					 {'name':'node force symetric', 'type':'node'},
					 {'name':'offsetx', 'type':'float'},
					 {'name':'offsety', 'type':'float'},
					 {'name':'offsetz', 'type':'float'},
					 {'name':'width', 'type':'float'}, 	  # Width define the dimension of the panel
					 {'name':'length', 'type':'float'}, 	 # length define the dimension of the panel
					 {'name':'max angle', 'type':'float'}, # max inclination angle
					 {'name':'textcord x1', 'type':'string'}, # texture coords x1
					 {'name':'textcord y1', 'type':'string'}, # texture coords y1
					 {'name':'textcord x2', 'type':'string'}, # texture coords x2
					 {'name':'textcord y2', 'type':'string'} # texture coords y2
				
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
					{'name':'airfoil filename', 'type':'string'}
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
					{'name':'airfoil filename', 'type':'string'}
				],
				#turbojets
				'turbojets':[
				   # a node at the air intake 
				   {'name':'node front', 'type':'node'},
				   # a node at the base of the nozzle 
				   {'name':'node back', 'type':'node'},
				   # a node at the side of the engine, for reference. 
				   {'name':'node side', 'type':'node'},
				   # tells if it can go to reverse (not sure if it works) 
				   {'name':'is_reversable', 'type':'int'}, # wiki dont know if it works
				   # the thrust without afterburner (in kilonewtons)
				   {'name':'dry thrust', 'type':'float'},
				   # the total thrust with afterburner, or zero if it does not apply. 
				   {'name':'wet thrust', 'type':'float'},
				   # not used yet
				   {'name':'front diameter', 'type':'float'},
				   # the nozzle diameter 
				   {'name':'nozzle diameter', 'type':'float'},
				   # the length of the nozzle. This will automatically add a nozzle prop at the end of the engine, with the diameter and length specified. 
				   {'name':'nozzle diameter', 'type':'float'}
					
				],
				
				#WHAT IS THIS
				'pistonprops':[
				   {'name':'ref', 'type':'node'},
				   {'name':'back', 'type':'node'},
				   {'name':'p1', 'type':'node'},
				   {'name':'p2', 'type':'node'},
				   {'name':'p3', 'type':'node'},
				   {'name':'p4', 'type':'node'},
				   {'name':'couplenode', 'type':'float'},
				   {'name':'power', 'type':'int'},
				   {'name':'pitch', 'type':'int'},
				   {'name':'prop foil', 'type':'string'}
				],

				#Screwprops are boats propellers. As of RoR 0.31, the definition of this section is not stabilized, and is bound to change as the propeller model will improve. Currently, steering is only done by thrust vectoring. The current format is prop node, back node, top node, power.				 
				'screwprops':[
				   {'name':'prop node', 'type':'node'},
				   {'name':'back node', 'type':'node'},
				   {'name':'top node', 'type':'node'},
				   {'name':'power', 'type':'float'}
				],

				'comment':[
						{'name':'multiline comment', 'type':'string', 'restofline':True}
						],
				'end_comment':[
						{'name':'multiline comment end', 'type':'string'}
						],

		'hookgroup': [
					{'name': 'hookgroup', 'type':'string'},
					{'name': 'node id', 'type': 'int', 'help': 'node number of this group'},
					{'name': 'group id', 'type':'int', 'help': 'group of the node, -1 all groups'}
					],
		'slidenodes':[
					{'name':'slide node', 'type':'node'},
					{'name':'beam list', 'type':'string', 'restofline':True}
					],
		'shocks2':[
				{'name':'first node', 'type':'node'},
				{'name':'second node', 'type':'node'},
				{'name':'spring', 'type':'float'},
 				{'name':'damping', 'type':'float'},
 			 	{'name':'prog spring', 'type':'float'},
 			  	{'name':'prog damping', 'type':'float'},
  			  	{'name':'spring out', 'type':'float'},
  			  	{'name':'damping out', 'type':'float'},
  			  	{'name':'prog spring out', 'type':'float'},
  			  	{'name':'prog damping out', 'type':'float'},
  			  	{'name':'short bound', 'type':'float'},
  			  	{'name':'long bound', 'type':'float'},
  			  	{'name':'precomp', 'type':'float'},
  			  	{'name':'options', 'type':'string',
					'validmultiplevalues':[
										{'name':'invisible', 'option':'i', 'type':'string'},
										{'name':'soft bump', 'option':'s', 'type':'string'},
										{'name':'metric values', 'option':'m', 'type':'string'},
										{'name':'Absolute metric', 'option':'M', 'type':'string'}
										]
					
					}
				],
		'torquecurve':[
					{'name':'torque curve', 'type':'string', 'restofline':True}
					
					],
		'axles':[
				{'name':'axles', 'type':'string', 'restofline':True}
				],
		'managedmaterials':[
				{'name':'new name', 'type':'string', 'splitspaces':True},
				{'name':'effect', 'type':'string', 'splitspaces':True}, 		
				{'name':'effect parameter', 'type':'string', 'splitspaces':True, 'restofline':True}
						
						],
		'railgroups':[
				{'name':'node id', 'type':'node'},
				{'name':'node list', 'type':'string', 'restofline':True}
					
					
					],
		'envmap':[
				{'name':'envmap', 'type':'string'}
				],
		'materialflarebindings':[
					{'name': 'flare number', 'type':'int'},
					{'name': 'material Flare bind', 'type':'string'}
								]
				}

	# tree of the actual file's data
	tree = None
	# this will hold all comments
	comments = None

	links = [
		{}
	]

	def __del__(self):
		self.lines = []
		
	def __init__(self):
		self.initVariables()

	def initVariables(self):
		""" clear variables that are 
		ONLY before __init__ method"""
		self.tree = None
		# this will hold all comments
		self.comments = None

		self.links = [
					  {}
					 ]
		self.errorCount = [] # each time errorMsg is called, so a parsing error had happened
		self.requiredSections = ['title', 'globals', 'nodes', 'beams', 'cameras', 'cinecam']
		self.lines = []
		self.formatOutput = False #Format integer and floats with spaces to indent
		self.tabBeforeLine = False #all data section is indented after section Name
		self.blankLineBeforeSection = True #Clear a bit content, inserting a blank line before each section
		self.errorReported = False
		self.filename = ""
		
	def argIsRequired(self, arg):
		# simple wrapper, because if not otherwise defined, everthing is required
		if arg.has_key('required'):
			return arg['required']
		return True

	def errorMsg(self, filename, lineno, sectionname, sectiontype, argname, line, msgold):
		self.errorReported = True
		obj = self.createObject(uhoh, [line])
		self.lines.append(obj)
		argpath = "/%s/%s/%s" % (sectiontype, sectionname, argname)
		msg = "%20s Line %04d %-30s | %-40s | %s" % \
			(os.path.basename(filename), int(lineno) + 1, argpath,
			 msgold, line)

		self.errorCount.append(msg)
		lineobj = self.getLine(lineno)
		if not lineobj is None:
			if not 'errors' in lineobj.keys():
				lineobj['errors'] = []
			lineobj['errors'].append(msg)

#		if not 'errors' in self.tree.keys():
#			self.tree['errors'] = [] #initialize section
#		self.tree['errors'].append({'data':line, 'originline':lineno, 'file':filename, 'section':argpath, 'error':msgold, 'line':line})
		sys.stderr.write(msg + "\n")

	def findNode(self, nodeNum):
		
		#need to search over all file since people can create several nodes sections :-s
		if int(nodeNum) == 9999:
			return None
		for obj in self.lines:
			if obj.section == 'nodes' and not obj.isHeader:
				if obj.id == nodeNum: return obj
		return None

	def addComment(self, section, comment, lineno, attached):
		if not 'comments' in self.tree.keys():
			self.tree['comments'] = []
		newcomment = {'data':[comment, attached], 'originline':lineno, 'section':section, 'type':'comment'}
		self.tree['comments'].append(newcomment)

	def splitArgumentWithSpaces(self, args, argumentsection):
		#some arguments have a space between them, split them
		if argumentsection is None:
			return 
		cont = 0
		last = len(args)
		while cont < last:
			if cont < len(argumentsection):
				if argumentsection[cont].has_key('restofline'):
					if argumentsection[cont]['restofline']:
						newparam = ", ".join(args[cont:]) #args was previously splitted by comma
						newargs = args[0:cont]
						newargs.append(newparam) 
						args = newargs
						print "args with restofline :", args
						break
			
				if argumentsection[cont].has_key('splitspaces'):
					if argumentsection[cont]['splitspaces']:
						spacelist = args[cont].split(" ")
						if len(spacelist) > 1:
							args[cont] = spacelist[0] #replace the previous param
							for ncont in range(1, len(spacelist)):
								args.insert(cont + 1, spacelist[ncont])
								last += 1
								cont += 1
				cont += 1
			else: cont += 1
		return args # had been modified!!!!
			
	def parse(self, filename, verbose=True):
		self.filename = filename
		self.verbose = verbose
		self.truckSections = []
#		 making commandline compatible
		content = []
		if os.path.exists(filename):
			content = getContent(filename)
			if content is None:
				sys.stderr.write("error while reading file!\n")
				sys.exit(1)
			if verbose:
				sys.stderr.write("processing file %s\n" % filename)
		else:
			try:
				from rorcommon import loadResourceFile
				content = loadResourceFile(filename)
			except:
				sys.stderr.write("error while reading file!\n")
				sys.exit(1)

		self.tree = {'title':[]}
		inlineComment = ""
		actualsection = "title"
		prevSectionWasCommand = False
		prevsection = ""
		currentsubmesh = None
		self.tree['submeshgroups'] = []
		if len(content) == 0:
			raise Exception("content file length is zero") 
		lineno = -1
		nextLine = None
		for lineno in range(0, len(content)):
			line = content[lineno]
			# strip line-endings
			line = line.strip()
			#log.info(lineno+","+ line)
			if line.strip() == "":
				# add blank lines to comments
				self.addComment(actualsection, line, lineno, False)
				continue

			#split comments out first
			if line.find(';') != -1:    
				line1 = line.split(';')
				if line1[0] != '':  #comment at the end of a line
					line = line1[0]
					inlineComment = line1[1] #no semicolon added
				else:				#comment at first character of line
					self.lines.append(self.createObject(';', [line[1:]]))
					continue
			if prevSectionWasCommand : 
				actualsection = prevsection
				prevSectionWasCommand = False

			# test for new section
			if line in self.sections.keys():
				prevsection = actualsection
				actualsection = line
#				if not currentsubmesh is None and len(currentsubmesh['texcoords']) > 0 and len(currentsubmesh['cab']) > 0:
#					self.tree['submeshgroups'].append(currentsubmesh)
#					currentsubmesh = None
#				if actualsection == 'submesh' and currentsubmesh is None:
#					currentsubmesh = {'texcoords':[], 'cab':[], 'type':'submeshgroup'}
				# check if section is in the tree already
				if not actualsection in self.tree.keys():
					self.tree[actualsection] = []
				obj = self.createObject(actualsection, [])
				obj.isHeader = True
				self.lines.append(obj)
				
				 
				continue
			
			# extract arguments
			args = line.split(',')

			# format args to have correct datatypes
			for argnum in range(0, len(args)):
				args[argnum] = args[argnum].strip()
			
			#Lepes ask: should I split by spaces now to get some not comma separate values?

			# check arguments

			#check if it is a command
			argumentsection = []

			try:
				prevSectionWasCommand = False
				cmdcheck = args[0].split(' ')[0].strip()
				if cmdcheck in self.commands.keys():
					prevsection = actualsection
					actualsection = cmdcheck
					if list_has_value(self.commands[cmdcheck], 'restofline', True) != -1:
						args = []
						args.append(cmdcheck)
						args.append(line[len(cmdcheck) + 1:])
					#construct new set of arguments if there are some
					if len(args[0].split(' ')) > 1: #i.e.: set_beam_defaults -1, -1
						newargs = args[0].split(' ')
						newargs.extend(args[1:])
						args = newargs
						prevSectionWasCommand = True
						#ok
						# continue to next line, do not further parse it!
	#					continue
					else:
						# no other args except the command itself
						args = args[0:]
						# continue to next line, do not further parse it!
	#					continue
					argumentsection = self.commands[cmdcheck]
					argumentsection_str = "command"
				else:
					
					argumentsection = self.sections[actualsection]
					argumentsection_str = "section"
			except Exception, e:
				print str(e)
				continue
			argumenttree = []
			args = self.splitArgumentWithSpaces(args, argumentsection) 
			# debug stuff: 
			#print actualsection, argnum, args
			#print (args), (argumentsection)
			#if  len(args) < len(argumentsection):
			#	print "too short!!"

#			print 'section detected %s \n line: %s' % (actualsection, line)
			for argnum in range(0, len(argumentsection)):
#				print "checking arg num %d" % argnum
				if argnum >= len(args) and not self.argIsRequired(argumentsection[argnum]):
					continue
				elif argnum >= len(args) and not self.argIsRestOfLine(argumentsection, argnum):
					self.errorMsg(filename, lineno, actualsection, argumentsection_str,
							argumentsection[argnum]['name'], line, "too less args(%d/%d)" % (len(args), len(argumentsection)))
					break
				if self.argIsRestOfLine(argumentsection, argnum):
					arg = "".join(args[argnum:])
				else: arg = args[argnum]
				try:
					if argumentsection[argnum]['type'] == 'string' and type(arg) == type("") or \
		(argumentsection[argnum]['type'] == 'int' or argumentsection[argnum]['type'] == 'node')	and type(int(arg)) == type(1) or \
						argumentsection[argnum]['type'] == 'float'  and type(float(arg)) == type(0.1) or \
						(argumentsection[argnum]['type'] == 'shortcut'):
						#check not for valid values

						#if argumentsection[argnum]['type'] == 'node':
							# this is being checked later if everything is read in!
						if argumentsection[argnum].has_key('validvalues') and argumentsection[argnum]['type'] == 'string':
							#check string valid values

							#continue on empty optionals
							if not self.argIsRequired(argumentsection[argnum]) and arg.strip() == "":
								continue

							# some section has a list with strings, other ones has a list of dictionaries, so we must check both 
							optionList = argumentsection[argnum]['validvalues']
							if optionList is not None:
								if isinstance(optionList, ListType):
									for element in optionList:
										if isinstance(element, DictType):
											if list_has_value(optionList, 'option', letter) == -1:
												self.errorMsg(filename, lineno, actualsection, argumentsection_str,
															argumentsection[argnum]['name'], line, "invalid value of argument: %s" % arg)
												break

										elif isinstance(element, StringType):
											if not arg in optionList:
												self.errorMsg(filename, lineno, actualsection, argumentsection_str,
															argumentsection[argnum]['name'], line, "invalid value of argument: %s" % arg)
												break
							
							
#							if arg not in argumentsection[argnum]['validvalues']:
#								self.errorMsg(filename, lineno, actualsection, argumentsection_str,
#											argumentsection[argnum]['name'], line, "invalid value of argument: %s" % arg)
						
						if argumentsection[argnum].has_key('validmultiplevalues') and argumentsection[argnum]['type'] == 'string':
							#continue on empty optionals
							if not self.argIsRequired(argumentsection[argnum]) and arg.strip() == "":
								continue
							for letter in arg:
								if list_has_value(argumentsection[argnum]['validmultiplevalues'], 'option', letter) == -1:
									self.errorMsg(filename, lineno, actualsection, argumentsection_str,
											argumentsection[argnum]['name'], line, "invalid value of argument: %s" % arg)
									break

						#print "type ok"
						if (argumentsection[argnum]['type'] == 'int' or argumentsection[argnum]['type'] == 'node'): arg = int(arg)
						elif argumentsection[argnum]['type'] == 'float': arg = float(arg)
						argumenttree.append(arg)
						continue
				except Exception, e:
					self.errorMsg(filename, lineno, actualsection, argumentsection_str,
								argumentsection[argnum]['name'], line, "invalid type of argument, or unkown command")
					print "argnum was %d, args are-> %s" % (argnum, " | ".join(args))
					print str(e)
					break
			if self.errorReported : self.errorReported = False
			else:
				if len(args) > len(argumentsection):
					self.errorMsg(filename, lineno, actualsection, argumentsection_str,
								None, line, "too much args(%d/%d)" % (len(args), len(argumentsection)))

			#append caps and textcoords to submesh section
#			if (actualsection == 'texcoords' or actualsection == 'cab') and not currentsubmesh is None:
#				currentsubmesh[actualsection].append({'data':argumenttree, 'originline':lineno, 'section':actualsection})
#				continue
			# append argument list to the tree
			if len(argumenttree) > 0 or argumentsection_str == 'command':
				obj = self.createObject(actualsection, argumenttree)
				if inlineComment != "" :
					obj.inlineComment = inlineComment
					inlineComment = ''
				self.lines.append(obj)
#				if argumentsection_str == 'command':
#					# prepend command again
#					argumenttree.insert(0, str(cmdcheck))
#					self.tree[actualsection].append({'data':argumenttree, 'originline':lineno, 'section':actualsection, 'type':'command', 'obj':obj})
#				else:
#					self.tree[actualsection].append({'data':argumenttree, 'originline':lineno, 'section':actualsection, 'obj':obj})
			continue
		#if len(self.errorCount) > 0:
		#	showInfo('total errors', 'errors interpreting this file: %d\n\n%s' % (len(self.errorCount), '\n'.join(self.errorCount)))
		print 'errors interpreting this file: %d' % len(self.errorCount)
		#self.checkNodes()
		#self.checkForDoubleNodes()
		#self.checkForDoubleBeams()
	def getSummary(self):
		""" return a sumary of how many elements has each section
		
		return a dictionary, each key is a section and the value is a counter
		"""
		sum = {}
		for l in self.lines:
			if l.isHeader: continue
			if not sum.has_key(l.section):
				sum[l.section] = 0
			sum[l.section] += 1
		return sum
	def insertLine(self, atPos= -1, section=None):
		if section is None:
			section = self.lines[atPos].section
		if isinstance(section, StringType):
			obj = self.createObject(section)
		elif isinstance(section, lineOfSection):
			obj = section
		else: raise Exception("I need a string name or lineOfSection to create a section")
		
		if atPos + 1 >= len(self.lines):
			self.lines.append(obj)
		elif atPos + 1 > -1:
			if self.lines[atPos].isHeader: atPos += 1
			self.lines.insert(atPos, obj)
		return obj
	def cloneObject(self, obj):
		if obj.isHeader: raise Exception("We can not duplicate a section header")
		argTree = []
		for i in range(obj.getMaxCols()):
			argTree[i] = obj.getColValue(i)
		return self.createObject(obj.section, argTree)
		
	def deleteLine(self, obj):
		if obj is not None:
			self.lines.remove(obj)
	def createObject(self, actualsection="", argumenttree=[]):
		""" Instance the lineOfSection class and create attributes on the fly""" 
		obj = lineOfSection()
		obj.parent = self
#		print "creating line of section for section " + actualsection
#		obj.setSection(actualsection)
		if self.commands.has_key(actualsection):
			value = True
			columnlist = self.commands[actualsection]
		elif self.sections.has_key(actualsection):
			value = False
			columnlist = self.sections[actualsection]
		else:
			raise exception('%s is not a valid neither command nor section' % actualsection)

		obj.isHeader = False
		obj.setSection(actualsection)
#		f = 'isCommand'
#		setattr(obj, f, value)
		setattr(obj, 'section', actualsection)
		if len(columnlist) > 0 and not obj.isHeader: #python list
			for i in range(len(columnlist)):
				if columnlist[i].has_key('name'):
					attrname = obj.getColName(i) 
					if i >= len(argumenttree) : attrvalue = None
					else: attrvalue = argumenttree[i] #must match
					setattr(obj, attrname, attrvalue)
				else: raise Exception('section %s column %d does not have a "name" dictionary key' % (actualsection, i))
		return obj

	def sectionStart(self, sectionname):
		""" return the index of parser.lines list where this section starts
		
		***not good if people create some repeated sections 
		
		return -1 if not found
		"""
		i = 0
		while i < len(self.lines):
			if self.lines[i].section != sectionname:
				i += 1
			else: return i
		return - 1
	def sectionEnd(self, sectionname):
		""" return the index of parser.lines list where this section ends
		
		return -1 if not found
		"""
		i = 0
		Found = False
		while i < len(self.lines):
			if Found and self.lines[i].section != sectionname and not self.lines[i].isCommand:
				return i
			elif self.lines[i].section == sectionname:
				Found = True
			i += 1
		return - 1 
			
			
	def argIsRestOfLine(self, sectiondef, argnum):	
		""" argumentsection is section definition, 
		argnum is the col that we want to know if it is a rest of line
		"""
		if argnum < len(sectiondef):
			if sectiondef[argnum].has_key("restofline"):
				return sectiondef[argnum]["restofline"]
		return False
	
	def save(self):
		#(fid, filename) = tempfile.mkstemp(suffix='.RoRObject')
		filename = self.filename + "_pickle"
		log().info("trying to save Settings to file %s for file %s" % (filename, os.path.basename(self.filename)))
		try:
			fh = open(filename, 'w')
			pickle.dump(self.tree, fh)
			fh.close()
			log().info("saving successfull!")
		except Exception, err:
			log().error("error while saving settings")
			log().error(str(err))


	def isFloat(self, s):
		try:
			i = float(s)
		except ValueError:
			i = None
		return i

	def printtree(self):
		rstr = ""
		for s in self.tree.keys():
			if len(self.tree[s]) == 0:
				continue
			rstr += "\n"
			rstr += "===========================================================================================================================================================================\n"
			rstr += "%s: %d\n" % (s, len(self.tree[s]))
			# for non original columns (generated ones)
			if not self.sections.has_key(s):
#				rstr += self.tree[s]
				continue
			for column in self.sections[s]:
				rstr += "| %-15s" % (column['name'][0:15])
			rstr += "\n"
			rstr += "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
			for line in self.tree[s]:
				for arg in line['data']:
					try:
						if arg.isdigit() or self.isFloat(arg):
							rstr += "|%15.3f " % (round(float(arg), 4))
						else:
							rstr += "|%15s " % (str(arg)[0:15])
					except:
						rstr += "|%15s " % (str(arg)[0:15])
				if 'errors' in line.keys():
					rstr += "[ERRORS: %d] " % (len(line['errors']))
				rstr += "(origin: %d)\n" % (line['originline'])
		log().info(rstr)

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
					data = ';' + n['data'][0]
			else:
				data = ", ".join(n['data'])
			result.append(data)
			n = self.getnextLine(n['originline'])
		
		#for r in result:
		#	print r

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
			if skey in ['node', 'errors']:
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
							self.errorMsg(self.filename, beam1obj['originline'], 'beams', 'section', 'beam',
							str(beam1obj['originline']) + ": " + str(beam1) + ", " + str(beam2obj['originline']) + ": " + str(beam2),
							 "duplicate beam found: %s and %s" % (beamcounter1, beamcounter2))
							continue
					if beam1[0] == beam2[1] and beam1[1] == beam2[0]:
						ignorebeams.append(str(beam1))
						ignorebeams.append(str(beam2))
						# found inverse beam
						self.errorMsg(self.filename, beam1obj['originline'], 'beams', 'section', 'beam',
						str(beam1obj['originline']) + ": " + str(beam1) + ", " + str(beam2obj['originline']) + ": " + str(beam2),
						"inverse beam found: %s and %s" % (beamcounter1, beamcounter2))
						continue
				except:
					self.errorMsg(self.filename, beam1obj['originline'], 'beams', 'section', 'beam', str(beam1) + ", " + str(beam2), "error while checking beams")
					continue
	def sectionDef(self, sectionName):
		""" return the definition of the sectionName
			It could be a command or a section
		"""
		if self.commands.has_key(sectionName): return self.commands[sectionName]
		elif self.sections.has_key(sectionName): return self.sections[sectionName]
		else: return None #raise Exception('%s is not neither a command nor valid sectionName')
	
	def getColOfSection(self, sectionName, colIndex):
		""" return the definition of the column
		"""
		sectiondef = self.sectionDef(sectionName)
		if colIndex >= len(sectiondef): return None # raise Exception("can not access to col %d of section %s because section only have %d columns" % (colIndex, sectionName, len(sectiondef)))
		return sectiondef[colIndex]
		
	
	def maxColumns(self):
		""" return maximum columns that TDF has now"""
		maxCol = -1
		for sec in self.commands.keys():
			maxCol = max(len(self.sectionDef(sec)), maxCol)
		for sec in self.sections.keys():
			maxCol = max(len(self.sectionDef(sec)), maxCol)
		return maxCol
	def expandNodeRange(self, str):
		""" str is: 1-4  34  37 minus 3 4-44
		will return a python list as: [1, 2, 3, 4, 34, 37]
		"""
		def parse(text, lst, ignorelst=[]):
			""" parse the text as a single node range and add those nodes to lst list"""

			#standar node range 1-23
			idx = text.find("-")
			if idx > -1:
				first = int(text[:idx])
				second = int(text[idx + 1:])
				for i in range(first, second + 1):
					if i not in ignorelst: lst.append(i)
			try:
				f = eval(text)
				lst.append(int(text))
			except Exception:
				log().debug("ignoring node Range parameter %s" % text)

		
		nodelst = []
		excludelst = []
		str += ' ' # bugfix ;D
		idxpar = str.find("minus")
		if idxpar > -1:
			exclude = str.split("minus")[1]
			if len(exclude) > 0: exclude = exclude.split(" ")
			nodes = str.split("minus")[0].split(" ")
			
		else: 
			nodes = str.split(" ")
			exclude = []

		for x in exclude: parse(x, excludelst)
		for n in nodes: parse(n, nodelst, excludelst)
		return nodelst
			
		

def list_has_key(listOfDict, keyToSearch=''):
	""" search for a key of the dict iterating over the list
	    return -1 if not found, otherwise it return the index of the list
	    where the dictionary has the key searched
	"""
	try:
		if not isinstance(listOfDict, ListType): 
			raise Exception("parameter of type list expected")
		if len(listOfDict) > 0:
			for i in range(len(listOfDict)):
				if isinstance(listOfDict[i], DictType):
					if listOfDict[i].has_key(keyToSearch):
						return i
				else: raise Exception("this list has not dictionaries inside ")
	except:
		raise
	return - 1

def list_has_value(listOfDict, keyToSearch='', value=None):
	""" search if the value is in the list of Dictionary
	
	return -1 or the list index where it was found
	
	"""
	
	idx = list_has_key(listOfDict, keyToSearch)
	if idx == -1: return - 1
	for i in range(idx, len(listOfDict)):
		if listOfDict[i].has_key(keyToSearch):
			if value is None:
				if listOfDict[i][keyToSearch] is None: return i
			else:
				if listOfDict[i][keyToSearch] == value : return i
	return - 1


			
#def main():
#	p = rorparser()
#	for argno in range(1,len(sys.argv)):
#		p.parse(sys.argv[argno])
#	p.parse('I:\\Archivos de programa\\Rigs of Rods 0.35\\data\\trucks\\wrecker.truck')
	#p.printtree()
	
#if __name__ == '__main__':
#	main()
