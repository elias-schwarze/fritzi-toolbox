import bpy
from bpy.types import Operator

class FTB_OT_Apply_All_Op(Operator):
    bl_idname = "object.apply_all_mods"
    bl_label = "Apply all"
    bl_description = "Apply all operators of the active object"

    @classmethod
    def poll(cls, context):
        obj = context.object
 
        if obj is not None:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        #Apply all modifiers of active object
        active_obj = context.view_layer.objects.active

        for mod in active_obj.modifiers:
            bpy.ops.object.modifier_apply(modifier = mod.name)

        return {'FINISHED'}
    

class FTB_OT_Toggle_Face_Orient_Op(Operator):
    bl_idname = "view.toggle_face_orient"
    bl_label = "Toggle Face Orientation"
    bl_description = "Toggle the Face Orientation overlay"

    def execute(self, context):
        if bpy.context.space_data.overlay.show_face_orientation == True:
            bpy.context.space_data.overlay.show_face_orientation = False

        elif bpy.context.space_data.overlay.show_face_orientation == False:
            bpy.context.space_data.overlay.show_face_orientation = True

        return {'FINISHED'} 

class FTB_OT_SelectScaleNonOne_Op(Operator):
    bl_idname = "object.select_scale_non_one"
    bl_label = "Unapplied Scale"
    bl_description = "Select all objects that do not have Scale of (1,1,1)"
    bl_options = {"REGISTER", "UNDO"}

    #should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj is not None:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        for o in bpy.data.objects:
            if o.type == 'MESH':
                if o.scale[0] != 1 or o.scale[1] != 1 or o.scale[2] != 1:
                    o.select_set(True)
        
        return {'FINISHED'}

class FTB_OT_SelectScaleNonUniform_Op(Operator):
    bl_idname = "object.select_scale_non_unform"
    bl_label = "Non Uniform Scale"
    bl_description = "Select all objects that do not have a uniform Scale (x=y=z))"
    bl_options = {"REGISTER", "UNDO"}

    #should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj is not None:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        bpy.ops.object.select_all(action='DESELECT')
        for o in bpy.data.objects:
            if o.type == 'MESH':
                if not (o.scale[0] == o.scale[1] == o.scale[2]):
                    o.select_set(True)
        
        return {'FINISHED'}


class FTB_OT_RemoveMaterials_Op(Operator):
    bl_idname = "object.remove_all_materials"
    bl_label = "Remove All Materials"
    bl_description = "Remove all Material slots from all selected Objects"
    bl_options = {"REGISTER", "UNDO"}

    #should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj is not None:
            if obj.mode == "OBJECT":
                return True

        return False


    def execute(self, context):
        for m in bpy.data.materials:
            bpy.data.materials.remove(m)

        self.report({'INFO'}, 'Removed all Materials')
        return {'FINISHED'}


class FTB_OT_PurgeUnusedData_Op(Operator):
    bl_idname = "data.purge_unused"
    bl_label = "Purge Unused Data"
    bl_description = "Recursively remove all unused Datablocks from file"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)
        self.report({'INFO'}, 'Purged unused Data')
        return {'FINISHED'}

class FTB_OT_SetToCenter_Op(Operator):
    bl_idname = "object.center_object"
    bl_label = "Center Object"
    bl_description = "Set the object to World Origin"
    bl_options = {"REGISTER", "UNDO"}
        
    #should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj is not None:
            if obj.mode == "OBJECT":
                return True

        return False


    def execute(self, context):
        offsetMode = bpy.context.tool_settings.transform_pivot_point
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.context.tool_settings.transform_pivot_point = 'ACTIVE_ELEMENT'
        bpy.ops.view3d.snap_selected_to_cursor(use_offset=True)
        bpy.context.tool_settings.transform_pivot_point = offsetMode
        return {'FINISHED'}

class FTB_OT_OriginToCursor_Op(Operator):
    bl_idname = "object.origin_to_cursor"
    bl_label = "Origin to cursor"
    bl_description = "Set object origin to 3D Cursor"
    bl_options = {"REGISTER", "UNDO"}

    #should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj is not None:
            if obj.mode == "OBJECT":
                return True

        return False


    def execute(self, context):
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        return {'FINISHED'}

class FTB_OT_CheckNgons_Op(Operator):
    bl_idname = "object.check_ngons"
    bl_label = "Check Ngons"
    bl_description = "Select all ngons of active object, if any"
    bl_options = {"REGISTER", "UNDO"}

    #should work in edit and object mode
    @classmethod
    def poll(cls, context):
        obj = context.object
    #test
        if obj is not None:
            if obj.mode == "OBJECT" and obj.type == 'MESH':
                return True

            elif obj.mode == "EDIT" and obj.type == 'MESH':
                return True

        return False

    def execute(self, context):
        obj = context.object
    
        #if in object mode switch to edit and select ngons
        if obj != None and obj.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER', extend=False)
            return {'FINISHED'}

        #if in edit mode select ngons directly
        elif obj != None and obj.mode == 'EDIT':
            bpy.ops.mesh.select_face_by_sides(number=4, type='GREATER', extend=False)
            return {'FINISHED'}

