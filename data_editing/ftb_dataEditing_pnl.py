import bpy
from bpy import context
from bpy.props import StringProperty
import bpy.utils
from bpy.types import Panel, WindowManager
from bpy.app.handlers import persistent


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


class FTB_PT_DataEditingDanger_Panel(Panel):
    bl_label = "Danger Zone"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FTB"
    bl_parent_id = "FTB_PT_DataEditing_Panel"
    bl_options = {"DEFAULT_CLOSED"}

    inputType = ''

    # Variable to keep references to data returned by enumShaderInputsFromNodeTree to avoid undefined behavior when using callback function to fill EnumProperty()
    shaderFtbEnum_items = []

    # UI Label text to display data type of current shader Input
    bpy.types.WindowManager.ftbShaderInputDataType = bpy.props.StringProperty()

    bpy.types.WindowManager.ftbShaderType = bpy.props.PointerProperty(name="Shader Group",
                                                                      type=bpy.types.NodeTree)

    bpy.types.WindowManager.editShaderScope = bpy.props.EnumProperty(
        name="Limit To",
        description="Limit operation to certain objects",
        items=[
            ('VIEW_LAYER', "View Layer",
             "Limit to objects in current view layer."),
            ('COLLECTION', "Active Collection",
             "Limit to objects in active collection."),
            ('SELECTION', "Selection",
             "Limit to currently selected objects.")
        ],
        default='VIEW_LAYER'
    )

    # UI Color Picker
    bpy.types.WindowManager.ftbShaderInputColor = bpy.props.FloatVectorProperty(
        name="",
        subtype="COLOR",
        default=(0.5, 0.5, 0.5, 0.5),
        size=4,
        soft_max=1.0,
        soft_min=0.0
    )

    # UI Float Value
    bpy.types.WindowManager.ftbShaderInputValue = bpy.props.FloatProperty(
        name="",
        default=0.0
    )

    # UI Vector Value
    bpy.types.WindowManager.ftbShaderInputVector = bpy.props.FloatVectorProperty(
        name="",
        subtype="XYZ",
        default=(0.0, 0.0, 0.0),
        size=3
    )

    # UI Operation Mode Enum
    bpy.types.WindowManager.ftbShaderOperation = bpy.props.EnumProperty(
        name="Operation:",
        items=[
            ('SET', "Set",
             "Sets the values."),
            ('ADD', "Add",
             "Adds the values. (Use negative value to substract)"),
            ('MUL', "Multiply",
             "Multiply the values. (Decimals and negative values are allowed)")
        ],
        default='SET'
    )

    # load handler to clear any data block referenced by ftbShaderType.
    # If ftbShaderType is referencing a data block in the current blend file and this reference is not cleared when another file is opened,
    # an access violation will occur and Blender will crash.
    # This load handler function is excecuted before a new blend file is opened.

    @persistent
    def preLoad_handler(dummy):
        bpy.context.window_manager.ftbShaderType = None

    bpy.app.handlers.load_pre.append(preLoad_handler)

    def updateShaderInputValues(self):
        wm = bpy.context.window_manager

        if (wm.ftbShaderType is not None):
            for dinput in wm.ftbShaderType.inputs:
                if (dinput.identifier == wm.ftbShaderInput):
                    wm.ftbShaderInputDataType = "Type: " + dinput.type
                    self.inputType = dinput.type

        elif (wm.ftbShaderType is None):
            wm.ftbShaderInputDataType = "Type: None"

    def enumShaderInputsFromNodeTree(self, context):
        """callback function for ftbShaderInput enum property"""
        global shaderFtbEnum_items
        shaderFtbEnum_items = []

        if context is None:
            return shaderFtbEnum_items

        wm = bpy.context.window_manager

        if wm.ftbShaderType is None:
            return shaderFtbEnum_items

        for dinput in reversed(wm.ftbShaderType.inputs):
            appendTuple = (dinput.identifier, dinput.name +
                           " (" + dinput.identifier + ")", "")
            shaderFtbEnum_items.append(appendTuple)

        return shaderFtbEnum_items

    bpy.types.WindowManager.ftbShaderInput = bpy.props.EnumProperty(
        name="Shader Input", items=enumShaderInputsFromNodeTree)

    def draw(self, context):

        wm = bpy.context.window_manager
        layout = self.layout

        col = layout.column()
        col.label(
            text="WARNING! Use at own risk.", icon='ERROR')

        col = layout.column()
        col.operator("object.remove_modifers",
                     text="Remove All Modifiers")

        col = layout.column()
        col.operator("object.remove_all_materials",
                     text="Remove All Materials")

        col = layout.column()
        col.separator()

        col = layout.column()
        col.label(text="Batch Shader Editor: ")

        row = layout.row(align=True)
        row.prop(wm, "ftbShaderOperation", expand=True)

        col = layout.column()
        col.prop(wm, "editShaderScope")

        col = layout.column()

        col.prop_search(data=wm, property="ftbShaderType",
                        search_data=bpy.data, search_property="node_groups")

        if (wm.ftbShaderType != None):

            col = layout.column()
            col.prop(wm, "ftbShaderInput")

            if (wm.ftbShaderInput != None):
                self.updateShaderInputValues()

                col.label(text=wm.ftbShaderInputDataType)

                if (self.inputType == 'RGBA'):
                    col.prop(wm, "ftbShaderInputColor")

                if (self.inputType == 'VALUE'):
                    col.prop(wm, "ftbShaderInputValue")

                if (self.inputType == 'VECTOR'):
                    col.prop(wm, "ftbShaderInputVector")

                col.separator()

                col.operator("material.edit_shader_prop")


def register():
    bpy.utils.register_class(FTB_PT_DataEditing_Panel)
    bpy.utils.register_class(FTB_PT_DataEditingDanger_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_DataEditingDanger_Panel)
    bpy.utils.unregister_class(FTB_PT_DataEditing_Panel)
