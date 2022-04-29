import bpy
from bpy.types import Panel
from .ftb_dataEditing_op import BinToDec


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
        ],
        default='INHERIT'
    )

    bpy.types.WindowManager.matSlotLink = bpy.props.EnumProperty(
        name="Set to",
        description="Material slot link type",
        items=[
            ('OBJECT', "Object", "Material Slots linked to object data"),
            ('DATA', "Data", "Material Slots linked to mesh data")
        ],
        default='OBJECT'
    )

    bpy.types.WindowManager.matSlotLinkLimit = bpy.props.EnumProperty(
        name="Limit",
        description="Limit operation to certain objects",
        items=[
            ('VIEW_LAYER', "View Layer",
             "Limit to objects in current view layer."),
            ('COLLECTION', "Active Collection",
             "Limit to objects in active collection."),
            ('SELECTION', "Selection", "Limit to currently selected objects.")
        ],
        default='VIEW_LAYER'
    )

    def draw(self, context):
        layout = self.layout

        col = layout.column()

        col.label(text = "Active Object:")
        col.operator("object.center_object")
        col.operator("object.origin_to_cursor")

        col.label(text="Copy Attributes:")

        col = layout.column(align=True)
        col.operator("object.copy_location")
        col.operator("object.copy_rotation")
        col.operator("object.copy_scale")

        col = layout.column()
        col.separator()

        col = layout.column()
        col.label(text="Material Slot Types:")

        col = layout.column()
        col.prop(bpy.context.window_manager, "matSlotLink")

        col = layout.column()
        col.prop(bpy.context.window_manager, "matSlotLinkLimit")

        col = layout.column()
        col.operator("object.set_material_links")

        col = layout.column()
        col.separator()

        col = layout.column()
        col.label(text="Lineart:")

        col = layout.column()
        col.prop(bpy.context.window_manager, "lineUsage")

        col = layout.column()
        col.operator("object.set_lineart_settings")

        col = layout.column()
        col.separator()

        col = layout.column()
        col.label(text="Library Override:")

        col = layout.column()
        col.operator("object.override_retain_transform")

        col = layout.column()
        col.label(text="Naming:")

        col = layout.column()
        col.operator("object.object_name_to_material")

        col = layout.column()
        col.operator("object.collection_name_to_material")


class FTB_PT_CollectionLineUsage_Panel(Panel):
    bl_label = "Line Art Layer Usage"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'collection'
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        
        if bpy.context.active_object:
            gpobject = bpy.context.active_object

            # check for any valid lineart modifiers
            if gpobject.type == 'GPENCIL':
                if gpobject.grease_pencil_modifiers:
                    for mod in gpobject.grease_pencil_modifiers:
                        if mod.type == 'GP_LINEART':

                            row = layout.row(align=True)

                            nameString = mod.name + ": "
                            layerNumberString = str(BinToDec(mod.use_intersection_mask))

                            # create warning string if "Exact Match" option is unchecked
                            if mod.use_intersection_match == False:
                                layerNumberString = layerNumberString + ", Exact Match disabled!"

                            row.label(text=nameString)
                            row.label(text=layerNumberString)


def register():
    bpy.utils.register_class(FTB_PT_DataEditing_Panel)
    bpy.utils.register_class(FTB_PT_CollectionLineUsage_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_CollectionLineUsage_Panel)
    bpy.utils.unregister_class(FTB_PT_DataEditing_Panel)
