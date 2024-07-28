from panda3d.core import (
    Geom,
    GeomVertexArrayFormat,
    GeomVertexFormat,
    GeomVertexWriter,
    OmniBoundingVolume,
)
from dataclasses import dataclass
from typing import List
from ursina import *


@dataclass
class Particle:
    position: Vec3
    velocity: Vec3

    lifetime: float
    delay: float

    init_scale: Vec2
    end_scale: Vec2

    init_color: Vec4
    end_color: Vec4

    trail_init_color: Vec4 = None
    trail_end_color: Vec4 = None

class Trail(Entity):
    def __init__(self,
                manager, 
                duration=1, 
                resolution=10, 
                segments=10, 
                init_thickness=0.3,
                end_thickness=0, 
                frames=Vec2(1,1),
                frames_per_loop=1,
                **kwargs):
        super().__init__(**kwargs,parent = manager)
        self.shader = Shader(
            vertex="""
                #version 430

                uniform mat4 p3d_ModelViewMatrix;
                uniform mat4 p3d_ProjectionMatrix;
                in vec4 p3d_Vertex;
                in vec2 p3d_MultiTexCoord0;

                in vec3 position;
                in vec3 velocity;
                in float lifetime;
                in float delay;
                in vec3 init_scale;
                in vec3 end_scale;
                in vec4 init_color;
                in vec4 end_color;

                uniform float elapsed_time;
                uniform vec3 gravity;
                uniform bool looping;
                uniform bool billboard;

                uniform int resolution;
                uniform int segments;
                uniform float duration;
                
                flat out int discard_frag;
                out vec2 texcoord;
                out vec4 new_color;
                out float anim_progress;

                vec3 get_position(float time) {
                    return (position+velocity*time + 0.5*gravity*time*time);
                }

                vec3 get_tangent(float time) {
                    return normalize(velocity + gravity*time);
                }

                mat3 get_rotation_matrix(vec3 tangent) {
                    vec3 from = vec3(0,1,0);
                    if (tangent == from * -1) {
                        return mat3(1);
                    }
                    vec3 v = cross(from, tangent);
                    float s = length(v);
                    float c = dot(from, tangent);
                    mat3 vx = mat3(
                        0, -v.z, v.y,
                        v.z, 0, -v.x,
                        -v.y, v.x, 0
                    );
                    return mat3(1) + vx + vx*vx*(1-c)/(s*s);
                    
                }

                mat4 remove_rotation(mat4 m) {
                    m[0][0] = 1;
                    m[0][1] = 0;
                    m[0][2] = 0;
                    
                    m[1][0] = 0;
                    m[1][1] = 1;
                    m[1][2] = 0;
                    
                    m[2][0] = 0;
                    m[2][1] = 0;
                    m[2][2] = 1;
                    
                    return m;
                }
                
                void main() {
                    if (duration == 0) {
                        discard_frag = 1;
                        return;
                    }
                    
                    int layer = int(p3d_Vertex.y);
                    
                    float prev_progress = 0;
                    float progress = float(layer) / float(segments);
                    float next_progress = 1;
                    
                    if (elapsed_time - delay - duration< 0) {
                        discard_frag = 1;
                        return;
                    }
                    
                    float start_time = mod(elapsed_time - delay - duration, lifetime);
                    float end_time = mod(elapsed_time - delay, lifetime);
                    
                    if (end_time < duration) {
                        end_time = lifetime;
                    }
                    
                    float adjusted_time = mix(start_time, end_time, 1-progress);
                    
                    float life = adjusted_time / lifetime;
                    
                    if (life < 0.0){
                        discard_frag = 1;
                        return;
                    }
                    discard_frag = 0;

                    vec3 new_scale = mix(init_scale, end_scale, life);

                    vec3 v = get_rotation_matrix(get_tangent(adjusted_time)) * vec3(p3d_Vertex.x, 0, p3d_Vertex.z) * new_scale;
                    
                    texcoord = p3d_MultiTexCoord0;

                    new_color = mix(init_color, end_color, life);

                    anim_progress = start_time / lifetime;

                    vec3 adjusted_position = get_position(adjusted_time);
                    
                    if (billboard) {
                        mat4 custom_ModelViewMatrix = remove_rotation(p3d_ModelViewMatrix);
                        vec4 temp = custom_ModelViewMatrix * vec4(v, p3d_Vertex.w) + p3d_ModelViewMatrix * vec4(adjusted_position, p3d_Vertex.w);
                        temp.w = p3d_Vertex.w;
                        gl_Position = p3d_ProjectionMatrix * temp;
                    } else {
                        gl_Position = p3d_ProjectionMatrix * p3d_ModelViewMatrix * vec4((v + adjusted_position), p3d_Vertex.w);
                    }
                }""",
            fragment="""
                    #version 430
                    
                    uniform sampler2D p3d_Texture0;
                    uniform vec4 p3d_ColorScale;
                    uniform vec2 frames;
                    uniform int frames_per_loop;
                    
                    flat in int discard_frag;
                    in vec2 texcoord;
                    in vec4 new_color;
                    in float anim_progress;
                    
                    out vec4 fragColor;
                    void main() {
                        if (discard_frag == 1) {
                            discard;
                        }
                        int frame = int(anim_progress * frames_per_loop);
                        int x = int(mod(frame, int(frames.x)));
                        int y = int(mod(frame / int(frames.x), int(frames.y)));
                        vec2 adjusted_texcoord = vec2(texcoord.x / frames.x + x / frames.x, texcoord.y / frames.y + y / frames.y);
                        fragColor = texture(p3d_Texture0, adjusted_texcoord)  * p3d_ColorScale * new_color;
                    }""")

        self._resolution = resolution
        self._segments = segments
        self._init_thickness = init_thickness
        self._end_thickness = end_thickness
        self.generate_model()
        self.manager = manager
        self.duration = duration
        self.frames = frames
        self.frames_per_loop = frames_per_loop

    def generate_model(self):
        if not(hasattr(self, "resolution") and hasattr(self, "segments") and hasattr(self, "init_thickness") and hasattr(self, "end_thickness")):
            return
        resolution = self.resolution
        segments = self.segments
        init_thickness = self.init_thickness
        end_thickness = self.end_thickness
        triangles = []
        uv = []
        vertices = []
        angle_step = math.radians(1/resolution*360)
        for i in range(segments+1):
            circle = []
            progress = i/segments
            thickness = lerp(init_thickness, end_thickness, progress)
            half_thickness = thickness/2
            i_res = i*resolution
            i_plus_1 = i_res+resolution
            for j in range(resolution):
                
                angle = j*angle_step
                dist = half_thickness
                
                vert = Vec3(math.sin(angle),0,math.cos(angle))
                vert *= dist
                vert.y = i
                
                circle.append(vert)
                
                uv.append((j/resolution,progress))
                
                if i == segments:
                    continue
                
                triangles.append([i_res+j, i_res+(j+1)%resolution, i_plus_1+j])
                triangles.append([i_plus_1+j, i_res+(j+1)%resolution, i_plus_1+(j+1)%resolution])
                
            vertices.extend(circle)
        
        model = Mesh(
            vertices=vertices,
            uvs=uv,
            triangles=triangles)
        
        model.generate()
        self.model = model

    def generate_format(self):
        
        geom_node = self.find("**/+GeomNode").node()

        if geom_node.getNumGeoms() == 0:
            raise Exception("No geometry found")

        if geom_node.getGeom(0).getVertexData().getNumRows() == 0:
            raise Exception("No vertex data found")

        if geom_node.getGeom(0).getVertexData().getNumRows() > 0:
            
            self._model_nb_rows = geom_node.getGeom(0).getVertexData().getNumRows()
        
            self.vformat = GeomVertexFormat(
                geom_node.getGeom(0).getVertexData().getFormat()
            )
            
            if not self.vformat.hasColumn("lifetime"):
                self.iformat = GeomVertexArrayFormat()
                self.iformat.setDivisor(1)
                self.iformat.addColumn(f"position", 3, Geom.NT_stdfloat, Geom.C_vector)
                self.iformat.addColumn(f"velocity", 3, Geom.NT_stdfloat, Geom.C_vector)

                self.iformat.addColumn(f"lifetime", 1, Geom.NT_stdfloat, Geom.C_vector)
                self.iformat.addColumn(f"delay", 1, Geom.NT_stdfloat, Geom.C_vector)

                self.iformat.addColumn(f"init_scale", 3, Geom.NT_stdfloat, Geom.C_vector)
                self.iformat.addColumn(f"end_scale", 3, Geom.NT_stdfloat, Geom.C_vector)

                self.iformat.addColumn(f"init_color", 4, Geom.NT_stdfloat, Geom.C_vector)
                self.iformat.addColumn(f"end_color", 4, Geom.NT_stdfloat, Geom.C_vector)

                
                self.vformat.addArray(self.iformat)
                
            self.vformat = GeomVertexFormat.registerFormat(self.vformat)


            self.vdata = geom_node.modifyGeom(0).modifyVertexData()
            self.vdata.setFormat(self.vformat)

            if self.vdata.getFormat() != self.vformat:
                raise Exception("Vertex data format mismatch")
        else:
            raise Exception("No vertex data found")

    @property
    def duration(self):
        return self._duration
    
    @duration.setter
    def duration(self, value):
        self._duration = value
        self.set_shader_input("duration", value)
        
    @property
    def resolution(self):
        return self._resolution
    
    @resolution.setter
    def resolution(self, value):
        self._resolution = value
        self.set_shader_input("resolution", value)
        self.generate_model()
        
    @property
    def segments(self):
        return self._segments
    
    @segments.setter
    def segments(self, value):
        self._segments = value
        self.set_shader_input("segments", value)
        self.generate_model()

    @property
    def resolution(self):
        return self._resolution 

    @resolution.setter
    def resolution(self, value):
        self._resolution = value
        self.set_shader_input("resolution", value)
        self.generate_model()

    @property
    def init_thickness(self):
        return self._init_thickness
    
    @init_thickness.setter
    def init_thickness(self, value):
        self._init_thickness = value
        self.generate_model()
        
    @property
    def end_thickness(self):
        return self._end_thickness
    
    @end_thickness.setter
    def end_thickness(self, value):
        self._end_thickness = value
        self.generate_model()

    
    @property
    def frames(self):
        return self._frames
    
    @frames.setter
    def frames(self, value):
        self._frames = value
        self.set_shader_input("frames", value)

    @property
    def frames_per_loop(self):
        return self._frames_per_loop
    
    @frames_per_loop.setter
    def frames_per_loop(self, value):
        self._frames_per_loop = value
        self.set_shader_input("frames_per_loop", value)
    
