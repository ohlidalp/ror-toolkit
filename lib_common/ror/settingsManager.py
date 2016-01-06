
import wx, os, os.path, sys, ConfigParser
from TrueSingleton import Singleton

# Lepes: Can not use logger here
#from logger import log
#Max98 fix 0.38

CONFIGFILE = "editor.ini"

#===============================================================================
# SECTIONS USED IN EDITOR.INI
#===============================================================================
ROR = 'RigsOfRods'
TOOLKIT = 'TOOLKIT'
TRUCKEDITOR = 'Truck Editor'

#===============================================================================
# keys USED IN EDITOR.INI
#===============================================================================
usePopupToSelect = "use_popup_to_select"
cameraVelocity = "camera_Velocity"
cameraShiftVelocity = "camera_Shift_Multiplier"

class rorSettings(Singleton):
	myConfig = None
	def __str__(self):
		s = ' rorFolder			  %s' % (self._rorFolder) 
		s += ' rorExecutable		  %s' % (self._rorExecutable)  
		s += ' rorFile			  %s' % (self._rorFile)
		s += ' rorFolder			  %s' % (self._rorFolder)  
		s += ' toolkit Main Folder %s' % (self._toolkitMainFolder)  
		s += ' toolkit home Folder %s' % (self._toolkitHomeFolder)
		s += ' editor.ini		  %s' % (self._configFile)
		return s

	def _getRorExecutable(self):
		return self._rorExecutable
		   
	def _setRorExecutable(self, value):
		tmp = self.getSetting(ROR, "rorbinary")
		if tmp == "":
			self._rorExecutable = value
		else:
			self._rorExecutable = tmp
	   
	
	def _getRorFolder(self):
		return self._rorFolder
		   
	def _setRorFolder(self, value):
		self._rorFolder = value
	   
	
	def _getRorFile(self):
		return os.path.join(self._rorFolder, self._rorExecutable)
	
	
	def _getToolkitMainFolder(self):
		return self._toolkitMainFolder
		   
	
	def _getToolkitHomeFolder(self):
		return self._toolkitHomeFolder
	
	def _getMainApp(self):
		if self._mainApp is None:
			raise Exception("not assigned MainApp yet in Settings Manager !!!")
		return self._mainApp
		   
	def _setMainApp(self, value):
		self._mainApp = value
	def _setStopOnExceptions(self, value):
		self._stopOnExceptions = value
	def _getStopOnExceptions(self):
		return self._stopOnExceptions
	
	
	def _getrorDebug(self):
		return self._rorDebug
		   
	def _setrorDebug(self, value):
		self._rorDebug = value
	   
	def _getRorHomeFolder(self):
		return self._rorHomeFolder
		   
	def _setRorHomeFolder(self, value):
		self._rorHomeFolder = value
	
	def _gettitle(self):
		return self._title
		   
	def _settitle(self, value):
		self._title = value
	   
	title = property(_gettitle, _settitle,
					 doc="""TiTle of main window""")
	
	rorDebug = property(_getrorDebug, _setrorDebug,
					 doc="""Boolean to print some debug stuff
							 
							 It also load a map and setup Main Window hardcoded size.
							 """)
	
	stopOnExceptions = property(_getStopOnExceptions, _setStopOnExceptions,
					 doc="""Toolkit should pass most exceptions in normal cases but
					 		in debug mode, it is useful to stop on Exceptions to see 
					 		source line of code that launch the first exception""")
	   
	mainApp = property(_getMainApp, _setMainApp,
					 doc=""" Store a pointer to Main Frame just to launch Exceptions and Messages
					 		 in a wx.MessageBox to the final user""")
	
	toolkitHomeFolder = property(_getToolkitHomeFolder,
					 doc="""toolkit path to 'My Documents' or /home """)
	
	toolkitMainFolder = property(_getToolkitMainFolder,
					 doc="""toolkit path to program files folder""")
	
	rorFile = property(_getRorFile,
					 doc="""RoR absolute path and filename """)
	
	rorFolder = property(_getRorFolder, _setRorFolder,
					 doc="""RoR folder where the binary file is""")

	rorHomeFolder = property(_getRorHomeFolder, _setRorHomeFolder,
					 doc=""" My Documents\Rigs of Rods 0.38 """)
	
	rorExecutable = property(_getRorExecutable, _setRorExecutable,
					 doc="""only filename of the executable RoR.bin / RoR.exe
					 		First time Toolkit is ran, it would have one of this values
					 		but if exist a setting "RoRbinary" in editor.ini file it will be
					 		used instead RoR.bin/ RoR.exe.
					 		""")
	
	
	# only run once where constructor is called first time
	# because it is a Subclass of Singleton Class
	def init(self):
		self.initProperties()
		self.retrievePaths()
		self.loadSettings()
	
	def initProperties(self):
		self._rorFolder = ''
		self._rorExecutable = ''
		self._toolkitHomeFolder = ''
		self._toolkitMainFolder = ''
		self._mainApp = None
		self._stopOnExceptions = False
		self._rorDebug = True
		self._title = "Rigs of Rods Toolkit 0.38 R2"
		self.onlyParseTrucks = False
	
	def retrievePaths(self):
		""" - get independent platform paths 
			- set up basic properties
			- create Editor.ini file
			- create logging.ini file for logger.py 
		"""
		self._toolkitMainFolder = self.getConcatPath(os.path.dirname(os.path.abspath(__file__)), ["..", ".."])
		sp = wx.StandardPaths.Get()
		ror = "Rigs of Rods 0.38"
		toolkit = "Rigs of Rods Toolkit 0.38"
		if self.getPlatform() == 'linux':
			ror = ror.replace(" ", "")
			toolkit = toolkit.replace(" ", "")
			
		self._toolkitHomeFolder = self.getConcatPath(sp.GetDocumentsDir(), [toolkit])
		self._rorHomeFolder = os.path.join(sp.GetDocumentsDir(), ror)
		if not os.path.isdir(self._rorHomeFolder):
			print "RoR Home folder not found in OS home dir. Do you have RoR 0.38 or up installed?"
	
		self._configFile = self.concatToToolkitHomeFolder(["config", CONFIGFILE], True)
		
		logfile = self.concatToToolkitHomeFolder(['logs', 'editor.log'], True)
		if not os.path.isfile(logfile):
			print "creating %s" % logfile
			f = open(logfile, "w")
			f.close()
		ogrefile = self.concatToToolkitHomeFolder(['logs', 'Ogre.log'], True)
		if not os.path.isfile(ogrefile):
			print "creating %s" % ogrefile
			f = open(ogrefile, "w")
			f.close()

		filename = self.concatToToolkitHomeFolder(['logs', 'logging.ini'], True)
		if not os.path.isfile(filename):
			print "creating %s using encoding: %s " % (filename, sys.getdefaultencoding())
			f = open(filename, "w")
			f.write(self.loggingContent.encode('utf-8'))
			f.write("args=( '%s', 'w')\n" % (logfile.replace('\\', '//').encode('utf-8')))
			f.write(self.logging2.encode('utf-8'))
			f.close()
			
			
					
	def loadSettings(self):
		try:
			self.myConfig = ConfigParser.ConfigParser()
			self.myConfig.read(self._configFile)
			self._rorFolder = self.getSetting(ROR, 'BasePath')
			print "Settings loaded"
		except Exception, e:
			print str(e)

	def getPlatform(self): # copied from rorcommon
		""" return a string, posible values are:
		'linux'
		'windows'
		'unkown'
		"""
		
		if sys.platform in ['linux', 'linux2']:
			return 'linux'
		elif sys.platform in ['win32', 'win64']:
			return 'windows'
		return 'unkown'
	
	def getSetting(self, group, key):
		try:
