import bpy

from bpy.types import Operator

from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Loc
from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Rot
from .. utility_functions.ftb_transform_utils import ob_Copy_Vis_Sca
from .. utility_functions.ftb_string_utils import strip_End_Numbers


class FTB_OT_RemoveMaterials_Op(Operator):
    bl_idname = "object.remove_all_materials"
    bl_label = "Remove All Materials"
    bl_description = "Remove all Material slots from all selected Objects"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        for m in bpy.data.materials:
            bpy.data.materials.remove(m)

        self.report({'INFO'}, 'Removed all Materials')
        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_CopyLocation_Op(Operator):
    bl_idname = "object.copy_location"
    bl_label = "Copy Location"
    bl_description = "Copy location from active object to selected"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):

        sourceObj = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            ob_Copy_Vis_Loc(obj, sourceObj)
        return {'FINISHED'}


class FTB_OT_CopyRotation_Op(Operator):
    bl_idname = "object.copy_rotation"
    bl_label = "Copy Rotation"
    bl_description = "Copy rotation from active object to selected"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):

        sourceObj = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            ob_Copy_Vis_Rot(obj, sourceObj)
        return {'FINISHED'}


class FTB_OT_CopyScale_Op(Operator):
    bl_idname = "object.copy_scale"
    bl_label = "Copy Scale"
    bl_description = "Copy scale from active object to selected"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):

        sourceObj = bpy.context.active_object

        for obj in bpy.context.selected_objects:
            ob_Copy_Vis_Sca(obj, sourceObj)
        return {'FINISHED'}


class FTB_OT_OverrideRetainTransform_Op(Operator):
    bl_idname = "object.override_retain_transform"
    bl_label = "Override Keep Transform"
    bl_description = "Make a library override and retain the transform of the previous instance object"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT" and obj.type == 'EMPTY' and obj.is_instancer:
                return True
        return False

    def execute(self, context):
        objName = context.active_object.name
        objLoc = context.active_object.location
        objRot = context.active_object.rotation_euler
        objScale = context.active_object.scale

        # add new empty object to temporarily store transform and parent matrix of linked object
        tempOb = bpy.data.objects.new(objName + "phx", None)
        bpy.context.scene.collection.objects.link(tempOb)

        # tempOb copy transform from linked object
        ob_Copy_Vis_Loc(tempOb, context.active_object)
        ob_Copy_Vis_Rot(tempOb, context.active_object)
        ob_Copy_Vis_Sca(tempOb, context.active_object)

        # rename the linked object before overriding, so the objects created by
        # library override can have the same name as the original linked object had
        bpy.context.active_object.name = objName + "phName"

        bpy.ops.object.make_override_library()
        newOb = bpy.data.collections[strip_End_Numbers(
            objName)].objects[strip_End_Numbers(objName)]

        ob_Copy_Vis_Loc(newOb, tempOb)
        ob_Copy_Vis_Rot(newOb, tempOb)
        ob_Copy_Vis_Sca(newOb, tempOb)

        bpy.data.objects.remove(tempOb, do_unlink=True)

        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_CollectionNameToMaterial_Op(Operator):
    bl_idname = "object.collection_name_to_material"
    bl_label = "Collection Name To Material"
    bl_description = "Name the active Material the same as the active Collection"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT" and obj.type == 'MESH':
                return True
        return False

    def execute(self, context):
        bpy.context.active_object.active_material.name = bpy.context.collection.name
        return {'FINISHED'}


class FTB_OT_ObjectNameToMaterial_Op(Operator):
    bl_idname = "object.object_name_to_material"
    bl_label = "Object Name To Material"
    bl_description = "Name the active Material the same as the active Object"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT" and obj.type == 'MESH':
                return True
        return False

    def execute(self, context):
        bpy.context.active_object.active_material.name = bpy.context.active_object.name
        return {'FINISHED'}


