# Thomas Fischer 31/05/2007, thomas@thomasfischer.biz
# Petr Ohlidal   2016

from ror.settingsManager import *

RENDERSYSTEMS = ['OpenGL', 'DirectX9']
DIRECTXLINE = "Plugin=RenderSystem_Direct3D9.dll"
OPENGLLINE = "Plugin=RenderSystem_GL.dll"
SPLASHIMAGE = rorSettings().getConcatPath(rorSettings().toolkitMainFolder, ["media","gui", "splash.bmp"],True)

def startApp(MainApp):
	from ror.logger import log

	### Callbacks and utils for the startup settings dialog
	
	def callback_homedir_selected(homedir_index, homedirs_list):
		if homedir_index < len(homedirs_list):
			rorSettings().rorHomeFolder = homedirs_list[homedir_index][1]

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
		import ror.rorcommon
		if not ror.rorcommon.checkRoRDirectory(new_installdir):
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
	
	# Create dialog, setup callbacks
	import rortoolkit.gui_panels
	conf_dialog = rortoolkit.gui_panels.StartupSettingsDialog(MainApp, -1, "")
	conf_dialog.set_callback_installdir_updated(callback_installdir_updated)
	conf_dialog.set_callback_renderer_selected(callback_renderer_selected)
	conf_dialog.set_callback_homedir_selected(callback_homedir_selected)
	conf_dialog.set_callback_abort(callback_abort)
	
	# List and check RoR's home directories (raise error if none found)
	import rortoolkit.sys_utils
	homedir_list = rortoolkit.sys_utils.list_ror_home_directories();
	if len(homedir_list) == 0:
		import rortoolkit.exceptions
		msg = "Rigs of Rods was not found on your system."
		if rortoolkit.sys_utils.is_system_windows():
			msg += "\nNo directory [Documents/Rigs of Rods*] found"
		else:
			msg += "\nNo RoR directory found in your user directory"
		raise rortoolkit.exceptions.ToolkitError(msg)
		
	# Setup the settings dialog
	conf_dialog.setup_content("rortoolkit.ico", rorSettings().title, SPLASHIMAGE, RENDERSYSTEMS, 1, homedir_list)
	
	return conf_dialog
