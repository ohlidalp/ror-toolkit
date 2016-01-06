#!/bin/env python
# Thomas Fischer 16/05/2007 thomas (at) thomasfischer.biz
# Lepes 2009-01-21 update parser from latest wiki webpage (truck definition file latest update: 2009-01-21)
import sys, os, os.path, tempfile, pickle

#from ror.logger import log
#from ror.settingsManager import rorSettings
#from ror.rorcommon import *

	# default values: required:True
	# please note: unkown args are marked with 'WHAT IS THIS'


#------------------------------------------------------------------------------ 
# Lepes
# FIXME: some options separated by spaces should be cut i.e.: commands2 "options  description" ==> 'splitspaces':True
# FIXME: add default values to some sections to auto complete?? is it posible?
#------------------------------------------------------------------------------ 

# just for debug, when finish delete it and import from ror.common

FileInfo_def = [
							# uniqueid: this field specifies the unique file ID (you get one by uploading it to the repository). -1 for none
						  {'name':'reserved word', 'type':'string', 'splitspaces':True, 'required':False },
						  {'name':'unique id', 'type':'string'},
							# categoryid: this is the category number from the repository. -1 for none
							# o you can find a list of valid numbers there: Truck Categories 
						  {'name':'repository category', 'type':'int'},
							# fileversion: this opens the possibility to update this mod. the version should be simple integers: 1 for version one, 2 for version two and so on. The version number is an integer number, so do not use character other than 0-9 or . or ,	
						  {'name':'file version', 'type':'int'}
				]




class rorterrainparser(object):
#===============================================================================
# Terrain file structure is very different from truck file definition, 
# we don't have a reserved word on every section to check what are the actual section
# so, we use a 'word' key as a posible reserved word
#===============================================================================
	sectionName = [
					{'name': 'ingame name'   , 'required':True										   },
					{'name': 'config file'  , 'required':True										   },
					{'name': 'water level'										,'word':'w'		   },
					{'name': 'caelum'											 ,'word':'caelum'	  },
					{'name': 'sky color'																},
					{'name': 'start position','required':True										   },
					{'name': 'author info'				  , 'canrepeat':True	,'word':'author'	  },
					{'name': 'fileinfo'										   ,'word':'fileinfo'	},
					{'name': 'mpspawn'					  , 'canrepeat':True	,'word':'mpspawn'	 },
					{'name': 'grass'						, 'canrepeat':True	,'word':'grass'	   }, 
					{'name': 'objects'					  , 'canrepeat':True			},
					{'name': 'end of file'	  , 'required':True, 'word':'end' }
				   ]
	sections = {
			'ingame name': [
							{'name': 'Terrain name', 'type':'string'}
						   ],
			
			'config file':[
						   {'name': 'Config File', 'type':'string'}
						  ],
			
			'water level':[
						   {'name': 'w ', 'type':'string', 'splitspaces':True},
						   {'name': 'in meters', 'type':'float'}
						  ],
						  
			'caelum':[
						   {'name': 'Use Caelum', 'type':'string'}
						  ],	
			
			'sky color':  [
						  {'name':'Red', 'type':'float', 'required':True }, 
						  {'name':'Blue', 'type':'float', 'required':True },
						  {'name':'Green', 'type':'float', 'required':True },
						  ],
			'start position':[
						  {'name':'Truck x', 'type':'float', 'required':True	},
						  {'name':'Truck y', 'type':'float', 'required':True	},
						  {'name':'Truck z', 'type':'float', 'required':True	},
						  {'name':'Camera x', 'type':'float'					},
						  {'name':'Camera y', 'type':'float'					},
						  {'name':'Camera z', 'type':'float'					},
						  {'name':'Character x', 'type':'float'				 },
						  {'name':'Character y', 'type':'float'				 },
						  {'name':'Character z', 'type':'float'				 }
							  
						  ],
						  
			'author info' : [
						  
						  {'name':'reserved word', 'type':'string', 'splitspaces':True},
						  #type = author of what? recommended values: chassis, texture, support 
						  {'name':'author of', 'type':'string'},
						  # authorid = id of the members forum account, so the user may write him a message
						  {'name':'forum id', 'type':'int'},
						  # authorname = name of the author
						  {'name':'author name', 'type':'string'},
						  # email = email address of the author (this is optional and can be left out) 
						  {'name':'author email', 'type':'string',
																  'required':False}
						],
			
			'fileinfo':FileInfo_def,			  
		   
			'mpspawn':  [
						  {'name':'reserverd word', 'type':'string', 'required':True, 'splitspaces':True },
						  {'name':'vehicle class', 'type':'string', 'required':True  }, 
						  {'name':'x', 'type':'float', 'required':True },
						  {'name':'y', 'type':'float', 'required':True },
						  {'name':'z', 'type':'float', 'required':True },
						  {'name':'rotx', 'type':'float', 'required':True },
						  {'name':'roty', 'type':'float', 'required':True },
						  {'name':'rotz', 'type':'float', 'required':True }
						  
						  ],
			'grass':  [
						  {'name':'reserverd word', 'type':'string', 'required':True, 'splitspaces':True },
						  {'name':'grass range', 'type':'int', 'required':True  }, 
						  {'name':'SwaySpeed', 'type':'float', 'required':True },
						  {'name':'SwayLength', 'type':'float', 'required':True },
						  {'name':'SwayDistribution', 'type':'int', 'required':True },
						  {'name':'Density', 'type':'float', 'required':True },
						  {'name':'minx', 'type':'float', 'required':True },
						  {'name':'miny', 'type':'float', 'required':True },
						  {'name':'maxx', 'type':'float', 'required':True },
						  {'name':'maxy', 'type':'float', 'required':True },
						  {'name':'fadetype', 'type':'float', 'required':True },
						  {'name':'minY', 'type':'float', 'required':True },
						  {'name':'maxY', 'type':'float', 'required':True },
						  {'name':'material', 'type':'string', 'required':True },
						  {'name':'colormap', 'type':'string', 'required':True },
						  {'name':'densitymap', 'type':'string', 'required':True }
						  ],		   
			'objects':  [
						  {'name':'x', 'type':'float', 'required':True },
						  {'name':'y', 'type':'float', 'required':True },
						  {'name':'z', 'type':'float', 'required':True },
						  {'name':'rotx', 'type':'float', 'required':True },
						  {'name':'roty', 'type':'float', 'required':True },
						  {'name':'rotz', 'type':'float', 'required':True },
						  {'name':'object name', 'type':'string', 'required':True, 'splitspaces':True },
						  {'name':'qualifier', 'type':'string'},
						  {'name':'unique name', 'type':'string'}
						  ],
			'end of file': [
						 {'name':'End of file', 'required':True}
						]						
		   
		   }
	
	# tree of the actual file's data
	tree = None
	# this will hold all comments
	comments = None

	links = [
		{}
	]

			
	def parse(self, filename, verbose = True):
		self.filename = filename
		self.verbose = verbose