class ParticleManager(Entity):
    max_particles = 1_000_000
    i = 0
    particle_shader = Shader(
        name=f"particle_shader",
        language=Shader.GLSL,
        vertex="""
                #version 430

                uniform mat4 p3d_ModelViewMatrix;
                uniform mat4 p3d_ProjectionMatrix;
                in vec4 p3d_Vertex;
                in vec2 p3d_MultiTexCoord0;

                in vec3 position;
                in vec3 velocity;
                in float lifetime;
                in float delay;
                in vec3 init_scale;
                in vec3 end_scale;
                in vec4 init_color;
                in vec4 end_color;

                uniform float elapsed_time;
                uniform vec3 gravity;
                uniform bool looping;
                uniform bool billboard;

                flat out int discard_frag;
                out vec2 texcoord;
                out vec4 new_color;
                out float progress;

                void main() {
                        
                    float adjusted_time = elapsed_time - delay;
                    float life = adjusted_time / lifetime;

                    if (life > 1.0) {
                        if (looping) {
                            life = fract(life);
                            adjusted_time = mod(adjusted_time, lifetime);
                        } else {
                            discard_frag = 1;
                            return;
                        }
                    }
                    else if (life < 0.0){
                        discard_frag = 1;
                        return;
                    }
                    discard_frag = 0;

                    vec3 new_scale = mix(init_scale, end_scale, life);

                    vec3 v = p3d_Vertex.xyz * new_scale;
                    
                    texcoord = p3d_MultiTexCoord0;

                    new_color = mix(init_color, end_color, life);

                    vec3 adjusted_position = (position+velocity*adjusted_time + 0.5*gravity*adjusted_time*adjusted_time);

                    progress = life;
                    
                    
                    if (billboard) {
                        mat4 custom_ModelViewMatrix = p3d_ModelViewMatrix;
                        custom_ModelViewMatrix[0][0] = 1;
                        custom_ModelViewMatrix[0][1] = 0;
                        custom_ModelViewMatrix[0][2] = 0;
                        custom_ModelViewMatrix[1][0] = 0;
                        custom_ModelViewMatrix[1][1] = 1;
                        custom_ModelViewMatrix[1][2] = 0;
                        custom_ModelViewMatrix[2][0] = 0;
                        custom_ModelViewMatrix[2][1] = 0;
                        custom_ModelViewMatrix[2][2] = 1;
                        vec4 temp = custom_ModelViewMatrix * vec4(v, p3d_Vertex.w) + p3d_ModelViewMatrix * vec4(adjusted_position, p3d_Vertex.w);
                        temp.w = p3d_Vertex.w;
                        gl_Position = p3d_ProjectionMatrix * temp;
                    } else {
                        gl_Position = p3d_ProjectionMatrix * p3d_ModelViewMatrix * vec4((v + adjusted_position), p3d_Vertex.w);
                    }
                }""",
        fragment="""
                    #version 430
                    uniform sampler2D p3d_Texture0;
                    uniform vec4 p3d_ColorScale;
                    uniform vec2 frames;
                    uniform int frames_per_loop;
                    in vec2 texcoord;
                    flat in int discard_frag;
                    in vec4 new_color;
                    in float progress;
                    out vec4 fragColor;
                    void main() {
                        if (discard_frag == 1) {
                            discard;
                        }
                        int frame = int(progress * frames_per_loop);
                        int x = frame % int(frames.x);
                        int y = int(mod(frame / int(frames.x), int(frames.y)));
                        vec2 adjusted_texcoord = vec2(texcoord.x / frames.x + x / frames.x, texcoord.y / frames.y + y / frames.y);
                        fragColor = texture(p3d_Texture0, adjusted_texcoord)  * p3d_ColorScale * new_color;
                    }""")

    def __init__(
        self,
        looping=False,
        simulation_speed=1,
        gravity=Vec3(0, -9.8, 0),
        particles=[],
        model="quad",
        trail_duration=0,
        trail_segments=10,
        trail_resolution=10,
        frames=None,
        frames_per_loop=None,
        billboard=False,
        **kwargs,
    ):
        """Creates a new ParticleManager

        Args:
            looping (bool, optional): If the particles should loop. Defaults to False.
            simulation_speed (int, optional): The speed of the simulation. Defaults to 1.
            gravity (Vec3, optional): The gravity which will affect every particle in this manager. Defaults to Vec3(0,-9.8,0).
            particles (List[Particle], optional): Every starting particles. Defaults to [].
        """
        self.instance = ParticleManager.i
        super().__init__(
            model=model,
            shader=ParticleManager.particle_shader,
        )
        ParticleManager.i += 1
        self.trail = Trail(manager=self, duration=trail_duration, resolution=trail_resolution, segments=trail_segments)
        self._bsphere = self.node().getBounds()
        self.elapsed_time = 0
        self.looping = looping
        self.simulation_speed = simulation_speed
        self.gravity = gravity
        self.trail_segments = trail_segments
        self.billboard = billboard
        self._particles = particles

        self.frames = frames if frames is not None else Vec2(1, 1)
        self.frames_per_loop = frames_per_loop if frames_per_loop is not None else 1

        for key, value in kwargs.items():
            if key.startswith("trail_"):
                setattr(self.trail, key[6:], value)
            else:
                setattr(self, key, value)
        
        geom_node = self.find("**/+GeomNode").node()

        if geom_node.getNumGeoms() == 0:
            raise Exception("No geometry found")

        if geom_node.getGeom(0).getVertexData().getNumRows() == 0:
            raise Exception("No vertex data found")

        if geom_node.getGeom(0).getVertexData().getNumRows() > 0:
            
            self._model_nb_rows = geom_node.getGeom(0).getVertexData().getNumRows()
        

            self.vformat = GeomVertexFormat(
                geom_node.getGeom(0).getVertexData().getFormat()
            )
            
            if not self.vformat.hasColumn("lifetime"):
                
                self.iformat = GeomVertexArrayFormat()
                self.iformat.setDivisor(1)
                self.iformat.addColumn(f"position", 3, Geom.NT_stdfloat, Geom.C_vector)
                self.iformat.addColumn(f"velocity", 3, Geom.NT_stdfloat, Geom.C_vector)

                self.iformat.addColumn(f"lifetime", 1, Geom.NT_stdfloat, Geom.C_vector)
                self.iformat.addColumn(f"delay", 1, Geom.NT_stdfloat, Geom.C_vector)

                self.iformat.addColumn(f"init_scale", 3, Geom.NT_stdfloat, Geom.C_vector)
                self.iformat.addColumn(f"end_scale", 3, Geom.NT_stdfloat, Geom.C_vector)

                self.iformat.addColumn(f"init_color", 4, Geom.NT_stdfloat, Geom.C_vector)
                self.iformat.addColumn(f"end_color", 4, Geom.NT_stdfloat, Geom.C_vector)
            
                self.vformat.addArray(self.iformat)
                
            self.vformat = GeomVertexFormat.registerFormat(self.vformat)


            self.vdata = geom_node.modifyGeom(0).modifyVertexData()
            self.vdata.setFormat(self.vformat)

            if self.vdata.getFormat() != self.vformat:
                raise Exception("Vertex data format mismatch")
            self.apply()
        else:
            raise Exception("No vertex data found")

    def update(self):
        self.elapsed_time += time.dt * self.simulation_speed
        self.set_shader_input("elapsed_time", self.elapsed_time)
        if hasattr(self, "trail") and isinstance(self.trail, Trail):
            self.trail.set_shader_input("elapsed_time", self.elapsed_time)

    def apply(self):
        to_generate = min(len(self.particles), ParticleManager.max_particles)

        if hasattr(self, "trail") and isinstance(self.trail, Trail):
            self.trail.generate_format()
            trail_vdata = self.trail.vdata
            trail_vdata.setNumRows(self.trail._model_nb_rows)
            trail_vdata.setNumRows(to_generate + self.trail._model_nb_rows)
            
        self.vdata.setNumRows(self._model_nb_rows)
        self.vdata.setNumRows(to_generate + self._model_nb_rows)

        position_i = GeomVertexWriter(self.vdata, f"position")
        velocity_i = GeomVertexWriter(self.vdata, f"velocity")

        lifetime_i = GeomVertexWriter(self.vdata, f"lifetime")
        delay_i = GeomVertexWriter(self.vdata, f"delay")

        init_scale_i = GeomVertexWriter(self.vdata, f"init_scale")
        end_scale_i = GeomVertexWriter(self.vdata, f"end_scale")

        init_color_i = GeomVertexWriter(self.vdata, f"init_color")
        end_color_i = GeomVertexWriter(self.vdata, f"end_color")

        if hasattr(self, "trail") and isinstance(self.trail, Trail):
            trail_position_i = GeomVertexWriter(trail_vdata, f"position")
            trail_velocity_i = GeomVertexWriter(trail_vdata, f"velocity")
            trail_lifetime_i = GeomVertexWriter(trail_vdata, f"lifetime")
            trail_delay_i = GeomVertexWriter(trail_vdata, f"delay")
            trail_init_scale_i = GeomVertexWriter(trail_vdata, f"init_scale")
            trail_end_scale_i = GeomVertexWriter(trail_vdata, f"end_scale")
            trail_init_color_i = GeomVertexWriter(trail_vdata, f"init_color")
            trail_end_color_i = GeomVertexWriter(trail_vdata, f"end_color")
            
            
        for i in range(to_generate):
            particle = self.particles[i]
            position_i.add_data3(*particle.position)
            velocity_i.add_data3(*particle.velocity)

            lifetime_i.add_data1(particle.lifetime)
            delay_i.add_data1(particle.delay)

            init_scale_i.add_data3(*particle.init_scale)
            end_scale_i.add_data3(*particle.end_scale)

            init_color_i.add_data4(*particle.init_color)
            end_color_i.add_data4(*particle.end_color)

            if hasattr(self, "trail") and isinstance(self.trail, Trail):
                trail_position_i.add_data3(*particle.position)
                trail_velocity_i.add_data3(*particle.velocity)
                
                trail_lifetime_i.add_data1(particle.lifetime)
                trail_delay_i.add_data1(particle.delay)
                
                trail_init_scale_i.add_data3(*particle.init_scale)
                trail_end_scale_i.add_data3(*particle.end_scale)
                
                if hasattr(particle, "trail_init_color") and particle.trail_init_color is not None:
                    trail_init_color_i.add_data4(*particle.trail_init_color)
                else:
                    trail_init_color_i.add_data4(*color.white)
                if hasattr(particle, "trail_end_color") and particle.trail_end_color is not None:
                    trail_end_color_i.add_data4(*particle.trail_end_color)
                else:
                    trail_end_color_i.add_data4(*color.white)
                        
                        
                
                
        self.set_instance_count(to_generate)
        if hasattr(self, "trail") and isinstance(self.trail, Trail):
            self.trail.set_instance_count(to_generate)
            
        self.elapsed_time = 0

    @property
    def culling(self):
        return self._culling

    @culling.setter
    def culling(self, value: bool):
        if not value:
            self.node().setBounds(OmniBoundingVolume())
            self.node().setFinal(True)
            if hasattr(self, "trail") and isinstance(self.trail, Trail):
                self.trail.node().setBounds(OmniBoundingVolume())
                self.trail.node().setFinal(True)
            self._culling = False
        else:
            self.node().setBounds(self._bsphere)
            self.node().setFinal(False)
            if hasattr(self, "trail") and isinstance(self.trail, Trail):
                self.trail.node().setBounds(self._bsphere)
                self.trail.node().setFinal(False)
            self._culling = True

    @property
    def particles(self):
        return self._particles

    @particles.setter
    def particles(self, value: List[Particle]):
        self._particles = value
        self.apply()

    @property
    def gravity(self):
        return self._gravity

    @gravity.setter
    def gravity(self, value: Vec3):
        self._gravity = value
        self.set_shader_input("gravity", value)
        if hasattr(self, "trail") and isinstance(self.trail, Trail):
            self.trail.set_shader_input("gravity", value)

    @property
    def simulation_speed(self):
        return self._simulation_speed

    @simulation_speed.setter
    def simulation_speed(self, value: float):
        self._simulation_speed = value

    @property
    def looping(self):
        return self._looping

    @looping.setter
    def looping(self, value: bool):
        self._looping = value
        self.set_shader_input("looping", value)
        if hasattr(self, "trail") and isinstance(self.trail, Trail):
            self.trail.set_shader_input("looping", value)

    @property
    def frames(self):
        return self._frames
    
    @frames.setter
    def frames(self, value):
        self._frames = value
        self.set_shader_input("frames", value)

    @property
    def frames_per_loop(self):
        return self._frames_per_loop
    
    @frames_per_loop.setter
    def frames_per_loop(self, value):
        self._frames_per_loop = value
        self.set_shader_input("frames_per_loop", value)

    @property
    def billboard(self):
        return self._billboard
    
    @billboard.setter
    def billboard(self, value):
        self._billboard = value
        self.set_shader_input("billboard", value)
        if hasattr(self, "trail") and isinstance(self.trail, Trail):
            self.trail.set_shader_input("billboard", value)

    def __setattr__(self, key, value):
        if key.startswith("trail_"):
            setattr(self.trail, key[6:], value)
        else:
            super().__setattr__(key, value)
    
    def __getattr__(self, key):
        if key.startswith("trail_"):
            return getattr(self.trail, key[6:])
        else:
            return super().__getattr__(key)

