import bpy
import bmesh

from mathutils import Vector, Matrix
from bmesh.types import BMVert
"""
This file uses a screw modifier to construct the helix solids.
Blender does a terrible job punching holes in things, and I was unable to create a printable version of this approach.
I'm leaving this file here as an example of what not to do, and why.
"""

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
# constants for use below
BUILD_CEILING = 360
CAP_VERTICES = 128
CAP_RADIUS = 75
CAP_DEPTH = 18
CAP_TAPER_DEPTH = 5
CAP_TAPER_RATE = 0.95
CAP_TOP_Z = BUILD_CEILING - CAP_DEPTH/2.0
HELIX_EDGE_OFFSET = 20
HELIX_WIDTH = 20
HELIX_SCREW_OFFSET = 340
HELIX_STEPS = 50
HELIX_RENDER_STEPS = HELIX_STEPS * 2
PENCIL_RADIUS = 5  # the size of the hole for the pencil, not the size of the pencil itself
PENCIL_Z_MIN = CAP_DEPTH + CAP_TAPER_DEPTH + PENCIL_RADIUS*2
PENCIL_Z_MAX = BUILD_CEILING - CAP_DEPTH - CAP_TAPER_DEPTH - PENCIL_RADIUS
"""
create a base from a cylinder, with some tapering
"""
bpy.ops.mesh.primitive_cylinder_add(vertices=CAP_VERTICES, radius=CAP_RADIUS, depth=CAP_DEPTH, location=[0.0, 0.0, CAP_DEPTH/2.0])
bottomCylinder = bpy.context.active_object
bottomCylinder.select_set(False)
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
add a helix, as a cube mesh with a screw modifier
"""
bpy.context.scene.cursor.location = [0.0, 0.0, CAP_DEPTH/2.0]
bpy.ops.mesh.primitive_cube_add(size=HELIX_WIDTH, location=[0.0, CAP_RADIUS - HELIX_EDGE_OFFSET, 1 + CAP_DEPTH/2.0])
helixOne = bpy.context.active_object
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.modifier_add(type='SCREW')
helixOne.modifiers['Screw'].screw_offset = HELIX_SCREW_OFFSET
helixOne.modifiers['Screw'].steps = HELIX_STEPS
helixOne.modifiers['Screw'].render_steps = HELIX_RENDER_STEPS
bpy.ops.object.modifier_apply(modifier='Screw')
bm = bmesh.new()
bm.from_mesh(helixOne.data)
bm.normal_update()
bm.to_mesh(helixOne.data)
bm.free()
bpy.ops.mesh.primitive_cube_add(size=20, location=[0.0, -1 * (CAP_RADIUS - HELIX_EDGE_OFFSET), 1 + CAP_DEPTH/2.0])
helixTwo = bpy.context.active_object
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.modifier_add(type='SCREW')
helixTwo.modifiers['Screw'].screw_offset = HELIX_SCREW_OFFSET
helixTwo.modifiers['Screw'].steps = HELIX_STEPS
helixTwo.modifiers['Screw'].render_steps = HELIX_RENDER_STEPS
bpy.ops.object.modifier_apply(modifier='Screw')
bm = bmesh.new()
bm.from_mesh(helixTwo.data)
bm.normal_update()
bm.to_mesh(helixTwo.data)
bm.free()

"""
create a top, much like the base
"""
bpy.ops.mesh.primitive_cylinder_add(vertices=CAP_VERTICES, radius=CAP_RADIUS, depth=CAP_DEPTH, location=[0.0, 0.0, CAP_TOP_Z])
topCylinder = bpy.context.active_object
topCylinder.select_set(False)
# extrude bottom face up, then scale it in
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
create a set of cylinders to bore the pencil holes in  the helices
todo: fill each hole with a taurus
there are a lot of fine-tuned numbers here to ensure that the Boolean operation succeeded
If any of the base numbers are adjusted, these will need to be fine-tuned again, I'm sure
"""
PENCIL_ROTATION_BASE = 4.325
PENCIL_ROTATION_INC = 0.37
PENCIL_DEPTH = CAP_RADIUS * 2.2
currentPencilZ = PENCIL_Z_MIN
currentRotation = PENCIL_ROTATION_BASE
loopCount = 1
while currentPencilZ < PENCIL_Z_MAX:
    bpy.ops.mesh.primitive_cylinder_add(vertices=CAP_VERTICES, radius=PENCIL_RADIUS, depth=PENCIL_DEPTH,
                                    location=[0.0, 0.0, currentPencilZ], rotation=[currentRotation, 1.57, 0.0])
    pencilObject = bpy.context.active_object
    bm = bmesh.new()
    bm.from_mesh(pencilObject.data)
    bm.normal_update()
    bm.to_mesh(pencilObject.data)
    bm.free()
    pencilObject.select_set(False)
    helixOne.select_set(True)
    bpy.context.view_layer.objects.active = helixOne
    bpy.ops.object.modifier_add(type='BOOLEAN')
    helixOne.modifiers['Boolean'].object = pencilObject
    bpy.ops.object.modifier_apply(modifier='Boolean')
    pencilObject.select_set(True)
    helixOne.select_set(False)
    bpy.context.view_layer.objects.active = pencilObject
    bpy.ops.object.delete()
    bpy.ops.mesh.primitive_cylinder_add(vertices=CAP_VERTICES, radius=PENCIL_RADIUS, depth=PENCIL_DEPTH,
                                    location=[0.0, 0.0, currentPencilZ], rotation=[currentRotation, 1.57, 0.0])
    pencilObject = bpy.context.active_object
    bm = bmesh.new()
    bm.from_mesh(pencilObject.data)
    bm.normal_update()
    bm.to_mesh(pencilObject.data)
    bm.free()
    pencilObject.select_set(False)
    helixTwo.select_set(True)
    bpy.context.view_layer.objects.active = helixTwo
    bpy.ops.object.modifier_add(type='BOOLEAN')
    helixTwo.modifiers['Boolean'].object = pencilObject
    bpy.ops.object.modifier_apply(modifier='Boolean')
    pencilObject.select_set(True)
    helixTwo.select_set(False)
    bpy.context.view_layer.objects.active = pencilObject
    bpy.ops.object.delete()
    loopCount += 1
    if loopCount == 11:
        currentPencilZ += 4 * PENCIL_RADIUS
        currentRotation -= PENCIL_ROTATION_INC
    if loopCount == 12:
        currentRotation -= 0.07
    if loopCount == 13:
        currentRotation -= 0.02
    if loopCount == 14:
        currentRotation += 0.06
    currentPencilZ += 4*PENCIL_RADIUS
    currentRotation -= PENCIL_ROTATION_INC

"""
select the 4 pieces (or maybe I should select all meshes?), make them manifold with the remesh modifier
topCylinder.select_set(True)
bottomCylinder.select_set(True)
helixOne.select_set(True)
helixTwo.select_set(True)
bpy.ops.object.modifier_add(type='REMESH')
topCylinder.modifiers['Remesh'].voxel_size = 1
bpy.ops.object.modifier_apply(modifier='Remesh')
topCylinder.select_set(False)
bottomCylinder.select_set(False)
helixOne.select_set(False)
helixTwo.select_set(False)
"""
