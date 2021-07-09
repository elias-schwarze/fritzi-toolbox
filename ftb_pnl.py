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
                col.label(text="Copy Attributes")

                col = layout.column(align=True)
                col.operator("object.copy_location")
                col.operator("object.copy_rotation")
                col.operator("object.copy_scale")

                col = layout.column(align=True)
                col.label(text="Scale Checking")

                col.operator("object.select_scale_non_one")
                col.operator("object.select_scale_non_unform")

                col = layout.column(align=True)
                col.label(text="Origin")

                col.operator("object.center_object")
                
                col.operator("object.origin_to_cursor")

                col = layout.column()
                col.label(text="Mesh Checking")
                col.operator("object.check_ngons")



class FTB_PT_DataEditing_Panel(Panel):
        bl_label = "Data Editing" 
        bl_space_type = "VIEW_3D"
        bl_region_type = "UI"
        bl_category = "FTB"
        bl_options = {"DEFAULT_CLOSED"}

        def draw(self, context):
                layout = self.layout

                col = layout.column()
                col.operator("object.override_retain_transform")

                col = layout.column(align=True)
                col.operator("object.remove_all_materials", text="Remove All Materials")
                col.operator("data.purge_unused", text="Purge Data", icon='ERROR')
