DESC = f"""{__file__} - A code sample to help get you started with proceedurally generated terrain / chunkloading in Ursina.
More complex terrain can be achieved by using a more complicated function in GameWithChunkloading.get_heightmap().
Supports both Perlin Noise and Open Simplex Noise.
Written by Lyfe.
"""

TERRAIN_X_Z_SCALE = 0.5 #Higher numbers yield rougher terrain
TERRAIN_Y_SCALE = 5 #Terrain Y amplification, results in y values in the range of +- MAP_MODEL_SCALE
CHUNK_DIVISIONS = 5 #Number of subdivisions per tile, more divisions is more detail
DEFAULT_NUM_GENERATORS = 1
RENDER_DISTANCE = 4
MAP_SCALE = 6 #how big the tiles are
USE_PERLIN = True

import os, json, random
import numpy as np
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

#This class is a trimmed version of terrain.py that takes a numpy array directly rather than an image
class HeightMesh(Mesh):
	def __init__(self, heightmap):
		heightmap = np.swapaxes(heightmap,0,1)
		self.vertices, self.triangles, self.uvs, self.normals = list(), list(), list(), list()
		lhm = len(heightmap)
		l=lhm-1
		i = 0
		for z in range(lhm):
			for x in range(lhm):
				self.vertices.append(Vec3(x/l, heightmap[x][z], z/l))
				self.uvs.append((x/l, z/l))
				if x > 0 and z > 0:
					self.triangles.append((i, i-1, i-l-2, i-l-1))
					if x < l-1 and z < l-1:
						rl = heightmap[x+1][z] - heightmap[x-1][z]
						fb = heightmap[x][z+1] - heightmap[x][z-1]
						self.normals.append(Vec3(rl, 1, fb).normalized())
				i += 1
		super().__init__(vertices=self.vertices, triangles=self.triangles, uvs=self.uvs, normals=self.normals)

#This entity is a base, when writing a game you would want to do stuff like spawning foliage etc when the chunk is initialized.
class Chunk(Entity):
	def __init__(self, game, chunk_id, heightmap, **kwargs):
		Entity.__init__(self, model=HeightMesh(heightmap),**kwargs)
		self.game, self.chunk_id, self.heightmap, self.collider, = game, chunk_id, heightmap, self.model
	def save(self):
		#You could implement a more complicated save system here,
		#adding more to the chunk save than just the heightmap
		#You would also need to add something during the chunk init that
		#checked if a save file existed for it and if so loaded that
		#save data
		x,z = self.chunk_id
		filename = self.game.saves_dir+f"{x}x{z}#{self.game.seed}.json"
		with open(filename, "w+") as f:
			json.dump({"heightmap":self.heightmap}, f)

