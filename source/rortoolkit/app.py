
import rortoolkit.gui
import rortoolkit.resources
import ror.settingsManager

class AppMode:
	"""
	Enum
	"""
	MAIN_MENU             = 0
	TERRAIN_IMPORT_SEARCH = 1

class Application:
	"""
	Application logic of RoRToolkit.
	GUI panels/tools should never perform application logic
	themselves, only invoke callbacks of Application.
	"""

	def __init__(self):
		self._terrain_project_db = {} # project_name => directory
		self._gui_panels = {
			"terrain_project_manager_window": None,
			"terrain_import_selector_window": None
		}
		self._mode = AppMode.MAIN_MENU

	def init_set_main_frame(self, gui_main_frame):
		self._gui_panels["main_frame"] = gui_main_frame

	def open_terrain_projects_window(self):
		window = self._gui_panels["terrain_project_manager_window"]
		if window is None:
			main_frame = self._gui_panels["main_frame"]
			window = rortoolkit.gui.TerrainProjectManagerPanel(main_frame, self)
			self._gui_panels["terrain_project_manager_window"] = window
		def callback_import_fn():
			self.enter_mode(AppMode.TERRAIN_IMPORT_SEARCH)
		window.callback_import_button_pressed = callback_import_fn
		# TODO: Load projects
		window.Show()

	def refresh_terrain_project_db(self):
		pass # To be done

	def enter_mode(self, mode):
		if mode == AppMode.MAIN_MENU:
			if self._mode == AppMode.TERRAIN_IMPORT_SEARCH:
				self._gui_panels["main_frame"].Show()
			self._mode = mode
		elif mode == AppMode.TERRAIN_IMPORT_SEARCH:
			self._enter_mode_terrn_import_select()

	def _enter_mode_terrn_import_select(self):
		self._mode = AppMode.TERRAIN_IMPORT_SEARCH
		# Hide all windows
		self._hide_all_windows()
		# Show terrn import window
		window = self._gui_panels["terrain_import_selector_window"]
		if window is None:
			main_frame = self._gui_panels["main_frame"]
			window = rortoolkit.gui.TerrainImportSelectorWindow(main_frame, self)
			self._gui_panels["terrain_import_selector_window"] = window
		window.set_status_text("Searching for terrains...")
		# Init resources
		res_mgr = rortoolkit.resources.resource_manager_get_singleton()
		res_mgr.init_all_known_resources() # This inits OGRE resource groups
		# Search for terrains
		window.assign_terrains(res_mgr.search_importable_terrains())
		# Callbacks
		def cancel_import_fn():
			self.enter_mode(AppMode.MAIN_MENU)
		window.callback_cancel = cancel_import_fn
		window.Show()

	def _hide_all_windows(self):
		# Hide toolbar windows
		self._gui_panels["main_frame"].hide_all_toolbar_windows()
		# Hide managed windows
		for window in self._gui_panels.values():
			if window is not None:
				window.Hide()
