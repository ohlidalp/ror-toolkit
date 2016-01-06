# Lepes: 
#===============================================================================
# 
#===============================================================================

import wx, os, os.path, copy, re
from decimal import *
import ogre.renderer.OGRE as ogre
from logger import log
from settingsManager import *
from ror.rorcommon import *
from lputils import *
from luabasic import *

class luaClass(object):
	""" Lua Parser class that maintain races"""
	
	def __init__(self, terrnFile, ogreWin):
		self._initVariables()
		self._ogreWin = ogreWin
		self.filename = terrnFile + ".lua"

		self.content = loadResourceFile(self.filename)
		if len(self.content) > 0:
			self.parse()
			
	def _initVariables(self):
		self.startScanLine = 0
		self.races = []
		self.showingcheckpoints = False
		self.content = []
		self.oldFormat = False
		self.modified = False
		self.warnings = []
		self.raceIndex = 0
	
	def __del__(self):
		self._initVariables()
	
	def isEmpty(self):
		return len(self.content) == 0
	
	def parse(self):
		i = 0
		while i < len(self.content):
			line = self.content[i].replace(" ", "").lower()
			if line.find("--toolkitscanbeginhere") > -1:
				self.startScanLine = i	   
			if self.startScanLine > 0 and line.find("setuprace(") > -1:
				self.newRace(self.content[i], line.find("setuprace("))
			i += 1
				
		self.oldFormat = self.startScanLine == 0
		log().debug("Found %d races in .lua file" % len(self.races))
		
	def newRaceFromTitle(self, title=""):
		if title.strip() == "":
			raise showedWarning("Race title must have at least one char.\n\nRace have not being created.")

		title = title.replace("|", "") #used in lua as a separator
		coded = title.replace(" ", "") 
		line = "setupRace( '%s', %s_checkpoints, %s_gates, false, false, false, 0.0 )" % (title, coded, coded)
		pos = 10
		return self.newRace(line, pos, True)
		
		
	def newRace(self, line, pos, isRuntimeRace=False):
		""" line - original line of setuRace( racename....
			pos - index of the open parhenthesis 
			isRuntimeRace - True if the race is been created from interface (not loaded from file)
			
			return True if succefully created, False otherwise or exception launched
		"""
		c = line.find(")")
		if c == -1:
			params = []
		else:
			params = line[pos:c].split(",")
#	--SetupRace has several parameters:
#	--  racename to show on screen (no spaces nor underscore)
#	--  array of checkpoints positions
#	-- is loop ? true or false (in lowercase, please)
#	--  Print Altitude of the next checpoint on screen ? true or false (in lowercase, please)
		r = raceClass(self)
		try:
			r.name = params[0][params[0].find("'") + 1 :params[0].rfind("'")]
			r.pointsVar[0] = params[1].replace(" ", "") 
			r.isLoop = params[2] == "true"
			r.showAltitude = params[3] == "true"
			if not isRuntimeRace:
				self._getRange(r.pointsVar)
				self._parseArray(r.pointsVar, r, r.points)
		except Exception:
			del r
			return False
		else:
			self.races.append(r)
			self.modified = isRuntimeRace
			return True

	
	def _parseArray(self, options, race, save):
		""" array of checkpoints of a race
		options - _getRange result, detect where this array start, end and if it is OK.
		race - the race 
		save - where the points of the race must be saved
		"""
		
		if options[1] == True:
			start = options[2] 
			finish = options[3] 
			for i in range(start, finish): #index are ok
				# delete invalid chars { } '
				# line is: {x, y, z, rx, ry, rz, 'gatename'},
				line = self.content[i].replace("{", "").replace("}", "").replace("'", "").strip().split(",")
				p = positionClass()
				p.asTuple = float(line[0]), float(line[1]), float(line[2])
				rot = rotationClass()
				rot.asTuple = float(line[3]), float(line[4]), float(line[5])
				gatename = line[6].replace("'", "").replace('"', '').replace(' ', '')
				save.append({'pos': p, 'rot': rot, 'entry':None, 'gate':gatename})
				
	def _getRange(self, text):
		""" detect where a checkpoint list start 
		
		text - name of checkpoint var or gates var
		it will add 3 values to the text (that is a list):
		booleanOk   -> if file was parsed without error
		startIndex  -> first line of lua file where began the 'text' parsed
		finishIndex -> last line of lua file where this section finish.
		
		"""
		start = 0
		finish = 0
		for i in range(self.startScanLine, len(self.content)):
			line = self.content[i].replace(" ", "")
			if line == (text[0] + "={"):  
				start = i + 1
			if start != 0 and line == "}":
				finish = i
				break
		ok = start != 0 and finish != 0
#		log().debug("checkpoints list for race  '%s': start %d finish %d" % (text[0], start, finish))
		text[1] = ok
		text[2] = start
		text[3] = finish
	
	def getRaceList(self):
		""" return a list with race names"""
		l = []
		for r in self.races:
			l.append(r.name)
		return l
	def getCheckpointList(self, irace):
		""" get a list to put in the interface
		irace - the integer index of races list
		"""
		r = []
		if irace >= len(self.races):
			return r # new race
