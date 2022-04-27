import bpy
import bpy.utils

from bpy.types import Panel
from .ftb_materialhelper_op import FindFritziShaderGroup
from ..utility_functions.ftb_path_utils import getFritziPreferences


class FTB_PT_MaterialHelper_Panel(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "Material Helper"
    bl_category = "FTB"
    bl_context = 'material'
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        if (getFritziPreferences().hide_fritzi_shader_warning == False):
            layout = self.layout

            col = layout.column()
            if not FindFritziShaderGroup():
                col.label(text="Fritzi Prop Shader Missing! Please append it.", icon='ERROR')

            col.operator("object.populatematerialslot")

            if context.active_object.override_library:
                col.operator("object.populatematerials")


def register():
    bpy.utils.register_class(FTB_PT_MaterialHelper_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_MaterialHelper_Panel)
