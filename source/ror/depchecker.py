#Thomas Fischer 06/07/2007, thomas@thomasfischer.biz
import sys, os, os.path, copy, md5

from ror.logger import log
from ror.settingsManager import rorSettings

DEPCHECKPATH = "depcheckerplugins"
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), DEPCHECKPATH))
from deptools import *

REMOVE_UNUSED_MATERIALS = True

MD5FILENAME = "031amd5.txt" #0.31a md5 .txt
RORDEPSFILENAME = "031a_deps.bin"
MD5FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), MD5FILENAME)
RORDEPSFILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), RORDEPSFILENAME)
GRAPHPATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".." ,"graphs"))

class RoRDepChecker:
	def __init__(self, path, mode, dependfilename, verbose=True):
		self.verbose = verbose
		self.filedeps = {}
		self.dstree = None # target field for single dtree's
		self.notfound = None
		self.dir = path
		self.invalid = False
		self.dependfilename = dependfilename
		
		self.getfiles()
		if mode == "getfiles":
			return

		self.createDeps()

		if mode == "record":
			self.generateCrossDep(False)
			self.saveTree(RORDEPSFILE)
			return
		else:
			self.generateCrossDep(True)


		if dependfilename != "":
			self.generateSingleDep()
		
		if mode == "all" and verbose:
			self.tryGraph()        

	def saveTree(self, filename):
		import pickle
		file = open(filename, 'w')
		pickle.dump(self.filedeps, file)
		file.close()

	def loadTree(self, filename):
		import pickle
		file = open(filename, 'r')
		result = pickle.load(file)
		file.close()
		return result
		
	def savemd5(self):
		lines = []
		for fn in self.files.keys():
			lines.append(os.path.basename(fn)+" "+self.files[fn]['md5']+"\n")
		f=open(MD5FILE, 'w')
		f.writelines(lines)
		f.close()
	
	def getSingleDepRecursive(self, filename, depth = 0):
		file = self.filedeps[filename]
		req = [{'depth':depth, 'filename':filename}]
		for r in file[REQUIRES][FILE]:
			try:
				for rr in self.getSingleDepRecursive(r, depth + 1):
					duplicate = False
					for rsub in req:
						if rr['filename'] == rsub['filename']:
							duplicate  = True
					
					# enable for graph functions (allows  multiple arrows then)
					if not duplicate:
						req.append(rr)
			except:
				pass
		return req
	
	def generateSingleDep(self):
		if not self.dependfilename in self.filedeps.keys():
			self.invalid = True
			if self.verbose:
				log().error("file not found in the dependency tree: %s !" % self.dependfilename)
			return
		tree = self.getSingleDepRecursive(self.dependfilename)           
		#print tree
		if self.verbose:
			for t in tree:
				t['fullpath'] = self.getFullPath(t['filename'])
				t['md5sum'] = self.md5Sum(t['fullpath'])
				infostr = "%-30s %-30s" % ("+"*t['depth']+t['filename'], t['md5sum'])
				log().info(infostr)                
		#self.removeOriginalFilesFromSingleDep
		#for t in tree:
		#    f = t['filename']
		#    print str(self.filedeps[f][REQUIRES])
		#    print str(self.filedeps[f][REQUIREDBY])
		#    print "---------------------------------"
		
		self.dstree = tree
		
		if self.verbose and len(tree) > 1:
			self.tryGraph(tree)
		

	def readMD5File(self):
		md5s = {}
		f=open(MD5FILE, 'r')
		content = f.readlines()
		f.close()
		for line in content:
			l = line.split(" ")
			md5s[l[0]] = l[1]
		self.orgMD5s = md5s
		return md5s
			
	def readFile(self, filename):
		f=open(filename, 'rb')
		content = f.read()
		f.close()
		return content        
	
	def md5Sum(self, filename):
		try:
			content = self.readFile(filename)
			#print len(content)
		except:
			return
		return md5.new(content).hexdigest()

	def tryGraph(self, tree = None):
		try:
			import pydot
			log().info("pydot found, drawing graphs! beware this can take some time with big graphs!")
			self.drawGraph(tree)
		except ImportError:
			log().error("pydot not found, not drawing graphs")
			pass   
			
	def drawGraph(self, tree = None):
		import pydot
		if not os.path.isdir(GRAPHPATH):
			os.mkdir(GRAPHPATH)
		edges = []
		if tree is None:        
			for filenameA in self.filedeps.keys():
				fileA = self.filedeps[filenameA]
				if REQUIRES in fileA.keys() and FILE in fileA[REQUIRES].keys():
					for rel in fileA[REQUIRES][FILE]:
						e = (filenameA, rel)
						edges.append(e)
			fn = os.path.join(GRAPHPATH, 'alldependencies.png')
		else:
			od = -1
			parents = []
			for t in tree:
				d = t['depth']
				f = t['filename']
				if d > od:
					if len(parents) > 0:
						#print "1", (parents[-1], f)
						edges.append((parents[-1], f))
					parents.append(f)
				elif d == od:
					#print "2", (parents[-2], f)
					edges.append((parents[-2], f))
				elif d < od:
					for i in range(0, od - d + 1):
						del parents[-1]
					#print "3", od - d, (parents[-1], f)
					edges.append((parents[-1], f))
					parents.append(f)
				od = d
			fn = os.path.join(GRAPHPATH, self.dependfilename + '_dependencies.png')
			pass
		
		#edges = [(1,2), (1,3), (1,4), (3,4)]
		graph = pydot.graph_from_edges(edges)
		graph.set_type('digraph')
		graph.simplify = True
		#graph.set("resolution", "320")
		#graph.set("overlap", "scale")
		#graph.set("shape", "box")
		
		for n in graph.get_node_list():
			n.set('fontsize', 8)
			n.set('style', 'filled')
			onlyfilename, ext = os.path.splitext(n.get_name())
			fp = self.getFullPath(n.get_name())
			if fp is None:
				n.set('fillcolor', 'red')
			else:
				if ext == ".truck":
					n.set('fillcolor', 'gold')
					n.set('group', 'truck')
				elif ext == ".load":
					n.set('fillcolor', 'lightyellow')
					n.set('group', 'load')
				elif ext == ".material":
					n.set('fillcolor', 'lightseagreen')
					n.set('group', 'material')
				elif ext == ".terrn":
					n.set('fillcolor', 'forestgreen')
					n.set('group', 'terrain')
				elif ext == ".mesh":
					n.set('fillcolor', 'lightsalmon')
					n.set('group', 'mesh')
				elif ext == ".odef":
					n.set('fillcolor', 'lightsalmon')
					n.set('group', 'object')
				elif ext == ".png" or ext == ".jpg" or ext == ".bmp":
					n.set('fillcolor', 'lightblue')
					n.set('group', 'texture')
			
			
		   
		#graph.set("ranksep", "2")
		#graph.set("splines", True)
		program = "dot" # dot or twopi
		# this takes very long:
		#if len(self.filedeps) > 100:
		#    program = "twopi"
		#    graph.set("overlap", "scale")
		
		graph.write(fn, prog = program, format='png')
		log().info("graph successfull written to " + fn)
		
	def removeRoRDeps(self, notfound):
		rortree = self.loadTree(RORDEPSFILE)
		newfound = {MATERIAL:[], FILE:[]}
		for category in notfound.keys():
			for searchitem in notfound[category]:
				found = False
				for filenameA in rortree.keys():
					if found:
						break
					fileA = rortree[filenameA]
					if PROVIDES in fileA.keys() and category in fileA[PROVIDES].keys():
						for provide in fileA[PROVIDES][category]:
							if provide == searchitem:
								if self.verbose:
									log().info("found missing item in original ror: %s, %s" % (category, provide))
								found = True
								break
				if not found:
					newfound[category].append(searchitem)
		return newfound
		
	def generateCrossDep(self, removeRoRDeps=False):
		crossdep = 0
		notfound = {MATERIAL:[], FILE:[]}
		newtree = copy.deepcopy(self.filedeps)
		for filenameA in self.filedeps.keys():
			fileA = self.filedeps[filenameA]
			for relation in [REQUIRES, OPTIONAL]:
				for type in TYPES:
					if not relation in fileA.keys() or len(fileA[relation]) == 0:
						continue
					for reqfile in fileA[relation][type]:
						found = False
						for filenameB in self.filedeps.keys():
							fileB = self.filedeps[filenameB]
							if filenameA == filenameB:
								continue
							#print filenameA, relation, type, reqfile, fileB[PROVIDES][type]
							if len(fileB[PROVIDES]) == 0:
								continue
							if reqfile in fileB[PROVIDES][type]:
								crossdep += 1
								newtree[filenameB][REQUIREDBY][FILE].append(filenameA)
								if not filenameB in fileA[REQUIRES][FILE]:
									# found new
									newtree[filenameA][REQUIRES][FILE].append(filenameB)
								found = True
								break
						if not found and relation != OPTIONAL:
							if not reqfile in notfound[type]:
								notfound[type].append(reqfile)
		self.filedeps = newtree
		#print  newtree
		self.everythingfound = False
		if len(notfound[MATERIAL]) == 0 and len(notfound[FILE]) == 0:
			self.everythingfound = True
			if self.verbose:
				log().info("### nothing missing, great!")
		else:
			if removeRoRDeps:
				notfound = self.removeRoRDeps(notfound)
			self.notfound = notfound
			if len(notfound[MATERIAL]) == 0 and len(notfound[FILE]) == 0:
				self.everythingfound = True
				if self.verbose:
					log().info("### no files missing, all prior missing files found in RoR")
			if self.verbose:
				if len(notfound[FILE]) > 0:
					log().info("### we are missing the following files:")
					log().info("   "+str(notfound[FILE]))
				if len(notfound[MATERIAL]) > 0:
					log().info("### we are missing the following materials:")
					log().info("   "+str(notfound[MATERIAL]))
		if self.verbose:
			log().info("### found %d files, of which %d have dependencies." % (len(self.files), len(self.filedeps)))
			nodeps = 0
			for filename in self.filedeps.keys():
				file = self.filedeps[filename]
				line = "  %-30s " % filename
				linesub = ""
				sublines = []
				if REQUIRES in file.keys() and FILE in file[REQUIRES].keys():
					linesub = "requires: %s" % (str(file[REQUIRES][FILE]))
				if linesub != "":
					sublines.append("%-50s" % linesub)
					
				linesub = ""
				if REQUIREDBY in file.keys() and FILE in file[REQUIRES].keys():
					linesub = "required by: %s" % (str(file[REQUIREDBY][FILE]))
				if linesub != "":
					sublines.append("%-50s" % linesub)
				if len(sublines) > 0:
					line += ", ".join(sublines)
				else:
					line += "NO DEPENDENCIES"
					nodeps += 1
				log().info(line)
			log().info("### %d files depends on each other" % (crossdep))
			log().info("### %d files with no dependencies" % (nodeps))
			log().info("### advanced file dependency check finished")
			#if len(file[PROVIDES]) == 0
	
	def getDependencies(self, extension, filename):
		try:
			#print "trying to use module: %s" % "ror_" + extension.lstrip(".")
			mod = __import__("ror_" + extension.lstrip("."))
		except ImportError, e:
			#print "module not found!"
			#print e
			return None
			pass            
		return mod.getDependencies(filename)

		
	def getFullPath(self, filename):
		for f in self.files:
			if os.path.basename(f) == filename:
				return f
		return None
	
	def getfiles(self, md5 = False):
		fl = {}
		for root, dirs, files in os.walk(os.path.abspath(self.dir)):
			for f in files:
				fn = os.path.join(root, f)
				fl[fn] = {}
				if md5:
					fl[fn]['md5'] = self.md5Sum(fn)
		if self.verbose:                    
			for fk in fl.keys():
				infostr = "%10s %s" % ("", os.path.basename(fk))
				log().info(infostr)
			log().info("found %d files!" % (len(fl.keys())))
		self.files = fl

	def newRelation(self, dep):
		# ensures that each field exists
		tmp = {}
		for rel in RELATIONS:
			tmp[rel] = {}
			for type in TYPES:
				tmp[rel][type] = []
		for rel in dep.keys():
			for type in dep[rel].keys():
				if type == FILE:
					for f in dep[rel][type]:
						#print f
						tmp[rel][type].append(os.path.basename(f))
				else:
					tmp[rel][type] = dep[rel][type]
		return tmp
		
	def createDeps(self):
		tree = self.filedeps
		unused = []
		if self.verbose:
			log().info("### dependency checker log following")
		for filename in self.files.keys():
			onlyfilename, extension = os.path.splitext(filename)
			basefilename = os.path.basename(filename)
			dependencies = self.getDependencies(extension, filename)
			if dependencies is None:
				unused.append(filename)
			#print "DEP "+ basefilename +" / "+str(dependencies)
			if not dependencies is None:
				for relation in dependencies.keys():
					deps = dependencies[relation]
					tree[basefilename] = {}
					tree[basefilename][relation] = {}
					for type in deps.keys():
						tree[basefilename] = self.newRelation(dependencies)            
		if self.verbose:
			log().info("### file dependency check finished")
			if len(unused) > 0:
				log().info("### unused files: %s" % str(unused))
			else:
				log().info("### all files used")

