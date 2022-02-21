import io
import bpy
import bmesh
import bpy.utils

from contextlib import redirect_stdout
from bpy.types import Operator

def IsLaubbaumNodeGroup(Modifier):
    return Modifier.node_group.inputs[0].name == "Geometry" and Modifier.node_group.inputs[1].name == "Particle Objects" and Modifier.node_group.inputs[2].name == "Particles | Distance Min"

def RecalculateNormals(Object):
    if not Object.type == 'MESH':
        return

    # bpy.ops method
    #    bpy.ops.object.mode_set(mode='EDIT')
    #    bpy.ops.mesh.select_all(action='SELECT')
    #    bpy.ops.mesh.normals_make_consistent(inside=False)
    #    bpy.ops.object.editmode_toggle()

    # bpy.ops free method
    bm = bmesh.new()
    mesh = Object.data
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.clear()
    mesh.update()
    bm.free()

def ApplyShapeKeys(Object):
    if not Object.type in ['MESH', 'CURVE'] or Object.data.shape_keys is None:
        return
    
    Object.shape_key_add(name='CombinedKeys', from_mix=True)
    if Object.data.shape_keys:
        for shapeKey in Object.data.shape_keys.key_blocks:
            Object.shape_key_remove(shapeKey)
            
def RemoveSpecialChars(Object):
    name = Object.name_full
    specialchars = ["ä", "Ä", "ü", "Ü", "ö", "Ö", "ß", ":", ")", "("]
    replacechars = ["ae", "AE", "ue", "UE", "oe", "OE", "ss" , "", "", ""]

    umlaut = 0
    for char in specialchars:
        umlaut += name.find(char)
    
    # break out if no special char found
    if umlaut == (len(specialchars) * -1):
        return
    
    for i in range(len(specialchars)):
        Object.name = Object.name_full.replace(specialchars[i], replacechars[i])

def ApplyModifiers(Object):
    bSuccessful = True
    for mod in Object.modifiers:
        # check for gnodes-laubbaum
        if mod.type == 'NODES':
            if IsLaubbaumNodeGroup(mod):
                Object.modifiers.remove(mod)
                return bSuccessful

        try:
            with redirect_stdout(io.StringIO()):
                bpy.ops.object.modifier_apply(modifier=mod.name)
        except RuntimeError as err:
            bSuccessful = False
            print(Object.name_full + "[" + Object.type + "] - " + mod.name + " Modifier - " + str(err), end="")

    return bSuccessful

def ConvertCurvesToMesh(Object):
    if Object.type == 'CURVE':
        # check for mesh curves and convert them otherwise skip conversion
        curve = Object.data
        bMeshCurve = curve.extrude > 0 or curve.bevel_depth > 0 or curve.bevel_object != None
        if bMeshCurve:
            bpy.ops.object.convert(target='MESH')
    elif Object.type in ['FONT', 'META', 'SURFACE']:
        bpy.ops.object.convert(target='MESH')

class FTB_OT_UEExport_Op(Operator):
    bl_idname = "utils.basicprep"
    bl_label = "Basic Export Preparation"
    bl_description = "Runs various steps on all objects in the scene which will take quite some time on larger scenes."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bModsApplied = True
        objBlacklist =  ['CAMERA', 'GPENCIL', 'LIGHT', 'LIGHT_PROBE', 'LATTICE', 'EMPTY', 'SPEAKER', 'ARMATURE']

        # dissolve linked assets and make them local
        bpy.ops.object.make_local(type='ALL')
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)

        scene = bpy.context.scene
        for object in scene.objects:
            if not object.visible_get() or object.type in objBlacklist:
                continue

            # unhide objects to select and set them active 
            object.hide_set(False)
            object.hide_viewport = False   
            object.select_set(True)
            bpy.context.view_layer.objects.active = object
            
            # try and run basic export steps on currently active object. The order here is relevant and should not be changed
            bpy.ops.object.make_single_user(object=True, obdata=True, material=True, animation=False, obdata_animation=False)
            ApplyShapeKeys(object)
            ConvertCurvesToMesh(object)
            bModsApplied &= ApplyModifiers(object)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            RecalculateNormals(object)
            RemoveSpecialChars(object)

            object.select_set(False)

        if bModsApplied:
            self.report({'INFO'}, "Basic Export Preparation Done")
        else:
            self.report({'WARNING'}, "Failed to apply some modifiers! Check system console for details.")

        return {'FINISHED'}

