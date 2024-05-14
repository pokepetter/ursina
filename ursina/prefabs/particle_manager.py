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


class ParticleManager(Entity):
    max_particles = 1_000_000
    i = 0
    particle_shader = Shader(
        name=f"particle_shader",
        language=Shader.GLSL,
        vertex="""#version 140

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

in vec3 position;
in vec3 velocity;
in float lifetime;
in float delay;
in vec2 init_scale;
in vec2 end_scale;
in vec4 init_color;
in vec4 end_color;

uniform float elapsed_time;
uniform vec3 gravity;
uniform bool looping;

flat out int discard_frag;
out vec2 texcoord;
out vec4 new_color;

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

    vec3 new_scale = vec3(mix(init_scale, end_scale, life), 1.0);

    vec3 v = p3d_Vertex.xyz * new_scale;
    
    texcoord = p3d_MultiTexCoord0;

    new_color = mix(init_color, end_color, life);

    vec3 adjusted_position = position+velocity*adjusted_time + 0.5*gravity*adjusted_time*adjusted_time;

    gl_Position = p3d_ModelViewProjectionMatrix * vec4(v + adjusted_position, 1.0);
}""",
        fragment="""#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoord;
flat in int discard_frag;
in vec4 new_color;
out vec4 fragColor;


void main() {
    if (discard_frag == 1) {
        discard;
    }
    fragColor = texture(p3d_Texture0, texcoord) * p3d_ColorScale * new_color;
}""",
    )

    def __init__(
        self,
        looping=False,
        simulation_speed=1,
        gravity=Vec3(0, -9.8, 0),
        particles=[],
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
            model=Quad(segments=0),
            billboard=True,
            shader=ParticleManager.particle_shader,
        )
        ParticleManager.i += 1
        self._bsphere = self.node().getBounds()
        self.elapsed_time = 0
        self.looping = looping
        self.simulation_speed = simulation_speed
        self.gravity = gravity
        self._particles = particles

        for key, value in kwargs.items():
            setattr(self, key, value)

        self.geom_node = self.find("**/+GeomNode").node()

        if self.geom_node.getNumGeoms() == 0:
            raise Exception("No geometry found")

        if self.geom_node.getGeom(0).getVertexData().getNumRows() == 0:
            raise Exception("No vertex data found")

        if self.geom_node.getGeom(0).getVertexData().getNumRows() > 0:
            self.iformat = GeomVertexArrayFormat()
            self.iformat.setDivisor(1)
            self.iformat.addColumn(f"position", 3, Geom.NT_stdfloat, Geom.C_vector)
            self.iformat.addColumn(f"velocity", 3, Geom.NT_stdfloat, Geom.C_vector)

            self.iformat.addColumn(f"lifetime", 1, Geom.NT_stdfloat, Geom.C_vector)
            self.iformat.addColumn(f"delay", 1, Geom.NT_stdfloat, Geom.C_vector)

            self.iformat.addColumn(f"init_scale", 2, Geom.NT_stdfloat, Geom.C_vector)
            self.iformat.addColumn(f"end_scale", 2, Geom.NT_stdfloat, Geom.C_vector)

            self.iformat.addColumn(f"init_color", 4, Geom.NT_stdfloat, Geom.C_vector)
            self.iformat.addColumn(f"end_color", 4, Geom.NT_stdfloat, Geom.C_vector)

            self.vformat = GeomVertexFormat(
                self.geom_node.getGeom(0).getVertexData().getFormat()
            )
            self.vformat.addArray(self.iformat)
            self.vformat = GeomVertexFormat.registerFormat(self.vformat)

            self.vdata = self.geom_node.modifyGeom(0).modifyVertexData()
            self.vdata.setFormat(self.vformat)

            if self.vdata.getFormat() != self.vformat:
                raise Exception("Vertex data format mismatch")
            print("Fuck")
            self.apply()
        else:
            raise Exception("No vertex data found")

    def update(self):
        self.elapsed_time += time.dt * self.simulation_speed
        self.set_shader_input("elapsed_time", self.elapsed_time)
        # print(mouse_emitter.world_position)

    def apply(self):
        to_generate = min(len(self.particles), ParticleManager.max_particles)

        self.vdata.setNumRows(to_generate)

        position_i = GeomVertexWriter(self.vdata, f"position")
        velocity_i = GeomVertexWriter(self.vdata, f"velocity")

        lifetime_i = GeomVertexWriter(self.vdata, f"lifetime")
        delay_i = GeomVertexWriter(self.vdata, f"delay")

        init_scale_i = GeomVertexWriter(self.vdata, f"init_scale")
        end_scale_i = GeomVertexWriter(self.vdata, f"end_scale")

        init_color_i = GeomVertexWriter(self.vdata, f"init_color")
        end_color_i = GeomVertexWriter(self.vdata, f"end_color")

        for i in range(to_generate):
            particle = self.particles[i]
            position_i.add_data3(*particle.position)
            velocity_i.add_data3(*particle.velocity)

            lifetime_i.add_data1(particle.lifetime)
            delay_i.add_data1(particle.delay)

            init_scale_i.add_data2(*particle.init_scale)
            end_scale_i.add_data2(*particle.end_scale)

            init_color_i.add_data4(*particle.init_color)
            end_color_i.add_data4(*particle.end_color)

        self.set_instance_count(to_generate)

        self.elapsed_time = 0

    @property
    def culling(self):
        return self._culling

    @culling.setter
    def culling(self, value: bool):
        if not value:
            self.node().setBounds(OmniBoundingVolume())
            self.node().setFinal(True)
            self._culling = False
        else:
            self.node().setBounds(self._bsphere)
            self.node().setFinal(False)
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
