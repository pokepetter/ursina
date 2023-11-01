class BoxShape:
	def __init__(self, center=(0,0,0), size=(1,1,1)):
		self.center = center
		self.size = size
		self.properties = {
			'shape': 'box',
			'center': self.center,
			'size': self.size
		}

	def getProperties(self):
		return self.properties


class SphereShape:
	def __init__(self, center=(0,0,0), radius=.5):
		self.center = center
		self.radius = radius
		self.properties = {
			'shape': 'sphere',
			'center': self.center,
			'radius': self.radius
		}

	def getProperties(self):
		return self.properties


class CapsuleShape:
	def __init__(self, center=(0,0,0), radius=.5, height=2, axis='y'):
		self.center = center
		self.radius = radius
		self.height = height
		self.axis = axis
		self.properties = {
			'shape': 'capsule',
			'center': self.center,
			'radius': self.radius,
			'height': self.height,
			'axis': self.axis
		}

	def getProperties(self):
		return self.properties


class MeshShape:
	def __init__(self, mesh=None, center=(0,0,0)):
		self.mesh = mesh
		self.center = center
		self.properties = {
			'shape': 'mesh',
			'mesh': self.mesh,
			'center': self.center
		}

	def getProperties(self):
		return self.properties


class CompoundShape:
	def __init__(self, shapes=[], center=(0,0,0)):
		self.shapes = shapes
		self.center = center
		self.properties = {
			'shape': 'compound',
			'shapes': [],
			'center': self.center
		}

		for s in self.shapes:
			self.properties['shapes'].append(s.getProperties())

	def getProperties(self):
		return self.properties