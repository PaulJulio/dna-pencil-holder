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
TAB_WIDTH = 4  # how far out of the segment the tab should protrude
TAB_HEIGHT = 9  # how tall the tab should be
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
get the distance between the first step and the origin, which is at (HELIX_R, 0, 0)
this is the measure of one side of the segment rectangle, while SEGMENT_HEIGHT is the other
math came from https://www.engineeringtoolbox.com/distance-relationship-between-two-points-d_1854.html
"""
t1 = Z_INTERVAL / HELIX_C  # t0 is 0
x1 = HELIX_R * math.cos(t1)  # x0 is HELIX_R
y1 = HELIX_R * math.sin(t1)  # y0 is 0

SEGMENT_LENGTH = math.pow(
    math.pow(x1 - HELIX_R, 2) +
    math.pow(y1, 2) +  # y1 - y0 = y1
    math.pow(Z_INTERVAL, 2), 0.5  # z0 = 0, z1 = Z_INTERVAL
)


def z_rotation(x, y, t):
    """
    the local x rotation will face the object towards the center of the helix (which is the world origin)
    first we get the angle of the origin to the center point of the segment
    then we use 90 - that angle to get the angle of rotation that the segment needs
    """
    rot_z = math.atan(y / x) * 180 / math.pi
    rot_z = 90 - rot_z
    """
    in two quadrants (negative x) add 180 degrees to fix the rotation
    """
    if 0.5 * math.pi < t <= 1.5 * math.pi:
        rot_z += 180
    return rot_z


def return_segment_to_origin(translated_segment, segment_step, helix=1):
    current_z = Z_INTERVAL * segment_step
    current_t = current_z / HELIX_C
    current_x = HELIX_R * math.cos(current_t)
    current_y = HELIX_R * math.sin(current_t)
    rot_z = z_rotation(current_x, current_y, current_t)
    rot_y = Z_INTERVAL / SEGMENT_LENGTH * 180 / math.pi
    """
    helix2 has a mirrored x, y, and rot_y
    """
    if helix == 2:
        current_x = -current_x
        current_y = -current_y
        rot_y = -rot_y
    """
    do the inverse of what would have been done to move the segment from the origin to its placement
    """
    translated_segment = translate([-current_x, -current_y, -current_z])(translated_segment)
    translated_segment = rotate([0, 0, rot_z])(translated_segment)
    translated_segment = rotate([0, -rot_y, 0])(translated_segment)
    return translated_segment


def create_segment(segment_step, helix=1):
    current_z = Z_INTERVAL * segment_step
    current_t = current_z / HELIX_C
    current_x = HELIX_R * math.cos(current_t)
    current_y = HELIX_R * math.sin(current_t)
    rot_z = z_rotation(current_x, current_y, current_t)
    """
    get the local y rotation of the segment
    we calculate rise over run as rise = change in z (the Z_INTERVAL) and
    run = the length of the side calculated above. to get the angle  we take the arctangent of this ratio
    """
    rot_y = Z_INTERVAL / SEGMENT_LENGTH * 180 / math.pi
    """
    helix2 has a mirrored x, y, and rot_y
    """
    if helix == 2:
        current_x = -current_x
        current_y = -current_y
        rot_y = -rot_y
    """
    create an OPENSCAD cube with the calculated dimensions at the calculated coordinates
    """
    geo = cube([SEGMENT_LENGTH, SEGMENT_THICKNESS, SEGMENT_HEIGHT], center=True)
    """
     even-numbered segments get a tab which appears attached to either side, 
     which will be matched with a slot in odd-numbered segments later.
    """
    if segment_step % 2 == 0:
        tab = cube([SEGMENT_LENGTH + TAB_WIDTH * 2, TAB_THICKNESS, TAB_HEIGHT], center=True)
        geo += tab

    geo = rotate([0, rot_y, -rot_z])(geo)
    geo = translate([current_x, current_y, current_z])(geo)
    """
    even-numbered segments also get a hole punched by a cylinder representing a pencil
    """
    if segment_step % 2 == 0:
        pencil_z = math.atan(current_y / current_x) * 180 / math.pi
        pencil = cylinder(r=PENCIL_RADIUS, h=3 * HELIX_R, segments=32, center=True)
        pencil = rotate([0, 90, pencil_z])(pencil)
        pencil = translate([0, 0, current_z])(pencil)
        geo = geo + hole()(pencil)
    return geo


world_geo = None
s = 1
while s <= HELIX_SEGMENTS:
    segment = create_segment(s)
    if world_geo is None:
        world_geo = segment
    else:
        world_geo += segment
    world_geo += create_segment(s, helix=2)
    s += 1
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
scad_render_to_file(world_geo, filepath=filepath, include_orig_code=False)

"""
output a hollow piece to its own scad file
"""
hollow_segment = create_segment(4)
hollow_segment = return_segment_to_origin(hollow_segment, 4)
hollow_segment = rotate([90, 0, 0])(hollow_segment)
filepath = os.path.join(os.getcwd(), 'hollow.scad')
scad_render_to_file(hollow_segment, filepath=filepath, include_orig_code=False)
"""
create a solid piece, subtract neighboring hollow pieces, output it to file
"""
lower_hollow_segment = create_segment(4)
upper_hollow_segment = create_segment(6)
solid_segment = create_segment(5)
carved_segment = solid_segment + hole()(lower_hollow_segment) + hole()(upper_hollow_segment)
carved_segment = return_segment_to_origin(carved_segment, 5)
filepath = os.path.join(os.getcwd(), 'solid.scad')
scad_render_to_file(carved_segment, filepath=filepath, include_orig_code=False)
"""
create a base, embed two solid segments and then subtract the two neighboring hollow segmments
"""
base = cylinder(h=CAP_HEIGHT, r=CAP_R, segments=CAP_SEGMENTS, center=False)
base = translate([0, 0, CAP_OFFSET_Z])(base)
base += create_segment(1)
base += create_segment(1, helix=2)
base = base + hole()(create_segment(2))
base = base + hole()(create_segment(2, helix=2))
filepath = os.path.join(os.getcwd(), 'base.scad')
scad_render_to_file(base, filepath=filepath, include_orig_code=False)
