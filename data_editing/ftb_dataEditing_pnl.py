import bpy
import bpy.utils
from bpy.types import Panel


class FTB_PT_DataEditing_Panel(Panel):
    bl_label = "Data Editing"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    bpy.types.WindowManager.lineUsage = bpy.props.EnumProperty(
        name="Usage",
        description="How to use this object in lineart calculation",
        items=[
            ('INHERIT', "Inherit", "Use settings from parent collection."),
            ('INCLUDE', "Include", "Generate feature lines for this object's data."),
            ('OCCLUSION_ONLY', "Occlusion Only",
             "Only use the object data to produce occlusion"),
            ('EXCLUDE', "Exclude", "Do not use this object."),
            ('INTERSECTION_ONLY', "Intersection Only",
             "Only generate intersection lines for this collection."),
            ('NO_INTERSECTION', "No Intersection",
             "Include this object but do not generate intersection lines.")
        ]
    )

    def draw(self, context):
        layout = self.layout

        col = layout.column()
        col.label(text="Copy Attributes")

        col = layout.column(align=True)
        col.operator("object.copy_location")
        col.operator("object.copy_rotation")
        col.operator("object.copy_scale")

        col = layout.column()
        col.separator()

        col = layout.column()
        col.label(text="Lineart")

        col = layout.column()
        col.prop(bpy.context.window_manager, "lineUsage")

        col = layout.column()
        col.operator("object.set_lineart_settings")

        col = layout.column()
        col.separator()

        col = layout.column()
        col.label(text="Library Override")

        col = layout.column()
        col.operator("object.override_retain_transform")

        col = layout.column()
        col.label(text="Naming")

        col = layout.column()
        col.operator("object.object_name_to_material")

        col = layout.column()
        col.operator("object.collection_name_to_material")


class FTB_PT_DataEditingDanger_Panel(Panel):
    bl_label = "Danger Zone"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FTB"
    bl_parent_id = "FTB_PT_DataEditing_Panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.operator("object.remove_all_materials",
                     text="Remove All Materials")
        col.operator("data.purge_unused", text="Purge Data")


def register():
    bpy.utils.register_class(FTB_PT_DataEditing_Panel)
    bpy.utils.register_class(FTB_PT_DataEditingDanger_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_DataEditingDanger_Panel)
    bpy.utils.unregister_class(FTB_PT_DataEditing_Panel)
