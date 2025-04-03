"""
ursina/hit_info.py

This module defines the HitInfo class, which is used to store information about collision hits in the Ursina engine.
The HitInfo class contains attributes such as the entity hit, the point of collision, the distance, and the normal of the hit.

Dependencies:
- ursina.entity.Entity
- ursina.vec3.Vec3
"""

class HitInfo:
    """
    The HitInfo class stores information about collision hits in the Ursina engine.

    Attributes:
        hit (bool): Whether a hit occurred.
        entity (Entity): The entity that was hit.
        point (Vec3): The point of collision in local space.
        world_point (Vec3): The point of collision in world space.
        distance (float): The distance from the origin to the point of collision.
        normal (Vec3): The normal vector at the point of collision in local space.
        world_normal (Vec3): The normal vector at the point of collision in world space.
        hits (list): A list of all hits.
        entities (list): A list of all entities hit.
    """
    __slots__ = ['hit', 'entity', 'point', 'world_point', 'distance', 'normal', 'world_normal', 'hits', 'entities']

    def __init__(self, **kwargs):
        """
        Initialize the HitInfo object with default values or provided keyword arguments.

        Args:
            **kwargs: Keyword arguments to set the attributes of the HitInfo object.
        """
        self.hit: bool = None  # Whether a hit occurred
        self.entity: Entity = None  # The entity that was hit
        self.point: Vec3 = None  # The point of collision in local space
        self.world_point: Vec3 = None  # The point of collision in world space
        self.distance: float = 9999  # The distance from the origin to the point of collision
        self.normal: Vec3 = None  # The normal vector at the point of collision in local space
        self.world_normal: Vec3 = None  # The normal vector at the point of collision in world space
        self.hits = []  # A list of all hits
        self.entities = []  # A list of all entities hit

        # Set attributes based on provided keyword arguments
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __bool__(self):
        """
        Return the boolean value of the HitInfo object.

        Returns:
            bool: True if a hit occurred, False otherwise.
        """
        return self.hit
