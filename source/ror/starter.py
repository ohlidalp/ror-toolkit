# Thomas Fischer 31/05/2007, thomas@thomasfischer.biz

# System imports
import wx, os, os.path
from subprocess import Popen
import subprocess

# External libs
from wxogre.OgreManager import *

# Internal libs
from ror.RoROgreWindow import *
from ror.rorcommon import *
from ror.logger import log
from ror.settingsManager import *
import roreditor.MainFrame
import roreditor.ShapedControls 

RENDERSYSTEMS = ['OpenGL', 'DirectX9']
DIRECTXLINE = "Plugin=RenderSystem_Direct3D9.dll"
OPENGLLINE = "Plugin=RenderSystem_GL.dll"
SPLASHIMAGE = rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ["media","gui", "splash.bmp"],True)

def startApp(MainApp):

	### Callbacks and utils for the startup settings dialog

	def update_renderer_configfile(rend_index, rend_list):
		log().debug("update_renderer_configfile(): retrieving plugins_windows.cfg")
		filename = os.path.join(os.getcwd(), "plugins_windows.cfg")
		f=open(filename, 'r')
		content = f.readlines()
		f.close()
		log().info("selected rendersystem: %s" % rend_list[rend_index])
		for i in range(0, len(content)):
			if content[i].find(DIRECTXLINE) >= 0:
				if rend_index == 1:
					content[i] = DIRECTXLINE+"\n"
				else:
					content[i] = "#"+DIRECTXLINE+"\n"
			elif content[i].find(OPENGLLINE) >= 0:
				if rend_index == 0:
					content[i] = OPENGLLINE+"\n"
				else:
					content[i] = "#"+OPENGLLINE+"\n"
	
		f=open(filename, 'w')
		f.writelines(content)
		f.close()
		
	def callback_installdir_updated(new_installdir):
		if not checkRoRDirectory(new_installdir): # rorcommon.checkRoRDirectory()
			return False
	
		rorSettings().setSetting("RigsOfRods", "BasePath", new_installdir)
		rorSettings().rorFolder = new_installdir
		return True	
	
	def callback_renderer_selected(rend_index, rend_list):
		update_renderer_configfile(rend_index, rend_list)
		
	def callback_abort():
		print("aborting....")
		sys.exit(0)
		
	### The startup settings dialog
	
	# Lepes: No new application needed, just a ShowModal() Frame
	#	MainApp = wx.PySimpleApp()
	#	wx.InitAllImageHandlers() #you may or may not need this
	import rortoolkit.gui_panels
	conf_dialog = rortoolkit.gui_panels.StartupSettingsDialog(MainApp, -1, "")
	conf_dialog.set_callback_installdir_updated(callback_installdir_updated)
	conf_dialog.set_callback_renderer_selected(callback_renderer_selected)
	conf_dialog.set_callback_abort(callback_abort)
	conf_dialog.setup_content(rorSettings().title, SPLASHIMAGE, RENDERSYSTEMS, 1)

	# add icon to the window
	icon = wx.Icon("rortoolkit.ico", wx.BITMAP_TYPE_ICO)
	conf_dialog.SetIcon(icon)
	
	return conf_dialog
