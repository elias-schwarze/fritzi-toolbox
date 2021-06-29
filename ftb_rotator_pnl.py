import bpy

from bpy.types import Panel

class FTB_PT_Rotator_Panel(Panel):
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_label = "Batch Rotator" 
        bl_category = "FTB"

        def draw(self, context):
            layout = self.layout
            col = layout.column()