#			msg = "Toolkit Error: trying to get a checkpoint from race that doesn't exists (bad index %d, actual length %d " % (irace, len(self.races))
#			raise showedError(msg)
		therace = self.races[irace]
		if len(therace.points) > 0:
			for i in range(len(therace.points)):
				line = " %.3d - %s " % (i, therace.points[i]['gate'])
				r.append(line)
			self.raceIndex = irace
			therace.showCheckpoints(True)
		return r
	def save(self, terrnFilename):
		""" filename choosen on Save As dialog"""
		onlyfile = os.path.split(terrnFilename)[1] + '.lua'
		terrnFilename += '.lua'
		if terrnFilename != ".lua" and len(self.races) > 0:
			newcontent = []
			newcontent.append(basicText)
			newcontent.insert(0, cache % onlyfile)
			for r in self.races:
				r.saveTo(newcontent)
			newcontent.append(fileend % onlyfile)				
			f = open(terrnFilename, 'w')
			f.writelines(newcontent)
			f.close()
			log().info('saved %d races on %s' % (len(self.races), terrnFilename))
			if len(self.warnings) > 0 :
				self.warnings.insert(0, "Some races not saved:")
				ShowInfo('LUA', "\n".join(self.warnings))
				self.warnings = []
	
	def deleteRace(self, raceIndex):
		""" need to delete callback """
		self._ogreWin.selected.entry = None
		r = self.races[raceIndex]
		try:
			for c in r.points:
				if c['entry'] is not None:
					r.deleteCallback(c['entry'])
					self._ogreWin.entries.pop(str(c['entry'].uuid))
					c['entry'].removeFromScene()
					del c['entry']
		finally:
			self.races.__delitem__(raceIndex)
			self.modified = True
			self._ogreWin.renderWindow.update()
	
		
				
class raceClass(object):
	
   
	def __init__(self, owner):
		self.clear()
		self.owner = owner
		
	def clear(self):
		self.points = [] # dict: 'pos': positionClass, 'rot': rotationClass, 'entry':None
		self.gates = []
		# pointsVar = ['lua_checkpoint_var', ok, start, finish] 
		self.pointsVar = ["", False, 0, 0]
		self.gatesVar	 = ["", False, 0, 0]
		
	def __del__(self):
		self.clear()
		
	def _getname(self):
		return self._name
		   
	def _setname(self, value):
		self._name = value
		self.owner.modified = True
	
	def _getisLoop(self):
		return self._isLoop
		   
	def _setisLoop(self, value):
		self._isLoop = value
		self.owner.modified = True
	
	
	def _getshowAltitude(self):
		return self._showAltitude
		   
	def _setshowAltitude(self, value):
		self._showAltitude = value
		self.owner.modified = True
	
	showAltitude = property(_getshowAltitude, _setshowAltitude,
					 doc="""Boolean""")
	
	isLoop = property(_getisLoop, _setisLoop,
					 doc="""Boolean""")
	
	name = property(_getname, _setname,
					 doc="""String with the name of the race without quotes""")
	
	def addCheckpoint(self, gate, pos, rot, entry):
		p = positionClass()
		p.asTuple = pos
		r = rotationClass()
		r.asTuple = rot
		self.points.append({'entry': entry, 'pos':p, 'rot':r, 'gate':entry.data.name})
		entry.OnPositionChanging.append(self.checkAlive)
		self.owner.modified = True
		
	def showCheckpoints(self, value=True):
		""" show or hide checkpoints of this race"""
		try:
			self.owner.showingcheckpoints = True
				
			for i in range(len(self.points)):
				if self.points[i]['entry'] is None and value:
					self.points[i]['entry'] = self.owner._ogreWin.addGeneralObject(self.points[i]['gate'] + '.odef',
																				 self.points[i]['pos'].asTuple,
																				 self.points[i]['rot'].asTuple)
					#set up callback, just a pointer to the method
				elif not self.points[i]['entry'] is None:
					self.points[i]['entry'].visible = value
		finally:
			self.owner.showingcheckpoints = False
		
	
	def checkAlive(self, entry):
		""" Once Checkpoints are spawned on terrain, whenever user modify  
			position/rotation this method will be executed to test if he
			deleted the checkpoint
		"""
		# luaClass has been modified, need to be saved.
		self.owner.modified = True
		if entry.deleted:
			self.deleteCallback(entry)
			found = False
			for i in range(0, len(self.points)):
				if self.points[i]['entry'] == entry:
					found = True
					break
			if found:
				self.points.__delitem__(i)
				self.owner._ogreWin.race.updateCheckpoints()
				
	def deleteCallback(self, entry):
		if  len(entry.OnPositionChanging) > 0:
			for i in range(len(entry.OnPositionChanging)):
				if entry.OnPositionChanging[i] == self.checkAlive:
					# delete callback
					entry.OnPositionChanging.__delitem__(i)
					break

	def saveTo(self, content):		  
		if len(self.points) < 2:
			self.owner.warnings.append("- race %s have less than 2 checkpoints. Race not saved" % self.name)
		else:
			# adding points
			content.append("\n%s = {\n" % self.pointsVar[0])
			for p in self.points:
				if not p['entry'] is None:
					p['pos'].asTuple = p['entry'].position
					p['rot'].asTuple = p['entry'].rotation
				content.append("{%s, %s, '%s'},\n" % (p['pos'].format2(), p['rot'].format2(), p['gate']))
			content[-1] = content[-1][:-2] + '\n' # remove last colon
			content.append("}\n\n")
			# adding custom gates
#			content.append("\n%s = {\n" % self.gatesVar[0])
#			for p in self.gates:
#				content.append("'%s',\n" % p)
#			content.append("}\n\n")
			coded = self.name.replace(" ", "") 
	
	#	-- is loop ? true or false (in lowercase, please)
	#	--  Print Altitude of the next checpoint on screen ? true or false (in lowercase, please)
	#	-- use penalization of 10 seconds if collide with the air Race checkpoint? true or false (in lowercase, please)
	#	--	 Note: to be able to use penalization, you need a "penalty" event. Check AirRace.odef file
	#	-- penalty Time - penalization in seconds to sum
	
			line = "setupRace( '%s', %s, %s, %s)\n" % (self.name,
													  self.pointsVar[0],
													  str(self.isLoop).lower(),
													  str(self.showAltitude).lower())
			content.append(line)

			