if __name__ == "__main__":
    import random


    window.vsync = False
    app = Ursina()


    def generate_particle():
        return Particle(
            position=Vec3(
                random.random() * 5 - 2.5, random.random() * 0.5, random.random() * 5 - 2.5
            ),
            velocity=Vec3(
                random.random() * 3 + 2,
                random.random() * 3 - 1.5,
                random.random() * 3 - 1.5,
            ),
            lifetime=random.random() * 5 + 3,
            delay=random.random() * 4,
            init_scale=Vec3(random.random() * 0.5),
            end_scale=Vec3(random.random() * 0.2),
            init_color=Vec4(random.random(), random.random(), random.random(), 0) * 0.2
            + color.yellow,
            end_color=color.white,
            trail_init_color=color.orange,
            trail_end_color=color.red
        )


    def generate_particles(n):
        return [generate_particle() for _ in range(n)]

    manager = ParticleManager(
        scale=1,
        particles=generate_particles(100),
        gravity=Vec3(0, 1, 0),
        position=Vec3(0, -3, 0),
        looping=True,
        culling=False,
        trail_duration=1,
        trail_init_thickness=1,
        model="diamond",
    )


    def input(key):
        if key == "space":
            manager.simulation_speed = 0 if manager.simulation_speed != 0 else 1
        if key == "-":
            manager.simulation_speed -= 0.1
        if key == "+":
            manager.simulation_speed += 0.1
    
    def update():
        movement =  Vec3(held_keys["d"] - held_keys["a"], held_keys["w"] - held_keys["s"], held_keys["up arrow"] - held_keys["down arrow"]) 
        if movement.length() > 0:
            movement = movement.normalized()
        manager.position += movement * time.dt * 5
        
        manager.rotation_y += (held_keys["left mouse"] - held_keys["right mouse"]) * 100 * time.dt

    app.run()