#A basic example of dynamic terrain generation and chunkloading
#More generators will result in smoother terrain
#The seed determines the terrain that spawns, leave empty for random
class GameWithChunkloading(Ursina):
	def __init__(self,*args,**kwargs):
		#Set defaults
		self.seed = random.randint(1,9999999999) #Random overwritten by kwargs
		self.radius = RENDER_DISTANCE
		self.use_perlin = USE_PERLIN
		self.chunk_divisions = CHUNK_DIVISIONS
		self.terrain_scale = TERRAIN_X_Z_SCALE
		self.terrain_y_scale = TERRAIN_Y_SCALE
		self.map_scale = MAP_SCALE
		self.num_generators = DEFAULT_NUM_GENERATORS
		self.enable_save_system = False
		self.saves_dir="saves"
		#Override passed non-defaults
		for key in ('seed', 'use_perlin', 'radius', 'chunk_divisions',\
				'terrain_scale', 'terrain_y_scale', 'map_scale',\
				'num_generators', 'enable_save_system', 'saves_dir'):
			if key in kwargs:
				setattr(self, key, kwargs[key])
				del kwargs[key]
		super().__init__(*args, **kwargs)
		##Chunkloading
		self.loaded = [] # loaded chunks
		self.last_chunk = None #Last place chunkload occured
		##Terrain Generation
		print(f"Using seed {self.seed}")
		if self.use_perlin:
			print("Using Perlin Noise")
			from perlin_noise import PerlinNoise
			self.generators = [PerlinNoise(seed=self.seed,octaves=self.num_generators)]
		else:
			print("Using Open Simplex")
			from opensimplex import OpenSimplex
			self.generators = [OpenSimplex(seed=(self.seed + i)*(i+1)).noise2 for i in range(self.num_generators)]
		##Save system
		if self.enable_save_system:
			self.saves_dir = "saves/"
			os.makedirs(self.saves_dir, exist_ok=True) #Make saves dir
		self.player = FirstPersonController(model='cube', z=-10, color=color.clear, origin_y=-.5, speed=8)
		self.player.collider = BoxCollider(self.player, Vec3(0,1,0), Vec3(1,2,1))
		self.player.y = self.get_heightmap(0,0)*self.map_scale*self.terrain_y_scale+1 #Ensure player is above map when spawned
		self.update() #Build terrain for first time
	def get_chunk_id_from_position(self,x,z):#Takes an x/z position and returns a chunk id
		return int(x/MAP_SCALE),int(z/MAP_SCALE)
	def get_heightmap(self,x,z):#Get terrain y at a given x/z position
		pos = (x*self.terrain_scale,z*self.terrain_scale) #Get adjusted position in heightmap
		#Get the sum of the heights for all generators at a given position
		#If using perlin noise this is handled internally using 'octaves' option
		height = sum(g(pos) if self.use_perlin else g(*pos) for g in self.generators)
		if len(self.generators)>1: height /= len(self.generators) #scale output back to range of [-1...1]
		return height
	def update(self): #update which chunks are loaded
		current = self.get_chunk_id_from_position(self.player.position.x, self.player.position.z)
		if current == self.last_chunk: return #Don't update if in same chunk as last update
		needed_chunk_ids = [] #List of chunks that should currently be loaded
		for z in range(int(current[1]-self.radius),int(current[1]+self.radius)):
			for x in range(int(current[0]-self.radius),int(current[0]+self.radius)):
				needed_chunk_ids.append((x,z))
		for c in self.loaded.copy(): #Remove unneeded chunks
			if c.chunk_id not in needed_chunk_ids:
				cid = c.chunk_id
				self.loaded.remove(c)
				destroy(c)
				print(f"Unloaded chunk {cid}")
		current_chunk_ids = [c.chunk_id for c in self.loaded]
		for chunk_id in needed_chunk_ids: #Show the needed chunks
			if not chunk_id in current_chunk_ids:
				x,z=chunk_id
				heightmap = []
				chunk_needs_save = False #Flag for if a chunk is new and needs to be saved
				if self.enable_save_system:
					filename = self.saves_dir+f"{x}x{z}#{self.seed}.json"
					#Check if saved chunk already exists:
					if os.path.exists(filename):
						print(f"Found saved chunk {chunk_id}")
						with open(filename, 'r') as f:
							heightmap = json.load(f)["heightmap"]
					else:
						heightmap = self.generate_chunk_heightmap(x,z)
						chunk_needs_save = True					
				else:
					heightmap = self.generate_chunk_heightmap(x,z)
				c = Chunk(
					self,
					chunk_id = chunk_id,
					heightmap=list(heightmap),
					scale=self.map_scale,
					scale_y=self.terrain_y_scale,
					texture="white_cube",
					position=(x*self.map_scale,0,z*self.map_scale)
					)
				self.loaded.append(c)
				if chunk_needs_save: c.save() #Save chunk if newly loaded
				print(f"Loaded chunk {chunk_id}")
		self.last_chunk = current #Update last rendered chunk to prevent unneeded re-draws
	def generate_chunk_heightmap(self,x,z):
		heightmap = []
		for _z in range(self.chunk_divisions+1):
			heightmap_row = []
			for _x in range(self.chunk_divisions+1):
				heightmap_row.append(self.get_heightmap(x+_x/self.chunk_divisions,z+_z/self.chunk_divisions))
			heightmap.append(heightmap_row)
		return heightmap

if __name__ == "__main__":
	import argparse
	parser = argparse.ArgumentParser(description=DESC)	
	parser.add_argument("-s", "--seed", help = "Select terrain seed. No seed / a seed of zero results in a random seed. (Int)")
	parser.add_argument("-d", "--divisions", help = "Number of divisions per chunk edge. (Int)")
	parser.add_argument("-r", "--renderdistance", help = "Render distance radius in chunks. (Int)")
	parser.add_argument("-t", "--terrainscale", help = "Higher values yield rougher terrain. (Float)")
	parser.add_argument("-y", "--yscale", help = "Terrain Y amplification. (Float)")
	parser.add_argument("-m", "--mapscale", help = "Length of chunk edge. (Float)")
	parser.add_argument("-n", "--numgenerators", help = "Length of chunk edge. (Float)")
	parser.add_argument("-l", "--loadchunks", action='store_true', help="Enable example chunk save/load system.")
	parser.add_argument("-o", "--opensimplex", action='store_true', help = "Set this flag to use Open Simplex Noise rather than Perlin Noise")
	args = parser.parse_args()
	kwargs = {}
	if args.seed: kwargs["seed"]= int(args.seed)
	if args.opensimplex: kwargs["use_perlin"]=not bool(args.opensimplex)
	if args.renderdistance: kwargs["radius"]= int(args.renderdistance)
	if args.divisions: kwargs["chunk_divisions"]= int(args.divisions)
	if args.terrainscale: kwargs["terrain_scale"]= float(args.terrainscale)
	if args.yscale: kwargs["terrain_y_scale"]= float(args.yscale)
	if args.mapscale: kwargs["map_scale"]= float(args.mapscale)
	if args.loadchunks: kwargs["enable_save_system"]=bool(args.loadchunks)
	num_terrain_generators = args.numgenerators or DEFAULT_NUM_GENERATORS
	app = GameWithChunkloading(**kwargs)
	update = app.update
	app.run()