class FTB_OT_MaterialPrep_Op(Operator):
    bl_idname = "utils.materialprep"
    bl_label = "Material Preparation"
    bl_description = "Clears all exisiting materials and adds an empty slot. This is run for the whole scene regardless of your active selection."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = bpy.context.scene

        for o in scene.objects:
            if not o.type in ['MESH', 'CURVE', 'FONT', 'META', 'SURFACE']:
                continue
            
            o.data.materials.clear()
            o.data.materials.append(None)
            o.active_material_index = 0

        return {'FINISHED'}

class FTB_OT_DissolveCollections_Op(Operator):
    bl_idname = "utils.dissolvecollections"
    bl_label = "Dissolve Collections"
    bl_description = "Dissolves all collections inside the Scene Collection while keeping all objects"
    bl_options = {"REGISTER", "UNDO"}
                
    def execute(self, context):
        collections = bpy.data.collections

        if len(collections) == 0:
            self.report({'INFO'}, "No collections to remove")
            return {'CANCELLED'}

        count = 0
        for c in collections:
            for o in c.objects:
                bInSceneCollection = False
                for uc in o.users_collection:
                    if uc == bpy.context.scene.collection:
                        bInSceneCollection = True
                
                if not bInSceneCollection:
                    bpy.context.scene.collection.objects.link(o)
            
            bpy.data.collections.remove(c)
            count += 1

        self.report({'INFO'}, "Successfully removed " + str(count) + " collections.")
        return {'FINISHED'}

class FTB_OT_DeleteModifiers_Op(Operator):
    bl_idname = "utils.deletemods"
    bl_label = "Delete All Modifiers"
    bl_description = "Delete all modifiers on all objects in the scene. Can be used to remove defunct modifiers that could not be applied."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        count = 0
        scene = bpy.context.scene
        for object in scene.objects:
            for mod in object.modifiers:
                object.modifiers.remove(mod)
                count += 1

        if count > 0:
            self.report({'INFO'}, "Successfully removed " + str(count) + " modifiers.")
        else:
            self.report({'INFO'}, "No modifiers to remove")

        return {'FINISHED'}

class FTB_OT_FlipNormals_Op(Operator):
    bl_idname = "object.flipnormals"
    bl_label = "Flip Normals - Selected"
    bl_description = "Flip Normals on your active selection"
    bl_options = {"REGISTER", "UNDO"}
    
    @classmethod
    def poll(cls, context):
        if len(bpy.context.selected_objects) == 0:
            return False

        return True

    def execute(self, context):
        bTaskDone = False
        count = 0
        so = bpy.context.selected_objects
        for obj in so:
            if not obj.type == 'MESH':
                continue

            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.flip_normals()
            bpy.ops.object.editmode_toggle()
            
            obj.select_set(False)

            bTaskDone = True
            count += 1

        if bTaskDone:
            self.report({'INFO'}, "Normals flipped for " + str(count) + " meshes")
        else:
            self.report({'INFO'}, "No meshes in active selection")

        return {'FINISHED'}

def register():
    bpy.utils.register_class(FTB_OT_UEExport_Op)
    bpy.utils.register_class(FTB_OT_MaterialPrep_Op)
    bpy.utils.register_class(FTB_OT_DissolveCollections_Op)
    bpy.utils.register_class(FTB_OT_DeleteModifiers_Op)
    bpy.utils.register_class(FTB_OT_FlipNormals_Op)

def unregister():
    bpy.utils.unregister_class(FTB_OT_FlipNormals_Op)
    bpy.utils.unregister_class(FTB_OT_DeleteModifiers_Op)
    bpy.utils.unregister_class(FTB_OT_DissolveCollections_Op)
    bpy.utils.unregister_class(FTB_OT_MaterialPrep_Op)
    bpy.utils.unregister_class(FTB_OT_UEExport_Op)