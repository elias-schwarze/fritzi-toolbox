import bpy
from bpy.types import Operator


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


class FTB_OT_RemoveModifiers_Op(Operator):
    bl_idname = "object.remove_modifers"
    bl_label = "Remove Modifiers"
    bl_description = "Remove all Modifiers from all selected objects"
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
        for obj in bpy.context.selected_objects:
            for mod in obj.modifiers:
                obj.modifiers.remove(mod)
        return{'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_EditShaderProperty_Op(Operator):
    bl_idname = "material.edit_shader_prop"
    bl_label = "Edit Shader Property"
    bl_description = "Sets selected shader property to selected value for all materials within scope."
    bl_options = {"REGISTER", "UNDO"}

    def setShaderProperty(self, materialObject):

        wm = bpy.context.window_manager

        # temporary list of already edited materials, in case some materials are looped over multiple times
        editedMatList = list()

        for matSlot in materialObject.material_slots:
            if matSlot.material is not None:
                if matSlot.material not in editedMatList:
                    editedMatList.append(matSlot.material)
                    if (matSlot.material.node_tree != None):
                        for node in matSlot.material.node_tree.nodes:
                            if (type(node) == bpy.types.ShaderNodeGroup and node.node_tree != None):
                                if (node.node_tree.name == wm.ftbShaderType.name):
                                    for dinput in node.inputs:
                                        if (dinput.identifier == wm.ftbShaderInput):

                                            if (dinput.type == 'RGBA'):

                                                if (wm.ftbShaderOperation == 'SET'):
                                                    dinput.default_value = wm.ftbShaderInputColor

                                                elif (wm.ftbShaderOperation == 'ADD'):
                                                    dinput.default_value[0] += wm.ftbShaderInputColor[0]
                                                    dinput.default_value[1] += wm.ftbShaderInputColor[1]
                                                    dinput.default_value[2] += wm.ftbShaderInputColor[2]
                                                    dinput.default_value[3] += wm.ftbShaderInputColor[3]

                                                elif (wm.ftbShaderOperation == 'MUL'):
                                                    dinput.default_value[0] *= wm.ftbShaderInputColor[0]
                                                    dinput.default_value[1] *= wm.ftbShaderInputColor[1]
                                                    dinput.default_value[2] *= wm.ftbShaderInputColor[2]
                                                    dinput.default_value[3] *= wm.ftbShaderInputColor[3]

                                            if dinput.type == ('VECTOR'):
                                                if (wm.ftbShaderOperation == 'SET'):
                                                    dinput.default_value = wm.ftbShaderInputVector

                                                elif (wm.ftbShaderOperation == 'ADD'):
                                                    dinput.default_value[0] += wm.ftbShaderInputVector[0]
                                                    dinput.default_value[1] += wm.ftbShaderInputVector[1]
                                                    dinput.default_value[2] += wm.ftbShaderInputVector[2]

                                                elif (wm.ftbShaderOperation == 'MUL'):
                                                    dinput.default_value[0] *= wm.ftbShaderInputVector[0]
                                                    dinput.default_value[1] *= wm.ftbShaderInputVector[1]
                                                    dinput.default_value[2] *= wm.ftbShaderInputVector[2]

                                            if dinput.type == ('VALUE'):
                                                if (wm.ftbShaderOperation == 'SET'):
                                                    dinput.default_value = wm.ftbShaderInputValue

                                                elif (wm.ftbShaderOperation == 'ADD'):
                                                    dinput.default_value += wm.ftbShaderInputValue

                                                elif (wm.ftbShaderOperation == 'MUL'):
                                                    dinput.default_value *= wm.ftbShaderInputValue

    def execute(self, context):

        wm = bpy.context.window_manager

        # Case limit = View Layer
        if (wm.editShaderScope == 'VIEW_LAYER'):
            if (not bpy.context.view_layer.objects):
                self.report(
                    {'ERROR'}, "No valid objects found in current view layer")
                return {'CANCELLED'}
            else:
                for obj in bpy.context.view_layer.objects:
                    self.setShaderProperty(obj)

                self.report(
                    {'INFO'}, "Shader property was changed for all materials in view layer.")

        # Case limit = Active Collection
        if (wm.editShaderScope == 'COLLECTION'):
            if (not bpy.context.collection):
                self.report({'ERROR'}, "No active collection")
                return {'CANCELLED'}

            else:
                for obj in bpy.context.collection.all_objects:
                    self.setShaderProperty(obj)

                self.report(
                    {'INFO'}, "Shader property was changed for all materials in active collection.")

        # Case limit = Current Selection
        if (wm.editShaderScope == 'SELECTION'):
            if (not bpy.context.selected_objects):
                self.report({'ERROR'}, "No objects selected")

            else:
                for obj in bpy.context.selected_objects:
                    self.setShaderProperty(obj)
                self.report(
                    {'INFO'}, "Shader property was changed for all materials in selection.")

        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


def register():
    bpy.utils.register_class(FTB_OT_RemoveMaterials_Op)
    bpy.utils.register_class(FTB_OT_RemoveModifiers_Op)
    bpy.utils.register_class(FTB_OT_EditShaderProperty_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_EditShaderProperty_Op)
    bpy.utils.unregister_class(FTB_OT_RemoveModifiers_Op)
    bpy.utils.unregister_class(FTB_OT_RemoveMaterials_Op)
