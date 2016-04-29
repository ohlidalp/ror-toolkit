
"""
:author: Petr Ohlidal 'only_a_ptr' 01/2016
"""

import ogre.renderer.OGRE as OGRE

class Mouse3D:
	"""
	Utility class for computing mouse transforms in 3d world.
	
	:author: Petr Ohlidal 'only_a_ptr' 01/2016
	"""

	def __init__(self, ogre_camera, ogre_renderwindow, ogre_scene_manager):
		"""
		"""
		self._ogre_camera = ogre_camera
		self._ogre_renderwindow = ogre_renderwindow
		self._ogre_plane = OGRE.Plane()
		self._ogre_scene_manager = ogre_scene_manager
		
	def create_camera_to_viewport_ray(self, screen_x_pixels, screen_y_pixels):
		"""
		:retuns: ogre.Ray on entered screen coordinates
		"""
		width  = self._ogre_renderwindow.getWidth()
		height = self._ogre_renderwindow.getHeight()
		x_perc = screen_x_pixels / float(width)
		y_perc = screen_y_pixels / float(height)
		return self._ogre_camera.getCameraToViewportRay(x_perc, y_perc)
		
	def query_mouse_terrain_position(self, screen_x_pixels, screen_y_pixels):
		"""
		http://www.comp.hkbu.edu.hk/~comp3080/2011/?page_id=296
		"""
		ray = self.create_camera_to_viewport_ray(screen_x_pixels, screen_y_pixels)
		ray_query = self._ogre_scene_manager.createRayQuery(OGRE.Ray()); # TODO: can't I pass the ray directly?
		ray_query.setRay(ray)
		result = ray_query.execute()
		final = None
		if len(result) > 0 and not result[0] is None and not result[0].worldFragment is None:
			final = result[0].worldFragment.singleIntersection
		self._ogre_scene_manager.destroyQuery(ray_query)
		return final

	def mouse_translate_along_axis(self, pivot_point, axis_ogre, mouse_x1, mouse_y1, mouse_x2, mouse_y2):
		"""
		:param ogre.Vector3   pivot_point :
		:param string{X/Y/Z}  axis_ogre   : OGRE world space (Y = up)
		:returns: Tuple(Success?:bool, ogre.Vector3|None)
		"""
		
		# Prepare plane
		cam2pivot_vec = self._ogre_camera.getPosition() - pivot_point
		cam2pivot_vec.normalise()
		camcos_x = abs(cam2pivot_vec.x)
		camcos_y = abs(cam2pivot_vec.y)
		camcos_z = abs(cam2pivot_vec.z)
		
		if axis_ogre == "X":
			if camcos_y > camcos_z:
				self._ogre_plane.redefine(OGRE.Vector3().UNIT_Y, pivot_point)
				normal_str = "Y"
			else:
				self._ogre_plane.redefine(OGRE.Vector3().UNIT_Z, pivot_point)
				normal_str = "Z"
		elif axis_ogre == "Y":
			if camcos_x > camcos_z:
				self._ogre_plane.redefine(OGRE.Vector3().UNIT_X, pivot_point)
				normal_str = "X"
			else:
				self._ogre_plane.redefine(OGRE.Vector3().UNIT_Z, pivot_point)
				normal_str = "Z"
		elif axis_ogre == "Z":
			if camcos_x > camcos_y:
				self._ogre_plane.redefine(OGRE.Vector3().UNIT_X, pivot_point)
				normal_str = "X"
			else:
				self._ogre_plane.redefine(OGRE.Vector3().UNIT_Y, pivot_point)
				normal_str = "Y"
			
		# Intersect planes
		ray = self.create_camera_to_viewport_ray(mouse_x1, mouse_y1)
		result = ray.intersects(self._ogre_plane)
		if not result.first:
			#print("    DBG mouse3d >> Failed on mouse1 | axis: " + axis_ogre + " | plane_norm: " + normal_str)
			return (False, None)
		point1 = ray.getPoint(result.second)
		
		ray = self.create_camera_to_viewport_ray(mouse_x2, mouse_y2)
		result = ray.intersects(self._ogre_plane)
		if not result.first:
			#print("    DBG mouse3d >> Failed on mouse2 | axis: " + axis_ogre + " | plane_norm: " + normal_str)
			return (False, None)
		point2 = ray.getPoint(result.second)
		
		# Clamp translation to axis
		plane_vec_raw = point2 - point1
		if axis_ogre == "X":
			world_vec = plane_vec_raw * OGRE.Vector3().UNIT_X
		elif axis_ogre == "Y":
			world_vec = plane_vec_raw * OGRE.Vector3().UNIT_Y
		elif axis_ogre == "Z":
			world_vec = plane_vec_raw * OGRE.Vector3().UNIT_Z
		
		#print("    DBG mouse3d >> OK | plane_vec_raw: " + str(plane_vec_raw) + " | world_vec: " + str(world_vec) + " | axis: " + axis_ogre + " | plane_norm: " + normal_str)
		return (True, world_vec)
