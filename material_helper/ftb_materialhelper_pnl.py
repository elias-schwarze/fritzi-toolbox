import bpy
import bpy.utils

from bpy.types import Panel
from .ftb_materialhelper_op import MaterialHelper

class FTB_PT_MaterialHelper_Panel(Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_label = "Material Helper"
    bl_category = "FTB"
    bl_context = 'material'
    bl_options = {'HIDE_HEADER'} 

    def draw(self, context):

        layout = self.layout

        col = layout.column()
        
        if not MaterialHelper.FritziNodeGroup:
            col.operator("wm.appendfritzishader", text="Fritzi Prop Shader Missing! Click tp append!", icon='ERROR')
        elif not MaterialHelper.BrushTexture:
            col.operator("image.openbrushtexture", text="Brush Texture Missing! Click to import!", icon='ERROR')
        elif not MaterialHelper.SplatTexture:
            col.operator("image.opensplattexture", text="Splat Texture Missing! Click to import!", icon='ERROR')

        col.operator("object.populatematerialslot")
        
        if context.active_object.override_library:
            col.operator("object.populatematerials")

def register():
    bpy.utils.register_class(FTB_PT_MaterialHelper_Panel)

def unregister():
    bpy.utils.unregister_class(FTB_PT_MaterialHelper_Panel)