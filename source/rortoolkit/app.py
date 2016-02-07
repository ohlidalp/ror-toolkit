
import rortoolkit.gui
import ror.settingsManager

class Application:
	"""
	Application logic of RoRToolkit.
	GUI panels/tools should never perform application logic
	themselves, only invoke callbacks of Application.
	"""
	def __init__(self):
		self._terrain_project_db = {} # project_name => directory
		self._gui_panels = {
			"terrain_project_manager_window": None
		}

	def init_set_main_frame(self, gui_main_frame):
		self._gui_panels["main_frame"] = gui_main_frame

	def open_terrain_projects_window(self):
		window = self._gui_panels["terrain_project_manager_window"]
		if window is None:
			main_frame = self._gui_panels["main_frame"]
			window = rortoolkit.gui.TerrainProjectManagerPanel(main_frame, self)
			self._gui_panels["terrain_project_manager_window"] = window
		# TODO: Load projects
		window.Show()

	def refresh_terrain_project_db(self):
		pass # To be done