class FTB_OT_SetLineartSettings_Op(Operator):
    bl_idname = "object.set_lineart_settings"
    bl_label = "Set Line Settings"
    bl_description = "Change Lineart usage for all selected objects at once"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object
        if not obj:
            return True

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            obj.lineart.usage = bpy.context.window_manager.lineUsage
        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_SetMatLinks_Op(Operator):
    bl_idname = "object.set_material_links"
    bl_label = "Set Material Links"
    bl_description = "Set Material Slot links for selected objects"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode

    @classmethod
    def poll(cls, context):
        obj = context.object
        if not obj:
            return True

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def changeMatLinks(self, prop_collection):
        wm = bpy.context.window_manager
        for obj in prop_collection:
            if (obj.type in ['MESH', 'CURVE', 'SURFACE']):

                # Case link = Object
                if (wm.matSlotLink == 'OBJECT'):
                    for slot in obj.material_slots:
                        slot.link = 'OBJECT'

                # Case link = Data
                elif (wm.matSlotLink == 'DATA'):
                    for slot in obj.material_slots:
                        slot.link = 'DATA'

    def execute(self, context):
        wm = bpy.context.window_manager

        # Case limit = View Layer
        if (wm.matSlotLinkLimit == 'VIEW_LAYER'):
            if (not bpy.context.view_layer.objects):
                self.report(
                    {'ERROR'}, "No valid objects found in current view layer")
                return {'CANCELLED'}
            else:
                self.changeMatLinks(bpy.context.view_layer.objects)
                self.report({'INFO'}, "Material slots linked to " +
                            wm.matSlotLink + " for view layer.")

        # Case limit = Active Collection
        if (wm.matSlotLinkLimit == 'COLLECTION'):
            if (not bpy.context.collection):
                self.report({'ERROR'}, "No active collection")
                return {'CANCELLED'}

            else:
                self.changeMatLinks(bpy.context.collection.objects)
                self.report({'INFO'}, "Material slots linked to " +
                            wm.matSlotLink + " for active collection.")

        # Case limit = Current Selection
        if (wm.matSlotLinkLimit == 'SELECTION'):
            if (not bpy.context.selected_objects):
                self.report({'ERROR'}, "No objects selected")

            else:
                self.changeMatLinks(bpy.context.selected_objects)
                self.report({'INFO'}, "Material slots linked to " +
                            wm.matSlotLink + " for selected objects.")

        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_EditShaderProperty_Op(Operator):
    bl_idname = "material.edit_shader_prop"
    bl_label = "Set Shader Property"
    bl_description = "Sets selected shader property to selected value for all materials within scope."
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object
        if not obj:
            return True
        if obj:
            if obj.mode == "OBJECT":
                return True
        return False

    def execute(self, context):

        wm = bpy.context.window_manager

        # Case limit = View Layer
        if (wm.editShaderScope == 'VIEW_LAYER'):
            if (not bpy.context.view_layer.objects):
                self.report(
                    {'ERROR'}, "No valid objects found in current view layer")
                return {'CANCELLED'}
            else:
                self.changeMatLinks(bpy.context.view_layer.objects)
                self.report({'INFO'}, "Material slots linked to " +
                            wm.matSlotLink + " for view layer.")

        # Case limit = Active Collection
        if (wm.editShaderScope == 'COLLECTION'):
            if (not bpy.context.collection):
                self.report({'ERROR'}, "No active collection")
                return {'CANCELLED'}

            else:
                self.changeMatLinks(bpy.context.collection.objects)
                self.report({'INFO'}, "Material slots linked to " +
                            wm.matSlotLink + " for active collection.")

        # Case limit = Current Selection
        if (wm.editShaderScope == 'SELECTION'):
            if (not bpy.context.selected_objects):
                self.report({'ERROR'}, "No objects selected")

            else:
                self.changeMatLinks(bpy.context.selected_objects)
                self.report({'INFO'}, "Material slots linked to " +
                            wm.matSlotLink + " for selected objects.")

        tuch = bpy.data.materials["tuch"]

        for node in tuch.node_tree.nodes:
            if (type(node) == bpy.types.ShaderNodeGroup):

                if (node.node_tree.name == wm.shaderType):
                    for dinput in node.inputs:
                        if dinput.name == "Flat / Shaded Mix":
                            print(dinput.default_value)
                            dinput.default_value = 0.5
        return {'FINISHED'}


class FTB_OT_TestShaderProperty_Op(Operator):
    bl_idname = "material.test_shader_prop"
    bl_label = "test Shader Property"
    bl_description = "tests selected shader property to selected value for all materials within scope."
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object
        if not obj:
            return True
        if obj:
            if obj.mode == "OBJECT":
                return True
        return False

    def execute(self, context):
        wm = bpy.context.window_manager
        for dinput in wm.shaderType.inputs:
            print(dinput.identifier + " : " + dinput.name)

        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_RemoveMaterials_Op)
    bpy.utils.register_class(FTB_OT_OverrideRetainTransform_Op)
    bpy.utils.register_class(FTB_OT_CollectionNameToMaterial_Op)
    bpy.utils.register_class(FTB_OT_ObjectNameToMaterial_Op)
    bpy.utils.register_class(FTB_OT_CopyLocation_Op)
    bpy.utils.register_class(FTB_OT_CopyRotation_Op)
    bpy.utils.register_class(FTB_OT_CopyScale_Op)
    bpy.utils.register_class(FTB_OT_SetLineartSettings_Op)
    bpy.utils.register_class(FTB_OT_SetMatLinks_Op)
    bpy.utils.register_class(FTB_OT_TestShaderProperty_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_TestShaderProperty_Op)
    bpy.utils.unregister_class(FTB_OT_SetMatLinks_Op)
    bpy.utils.unregister_class(FTB_OT_SetLineartSettings_Op)
    bpy.utils.unregister_class(FTB_OT_CopyScale_Op)
    bpy.utils.unregister_class(FTB_OT_CopyRotation_Op)
    bpy.utils.unregister_class(FTB_OT_CopyLocation_Op)
    bpy.utils.unregister_class(FTB_OT_ObjectNameToMaterial_Op)
    bpy.utils.unregister_class(FTB_OT_CollectionNameToMaterial_Op)
    bpy.utils.unregister_class(FTB_OT_OverrideRetainTransform_Op)
    bpy.utils.unregister_class(FTB_OT_RemoveMaterials_Op)
