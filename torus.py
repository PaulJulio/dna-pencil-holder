import bpy
import bmesh
import math

from mathutils import Vector, Matrix
from bmesh.types import BMVert

"""
clear the scene
if things go wrong and you need to manually reset, use:
bpy.ops.wm.read_factory_settings()
"""
# Ensure we are in Object Mode
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')
# Select mesh objects by type
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        o.select_set(True)
    else:
        o.select_set(False)
bpy.ops.object.delete()

"""
define constants for use in the build
"""
BUILD_CEILING = 195
CAP_VERTICES = 128
CAP_RADIUS = 75
CAP_DEPTH = 23
CAP_TAPER_DEPTH = 0
CAP_TAPER_RATE = 0.95
CAP_TOP_Z = BUILD_CEILING - CAP_DEPTH/2.0
HELIX_EDGE_OFFSET = 20
TORUS_SPACING = 20  # in mm on the z axis
TORUS_MAJOR_RADIUS = 7.5
TORUS_MINOR_RADIUS = 2.5

"""
create a base from a cylinder, with some tapering
"""
bpy.ops.mesh.primitive_cylinder_add(vertices=CAP_VERTICES, radius=CAP_RADIUS, depth=CAP_DEPTH, location=[0.0, 0.0, CAP_DEPTH/2.0])
bottomCylinder = bpy.context.active_object
bottomCylinder.select_set(False)
"""
# extrude top face up, then scale it in
bm = bmesh.new()
bm.from_mesh(bottomCylinder.data)
bm.faces.ensure_lookup_table()  # can't run the for loop without this
for face in bm.faces:
    vector = face.calc_center_median()
    if vector.z == CAP_DEPTH/2:  # note that this is local space, 10 units above the local center
        topFace = face
        faceCenter = face.calc_center_median()
        break
extrudeGeo = bmesh.ops.extrude_face_region(bm, geom=[topFace])  # the "selection" to extrude
extrudeVector = Vector((0, 0, CAP_TAPER_DEPTH))  # extrude 5 units up
translateVerts = [v for v in extrudeGeo['geom'] if isinstance(v, BMVert)]  # get the vertices to translate
bmesh.ops.translate(bm, vec=extrudeVector, verts=translateVerts)
scalingMatrix = Matrix.Scale(CAP_TAPER_RATE, 4)
scalingTranslation = Matrix.Translation(-faceCenter)
bmesh.ops.transform(bm, verts=translateVerts, space=scalingTranslation, matrix=scalingMatrix)
bm.normal_update()
bm.to_mesh(bottomCylinder.data)
bm.free()
"""

"""
create a top, much like the base
"""
bpy.ops.mesh.primitive_cylinder_add(vertices=CAP_VERTICES, radius=CAP_RADIUS, depth=CAP_DEPTH, location=[0.0, 0.0, CAP_TOP_Z])
topCylinder = bpy.context.active_object
topCylinder.select_set(False)
"""
# extrude bottom face, then scale it in
bm = bmesh.new()
bm.from_mesh(topCylinder.data)
bm.faces.ensure_lookup_table()  # can't run the for loop without this
for face in bm.faces:
    vector = face.calc_center_median()
    if vector.z == CAP_DEPTH/-2:  # note that this is local space, 10 units below the local center
        bottomFace = face
        faceCenter = face.calc_center_median()
        break
extrudeGeo = bmesh.ops.extrude_face_region(bm, geom=[bottomFace])  # the "selection" to extrude
extrudeVector = Vector((0, 0, CAP_TAPER_DEPTH * -1))  # extrude down
translateVerts = [v for v in extrudeGeo['geom'] if isinstance(v, BMVert)]  # get the vertices to translate
bmesh.ops.translate(bm, vec=extrudeVector, verts=translateVerts)
scalingMatrix = Matrix.Scale(CAP_TAPER_RATE, 4)
scalingTranslation = Matrix.Translation(-faceCenter)
bmesh.ops.transform(bm, verts=translateVerts, space=scalingTranslation, matrix=scalingMatrix)
bm.normal_update()
bm.to_mesh(topCylinder.data)
bm.free()
"""

"""
the math behind the helix comes from:
https://mathworld.wolfram.com/Helix.html
"""
helixHeight = BUILD_CEILING - 2 * CAP_DEPTH # note the taper is purposely excluded
# 2(pi)c describes the height between the helix loops, so to get c:
c = helixHeight / 2 / math.pi
r = CAP_RADIUS - HELIX_EDGE_OFFSET
# calculate t given a desired z, insert a taurus
z = CAP_DEPTH + CAP_TAPER_DEPTH/2 + TORUS_SPACING/2
z = CAP_DEPTH + TORUS_MAJOR_RADIUS
ry = 90.0 * math.pi / 180.0
priorx = 0
priory = 0
priorz = 0
while z < BUILD_CEILING - CAP_DEPTH:
    t = z / c
    x = r*math.cos(t)
    y = r*math.sin(t)
    rx = 2 * math.pi - math.atan(y/x)
    bpy.ops.mesh.primitive_torus_add(major_radius=TORUS_MAJOR_RADIUS, minor_radius=TORUS_MINOR_RADIUS,
                                     location=[x, y, z], rotation=[rx, ry, 0.0])
    bpy.ops.mesh.primitive_torus_add(major_radius=TORUS_MAJOR_RADIUS, minor_radius=TORUS_MINOR_RADIUS,
                                     location=[-x, -y, z], rotation=[rx, ry, 0.0])
    if priorz > 0:
        midx = (x + priorx)/2
        midy = (y + priory)/2
        midz = (z + priorz)/2
        # distance between these two points is the depth of the cylinder. got formula from
        # https://www.engineeringtoolbox.com/distance-relationship-between-two-points-d_1854.html
        depth = math.pow(math.pow(priorx - x, 2) + math.pow(priory - y, 2) + math.pow(priorz - z, 2), 0.5)
        rx = math.pi/2 + math.asin( (z - midz) / (depth/2) )
        rz = math.pi/2 + math.atan( (midy - y) / (midx - x) )
        if midx - x < -1 or midy - y < -1:
            print("x diff", midx - x, "y diff", midy - y)
            rz += math.pi
        # connect the top and bottom of the current torus to the prior torus
        # how far is it between these two 3d points? what's the midpoint? what's the angle?
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=TORUS_MINOR_RADIUS * .8,
                                            depth=depth - TORUS_MINOR_RADIUS,
                                            location=[midx, midy, midz + TORUS_MAJOR_RADIUS],
                                            rotation=[rx, 0.0, rz])
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=TORUS_MINOR_RADIUS * .8,
                                            depth=depth - TORUS_MINOR_RADIUS,
                                            location=[midx, midy, midz - TORUS_MAJOR_RADIUS],
                                            rotation=[rx, 0.0, rz])
        midx = -midx
        midy = -midy
        rz += math.pi
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=TORUS_MINOR_RADIUS * .8,
                                            depth=depth - TORUS_MINOR_RADIUS,
                                            location=[midx, midy, midz + TORUS_MAJOR_RADIUS],
                                            rotation=[rx, 0.0, rz])
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=TORUS_MINOR_RADIUS * .8,
                                            depth=depth - TORUS_MINOR_RADIUS,
                                            location=[midx, midy, midz - TORUS_MAJOR_RADIUS],
                                            rotation=[rx, 0.0, rz])
    priorx = x
    priory = y
    priorz = z
    z += TORUS_SPACING
