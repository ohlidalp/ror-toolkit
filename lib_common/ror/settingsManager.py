import os, os.path, sys, ConfigParser
import logger

CONFIGFILE = "editor.ini"

# singleton pattern
_rorsettings = None
def getSettingsManager():
	global _rorsettings
	if _rorsettings is None:
		_rorsettings = RoRSettings()
	return _rorsettings

class RoRSettings:
	myConfig = None
	configfilename  = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),"..", "..")),CONFIGFILE)
	#configfilename = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIGFILE)

	def __init__(self):
		self.loadSettings()

	def loadSettings(self):
		try:
			self.myConfig = ConfigParser.ConfigParser()
			self.myConfig.read(self.configfilename)
			logger.log().info("Settings loaded")
		except Exception, e:
			logger.log().exception(str(e))

	def getSetting(self, group, key):
		try:
			return self.myConfig.get(group, key)
		except Exception, e:
			logger.log().exception(str(e))
			return ""

	def saveSettings(self):
		try:
			fp = open(self.configfilename, 'w')
			self.myConfig.write(fp)
			fp.close()
			logger.log().info("Settings saved")
		except Exception, e:
			logger.log().exception(str(e))

	def setSetting(self, section, option, value):
		try:
			if not self.myConfig.has_section(section):
				self.myConfig.add_section(section)
			self.myConfig.set(section, option, value)
			self.saveSettings()
			return True
		except Exception, e:
			logger.log().exception(str(e))
			return False