#		 making commandline compatible
#		content = loadResourceFile(filename)
		try:
			content = []
			infile = open(filename,'r')
			content = infile.readlines()
			infile.close()
		except:
			sys.stderr.write("error while reading file!\n")
			raise 

		if content is None:
			sys.stderr.write("error while reading file!\n")
			sys.exit(1)
		if verbose:
			sys.stderr.write("processing file %s\n" % filename)
		self.tree = {"ingame name":[]}
		actualsection = "dummy"
		isectionname = -1
		prevsection = ""
		for lineno in range(0, len(content)):
			line = content[lineno].strip()
			if line == "":
				# add blank lines to comments
				self.addComment(actualsection, line, lineno, False)
				continue
			if lineno > 31:
				return 
			#split comments out first
			if lineno > 3: # at least 3 first lines are required
				if line.find('//') != -1 :
					line1 = line.strip().split('//')
					if len(line1) > 0 and line1[0].strip() !="": # comment at the end of a command line
						line = line1[0]
						self.addComment(actualsection, "// " + line1[1], lineno, True)
					else:
						if line.find("author") != -1 or line.find("fileinfo") != -1:
							line = line.replace("//","").strip() # only one comment supported
						else:
							self.addComment(actualsection, line1[1], lineno, True)
							continue
					

			# actually we have a new line of text and the previous section
			# Change to new section ??
			needChange = False
			if isectionname < len(self.sectionName) -1:
				if isectionname > -1:
					# can repeat actual section ? try it
					needChange = True
					if self.sectionNameHas('canrepeat', isectionname)== True:
						if self.sectionNameHas('word', isectionname) == self.firstWord(line):
							needChange = False
						else:
							# can repeat but actual section has not a reserved word
							# we don't know if will match
							pass
					nextsection = isectionname +1
					if nextsection < len(self.sectionName):
						if self.sectionNameHas('word', nextsection) == self.firstWord(line):
							# line match with next section
							needChange = True
						else:
							nextsection = isectionname
   
				else:
					needChange = True
			if needChange:
				isectionname +=1
				prevsection = actualsection
				actualsection = self.sectionName[isectionname]['name']
				print "actual section: %s. Prev section: %s" % (actualsection, prevsection)
			print "processing section -> %s" % self.sectionName[isectionname]['name']
			# check if section is in the tree already
			if not actualsection in self.tree.keys():
				self.tree[actualsection] = []
				
			# extract arguments
			args = line.split(',')

			# format args to have correct datatypes
			for argnum in range(0,len(args)):
				args[argnum] = args[argnum].strip()

			# check arguments

			defsection = None
			defsection = self.sections[actualsection] # list with column definitions
			defsection_str = "section"
			argumenttree = []
			self.splitArgumentWithSpaces(args, defsection) 
			# debug stuff: 
			#print actualsection, argnum, args
			#print (args), (defsection)
			#if  len(args) < len(defsection):
			#	print "too short!!"
			
			for argnum in range(0, len(defsection)): # for each column definition in the actual section
				
				if argnum >= len(args) and not self.argIsRequired(defsection[argnum]):
					continue
				elif argnum > len(args) and self.minRequiredColumns(isectionname) < argnum:
					continue
				elif argnum >= len(args):
					self.errorMsg(filename, lineno, actualsection, defsection_str,
							defsection[argnum]['name'], line, "too less args(%d/%d)"%(len(args), len(defsection)))
					break
				arg = args[argnum]
				try:
					if defsection[argnum]['type'] == 'string' and type(arg) == type("") or \
		(defsection[argnum]['type'] == 'int' or defsection[argnum]['type'] == 'node')	and type(int(arg)) == type(1) or \
						defsection[argnum]['type'] == 'float'  and type(float(arg)) == type(0.1):
						#check not for valid values

						argumenttree.append(arg)
						continue
				except:
					self.errorMsg(filename, lineno, actualsection, defsection_str,
								defsection[argnum]['name'], line, "invalid type of argument, or unkown command")
					
