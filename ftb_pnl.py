import bpy

from bpy.types import Panel

class FTB_PT_Checking_Panel(Panel):
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_label = "Object Checking" 
        bl_category = "FTB"

        def draw(self, context):
                layout = self.layout

                col = layout.column()
                col.operator("view.toggle_face_orient", text="Toggle Face Orientation")

                col = layout.column()
                col.label(text="Scale Checking")

                col = layout.column()
                col.operator("object.select_scale_non_one")

                col = layout.column()
                col.operator("object.select_scale_non_unform")

                col = layout.column()
                col.label(text="Origin")

                col = layout.column()
                col.operator("object.center_object")
                
                col = layout.column()
                col.operator("object.origin_to_cursor")

                col = layout.column()
                col.operator("object.check_ngons")



class FTB_PT_DataClean_Panel(Panel):
        bl_parent_id = "FTB_PT_Checking_Panel"
        bl_label = "Data Cleaning" 
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"

        def draw(self, context):
                layout = self.layout

                col = layout.column()
                col.operator("object.remove_all_materials", text="Remove All Materials")

                col = layout.column()
                col.operator("data.purge_unused", text="Purge Data")
