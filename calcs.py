import math
import os
from solid import *

"""
The math for a helix comes from https://mathworld.wolfram.com/Helix.html
x, y and z are coordinates in 3d space
r is a constant and gives the radius of the helix
t is where we are in a turn (in radians) and is thus a number from 0 to 2 * pi
c is a constant defining the height, and 2 * pi * c gives the vertical distance between loops

to solve for a given point on the helix, use:
x = r * cos(t)
y = r * sin(t)
z = c * t
"""
HELIX_HEIGHT = 200  # picked this initial number since it's double the diameter of the base
HELIX_PENCILS = 8  # rainbow colors
HELIX_R = 50  # the pencils I'm using are ~180mm out of the box, so a 100mm diameter circle seems good to start with
PENCIL_RADIUS = 5  # the pencils I'm using are about 8mm in diameter, so a 10mm hold should allow for smooth usage
SEGMENT_THICKNESS = 6  # how "thick" the helix should be
TAB_THICKNESS = 2  # how thick the tabs should be
SEGMENT_HEIGHT = 20  # if the helix "ribbon" weren't rotated, what would its height be?
CAP_HEIGHT = 15  # how tall is the base/top component?
CAP_R = 75  # the radius of the base/top component
CAP_SEGMENTS = 256  # higher numbers lead to smoother curves
CAP_OFFSET_Z = -3  # moves the base so that the segments don't protrude
"""
end of defined constants, start of computed constants
"""
HELIX_C = HELIX_HEIGHT / 2 / math.pi
"""
there is a "blank" segment between each "pencil-holding" segment, plus one on either end
"""
HELIX_SEGMENTS = HELIX_PENCILS * 2 + 1
Z_INTERVAL = HELIX_HEIGHT / HELIX_SEGMENTS  # the distance on the z plane between the center of one segment and another
"""
the origin of the first helix will be at r,0,0
find the set of points we use as the center of each segment. the distance between these points is the length of one
side of the segment
the first point we are looking for has a z equal to Z_INTERVAL
"""
world_geo = None
current_z = 0
current_y = 0
current_x = HELIX_R
current_t = 0
step = 0
while step < HELIX_SEGMENTS:
    prior_x = current_x
    prior_y = current_y
    prior_z = current_z
    prior_t = current_t
    step += 1
    current_z += Z_INTERVAL
    current_t = current_z / HELIX_C
    current_x = HELIX_R * math.cos(current_t)
    current_y = HELIX_R * math.sin(current_t)
    """
    get the distance between the current and prior point
    this is the measure of one side of the segment rectangle, while SEGMENT_HEIGHT is the other
    math came from https://www.engineeringtoolbox.com/distance-relationship-between-two-points-d_1854.html
    """
    d = math.pow(
        math.pow(current_x-prior_x, 2) +
        math.pow(current_y-prior_y, 2) +
        math.pow(current_z-prior_z, 2), 0.5
    )
    """
    the local x rotation will face the object towards the center of the helix (which is the world origin)
    first we get the angle of the origin to the center point of the segment
    then we use 90 - that angle to get the angle of rotation that the segment needs
    """
    rot_z = math.atan(current_y / current_x) * 180 / math.pi
    rot_z = 90 - rot_z
    """
    get the local z rotation of the segment
    we calculate rise over run as rise = change in z between the current_z and prior_z and
    run = the length of the side calculated above. to get the angle  we take the arctangent of this ratio
    """
    rot_y = (current_z - prior_z) / d * 180 / math.pi
    """
    in two quadrants (negative x) add 180 degrees to fix the rotation
    """
    if current_t > 0.5 * math.pi and current_t <= 1.5 * math.pi:
        rot_z += 180
    print("step: ", step, " x: ", current_x, " y: ", current_y, " z: ", current_z, " t: ", current_t, " d: ", d,
          " ry: ", rot_y, " rz: ", rot_z)
    """
    create an OPENSCAD cube with the calculated dimensions at the calculated coordinates
    """
    geo = cube([d, SEGMENT_THICKNESS, SEGMENT_HEIGHT], center=True)
    geo = rotate([0, rot_y, -rot_z])(geo)
    geo = translate([current_x, current_y, current_z])(geo)
    """
    even-numbered segments get a tab attached to either side, 
    which will be matched with a slot in odd-numbered segments later.
    we move backward and forward half a standard z-increment and create a tab with the same rules as the cube
    """
    if step % 2 == 0:
        t_half = (current_t - prior_t) / 2

    """
    add the cube to the world geometry
    """
    if world_geo is None:
        world_geo = geo
    else:
        world_geo += geo
    """
    helix2 is mirrored on the x and y, as well as the y-coordinate rotation
    """
    geo = cube([d, SEGMENT_THICKNESS, SEGMENT_HEIGHT], center=True)
    geo = rotate([0, -rot_y, -rot_z])(geo)
    geo = translate([-current_x, -current_y, current_z])(geo)
    world_geo += geo
    """
    add a cylinder to represent the pencil on the even-numbered segments, use it as a hole
    """
    if step % 2 == 0:
        rot_z = math.atan(current_y / current_x) * 180 / math.pi
        geo = cylinder(r=PENCIL_RADIUS, h=3*HELIX_R, segments=32, center=True)
        geo = rotate([0, 90, rot_z])(geo)
        geo = translate([0, 0, current_z])(geo)
        world_geo = world_geo + hole()(geo)

"""
add the base and top
"""
geo = cylinder(h=CAP_HEIGHT, r=CAP_R, segments=CAP_SEGMENTS, center=False)
geo = translate([0, 0, CAP_OFFSET_Z])(geo)
world_geo += geo
geo = cylinder(h=CAP_HEIGHT, r=CAP_R, segments=CAP_SEGMENTS, center=False)
geo = translate([0, 0, HELIX_HEIGHT])(geo)
world_geo += geo
"""
output the world geometry to file
"""
filepath = os.path.join(os.getcwd(), 'full.scad')
file_out = scad_render_to_file(world_geo, filepath=filepath, include_orig_code=False)
