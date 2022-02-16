import bpy
from bpy.types import Operator
from bpy.app.handlers import persistent


class FTB_OT_RemoveIndexOverrides_Op(Operator):
    bl_idname = "object.remove_index_overrides"
    bl_label = "Remove Index Overrides"
    bl_description = "Remove all overrides of active material index for all objects to prevent material slot errors upon reloading the blend file."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = bpy.context.scene

        for object in scene.objects:
            if not object.override_library:
                continue

            object.active_material_index = object.override_library.reference.active_material_index

            for element in object.override_library.properties:
                if (element.rna_path == "active_material_index"):
                    object.override_library.properties.remove(element)

        return {'FINISHED'}

    @persistent
    def preSave_handler(dummy):
        saveScene = bpy.context.scene

        for object in saveScene.objects:
            if not object.override_library:
                continue

            object.active_material_index = object.override_library.reference.active_material_index

            for element in object.override_library.properties:
                if (element.rna_path == "active_material_index"):
                    object.override_library.properties.remove(element)

        return {'FINISHED'}

    bpy.app.handlers.save_pre.append(preSave_handler)


def register():
    bpy.utils.register_class(FTB_OT_RemoveIndexOverrides_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_RemoveIndexOverrides_Op)