#			print "Retrieving Settings: %s - %s." %(group, key) )
			return self.myConfig.get(group, key)
		except Exception, e:
			print str(e)
			self.setSetting(group, key, "")
			return ""

	def saveSettings(self):
		try:
			fp = open(self._configFile, 'w')
			self.myConfig.write(fp)
			fp.close()
			print "Settings saved"
		except Exception, e:
			print str(e)
			
	def has_section(self, section):
		return self.myConfig.has_section(section)
	
	def has_key(self, section, key):
		return self.myConfig.has_option(section, key)


	def setSetting(self, section, option, value, autoSaveFile=True):
		try:
			if not self.myConfig.has_section(section):
				self.myConfig.add_section(section)
			self.myConfig.set(section, option, str(value))
			if autoSaveFile:
				self.saveSettings()
			return True
		except Exception, e:
			return False
	
	def getConcatPath(self, strAbsPath, values=[], isFile=False):
		""" Concat multiple paths
  		  and create whole folder structure if needed
		  (that's the difference with os.path.join)
		  
		  need to know if you are supplying a File or a folder
		  
		  returning absolute resulting path or file """	   
		s = strAbsPath
		file = values[len(values) - 1]
		for t in range(0, len(values) - 1):
			s = os.path.join(s, values[t])
		
		if not isFile:
			s = os.path.join(s, file)
		
		s = os.path.abspath(s)
		if not os.path.isdir(s):
			os.makedirs(s)
		if isFile:
			s = os.path.join(s, file)
		return os.path.abspath(s)

	def concatToRorFolder(self, values=[], isFile=False):
		""" Concat multiple paths to RoR "program files" folder
  		  and create whole folder structure if needed
		  (that's the difference with os.path.join)
		  
		  need to know if you are supplying a File or a folder
		  
		  returning absolute resulting path or file """	   		
		return self.getConcatPath(self.rorFolder, values, isFile)
	
	def concatToToolkitHomeFolder(self, values=[], isFile=False):
		""" Concat multiple paths to "My Documents\Rigs of Rods Toolkit" folder
  		  and create whole folder structure if needed
		  (that's the difference with os.path.join)
		  
		  need to know if you are supplying a File or a folder
		  
		  returning absolute resulting path or file """	   
		return self.getConcatPath(self._toolkitHomeFolder, values, isFile)
		 

# I don't want to supply 'logging.ini' in the installer
# because we need to touch it to configure 'editor.log' path.
# On the other hand, I'm sure I will forget to include this file in the installer package ;)

	loggingContent = """
#lines with # are comments!
#please refer to http://docs.python.org/lib/logging-config-fileformat.html

#list of loggin-targets
[loggers]
keys=root

#list of handlers
[handlers]
keys=consolelog,filelog

#list of formatters
[formatters]
keys=full,short

#main logging-target
[logger_root]
level=NOTSET
handlers=consolelog,filelog

[handler_filelog]
class=FileHandler
level=DEBUG
formatter=full
"""

	logging2 = """

#console-output-handler
[handler_consolelog]
class=StreamHandler
level=DEBUG
formatter=short
args=(sys.stdout,)

#logging formats
[formatter_full]
format=%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(message)s
datefmt=

[formatter_short]
format=%(asctime)s | %(levelname)s | %(message)s
datefmt=
	"""