#					raise
					break

			if len(args) > len(defsection):
				self.errorMsg(filename, lineno, actualsection, defsection_str,
							None, line, "too much args(%d/%d)"%(len(args), len(defsection)))

			# append argument list to the tree
			if len(argumenttree) > 0 :
				self.tree[actualsection].append({'data':argumenttree, 'originline':lineno, 'section':actualsection})
				continue
		#self.checkNodes()
		#self.checkForDoubleNodes()
		#self.checkForDoubleBeams()
		if verbose:
			sys.stderr.write("finished processing of file %s\n" % filename)
#		self.printtree()
		#self.linearizetree()
		#print self.tree['errors']
		#self.save()
	def minRequiredColumns(self, isection):
		section = self.sectionName[isection]['name']
		columnlist = self.sections[section]
		nrequired = 0
		for i in range(0, len(columnlist)):
			if columnlist[i].has_key('required'):
				if columnlist[i]['required']:
					nrequired += 1
		return nrequired
	
	def sectionNameHas(self, key, isection):	
		""" return the value of self.sectionName[key]
		or None if sectionName doesn't have this key
		"""
		if self.sectionName[isection].has_key(key):
			return self.sectionName[isection][key]
		else:
			return None
		
	def firstWord(self, args):
		""" return the first left word of the string 
		keep in mind that SPACE or COLON may be used as 
		a separator """
		a = args
		#splitted into a list, and every item stripped.
		a1 = [x.strip() for x in a.split(" ")]
		for x in a1:
			if len(x) > 0:
				s = [w.strip() for w in x.split(",")]
				for ww in s:
					if len(ww)> 0 :
						return ww.lower()
					
	
	def splitArgumentWithSpaces(self, args, defsection):
		""" args is a list that previously have been splitted by comma
		now we split the arguments with spaces
		"""
		#some arguments have a space between them, split them
		if defsection is None:
			return 
		split = False
		for i in range(0,len(defsection)):
			if defsection[i].has_key('splitspaces'):
				if defsection[i]['splitspaces']:
					split = True
					break 
		if split: 
			cont = 0
			last = len(args)
			while cont < last: # dirty code but "for" bucle can not be used because we expand the list "args"
				spacelist = args[cont].split(" ")
				if len(spacelist) > 1:
					args[cont] = spacelist[0] #replace the previous param
					for ncont in range(1, len(spacelist)):
						args.insert(cont+1, spacelist[ncont])
						last += 1
						cont += 1
				cont += 1
				
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
			rstr +=  "%s: %d\n" % (s, len(self.tree[s]))
			# for non original columns (generated ones)
			if not self.sections.has_key(s):
#				rstr += self.tree[s]
				continue
			for column in self.sections[s]:
				rstr += "| %-15s" % (column['name'][0:15])
			rstr += "\n"
			rstr +=  "---------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n"
			for line in self.tree[s]:
				for arg in line['data']:
					try:
						if arg.isdigit() or self.isFloat(arg):
							rstr +=  "|%15.3f " % (round(float(arg),4))
						else:
							rstr +=  "|%15s " % (str(arg)[0:15])
					except:
						rstr += "|%15s " % (str(arg)[0:15])
				if 'errors' in line.keys():
					rstr +=  "[ERRORS: %d] "%(len(line['errors']))
				rstr += "(origin: %d)\n"%(line['originline'])
		print rstr

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
					raise 
					continue

	def argIsRequired(self, arg):
		# simple wrapper, because if not otherwise defined, everthing is required
		if arg.has_key('required'):
			return arg['required']
		return True

	def errorMsg(self, filename, lineno, sectionname, sectiontype, argname, line, msgold):
		if not self.verbose:
			return
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
			self.tree['errors'] = [] #initialize section
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



def main():
	p = rorterrainparser()
#	for argno in range(1,len(sys.argv)):
	p.parse('C:\\Archivos de programa\\Rigs of Rods 0.35\\data\\terrains\\nhelens.terrn')
	p.printtree()
	
if __name__ == '__main__':
	main()
