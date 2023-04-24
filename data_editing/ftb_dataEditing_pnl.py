import bpy
from bpy.types import Panel, UIList
from .ftb_dataEditing_op import BinToDec

bpy.types.Scene.active_view_layer = bpy.props.IntProperty(
    name="Active View Layer in the view layer management list",
    default=0
)


def get_all_layer_collection_children(collection: bpy.types.LayerCollection):
    view_layer_collections: bpy.types.LayerCollection = list()

    if collection.children:
        for child in collection.children:
            if child.children:
                view_layer_collections += (get_all_layer_collection_children(child))
            view_layer_collections.append(child)

    return view_layer_collections


def draw_outliner_tools(self, context):
    if context.selected_ids:
        if getattr(context.selected_ids[0], "filepath", None):
            layout = self.layout
            layout.separator()
            layout.operator("outliner.get_absolute_path").relpath = context.selected_ids[0].filepath


def draw_mat_gnodes_menu(self, context):
    if context.object.material_slots:
        obj = context.object
        if obj.material_slots[obj.active_material_index].material:
            layout = self.layout
            layout.separator()

            gnodesMatName = obj.material_slots[obj.active_material_index].material.name
            if obj.material_slots[obj.active_material_index].link == 'DATA':
                if len(obj.material_slots) > 1:
                    gnodesOp = layout.operator("object.set_gnodes_materials", text="Replace By Material")
                    gnodesOp.replaceMode = 'REPLACE'
                    gnodesOp.matName = gnodesMatName
                else:
                    gnodesOp = layout.operator("object.set_gnodes_materials", text="Set By Material")
                    gnodesOp.replaceMode = 'SET'
                    gnodesOp.matName = gnodesMatName

            gnodesIndexOp = layout.operator("object.set_gnodes_materials", text="Replace By Index")
            gnodesIndexOp.replaceMode = 'INDEX'
            gnodesIndexOp.matIndex = obj.active_material_index
            gnodesIndexOp.matName = gnodesMatName


def add_to_dopesheet_context_menu(self, context):
    self.layout.operator("scene.set_shot_range")


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
        name="Set link to...",
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

    bpy.types.WindowManager.ftbSubdivEqualScope = bpy.props.EnumProperty(
        name="Scope",
        description="Limit operation to certain objects",
        items=[
            ('VIEW_LAYER', "View Layer",
             "Limit to objects in current view layer."),
            ('SELECTION', "Selection", "Limit to currently selected objects."),
            ('ALL', "All",
             "Apply to all objects in .blend File (unless object is linked without override)"),
        ],
        default='VIEW_LAYER'
    )

    bpy.types.WindowManager.ftbSubdivEqualTarget = bpy.props.EnumProperty(
        name="Target Level",
        description="How subidv levels should be equalized",
        items=[
            ('RENDER', "Render",
             "All viewport levels will be set to their respective render levels"),
            ('VIEWPORT', "Viewport",
             "All render levels will be set to their respective viewport levels")
        ],
        default='RENDER'
    )

    bpy.types.WindowManager.ftbBoolScope = bpy.props.EnumProperty(
        name="Scope",
        description="Limit operation to whole scene or certain collections",
        items=[
            ('ALL', "All", "All Objects in the .blend file"),
            ('COLLECTION', "Collection", "Limit to a collection and it's children."),
            ('SELECTION', "Selection", "Limit to currently selected objects.")
        ],
        default='ALL'
    )

    bpy.types.WindowManager.ftbBoolCollection = bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection
    )

    bpy.types.WindowManager.ftbLatticeScope = bpy.props.EnumProperty(
        name="Scope",
        description="Limit operation to whole scene or selection",
        items=[
            ('ALL', "All", "All Objects in the .blend file"),
            ('SELECTION', "Selection", "Limit to currently selected objects.")
        ],
        default='ALL'
    )

    bpy.types.WindowManager.ftbVisibilityScope = bpy.props.EnumProperty(
        name="Scope",
        description="Limit operation to objects, collections or selection",
        items=[
            ('OBJECTS', "ALL Objects", "Only the Objects in the .blend file"),
            ('COLLECTIONS', "ALL Collections", "Only the Collections in the file"),
            ('OBJ_IN_COLLECTION', "ALL Objects in Collection", "Limit to Objects inside a given Collection"),
            ('COL_IN_COLLECTION', "ALL Collections in Collection", "Limit to Collections inside a given Collection")
        ],
        default='OBJECTS'
    )

    bpy.types.WindowManager.ftbVisibilityCollection = bpy.props.PointerProperty(
        name="Collection",
        type=bpy.types.Collection
    )

    def draw(self, context):
        layout = self.layout
        # col = layout.column()

        # col.label(text="Active Object:")
        # col.operator("object.center_object")
        # col.operator("object.origin_to_cursor")

        # col.label(text="Copy Attributes:")

        # col = layout.column(align=True)
        # col.operator("object.copy_location")
        # col.operator("object.copy_rotation")
        # col.operator("object.copy_scale")

        # col = layout.column()
        # col.separator()

        col = layout.column()
        col.label(text="Material Operations:")

        col.prop(bpy.context.window_manager, "matSlotLinkLimit")

        btnLabel = "Set Links To Object"
        iconEnum = 'OBJECT_DATAMODE'
        if context.window_manager.matSlotLink == 'OBJECT':
            btnLabel = "Set Links To Object"
            iconEnum = 'OBJECT_DATAMODE'
        elif context.window_manager.matSlotLink == 'DATA':
            btnLabel = "Set Links To Mesh"
            iconEnum = 'OUTLINER_DATA_MESH'

        row = col.row(align=True)
        row.operator("object.set_material_links", text=btnLabel)
        row.prop(context.window_manager, "matSlotLink", icon_only=True, icon=iconEnum)

        col.operator("object.clear_material_slots", text="Clear Slots")

        col = layout.column()
        col.separator()

        col = layout.column()
        col.label(text="Subdivision:")

        col = layout.column()
        col.label(text="Target Level:")

        row = layout.row()
        row.prop(bpy.context.window_manager, "ftbSubdivEqualTarget", expand=True)

        col = layout.column()
        col.prop(bpy.context.window_manager, "ftbSubdivEqualScope")

        col.operator("object.equalize_subdiv", text="Equalize Subdiv Levels").useVisibility = False
        col.operator("object.equalize_subdiv", text="Equalize Subdiv Visibility").useVisibility = True

        col = layout.column()
        col.separator()

        col = layout.column()
        col.label(text="Lineart:")

        col = layout.column()
        col.prop(bpy.context.window_manager, "lineUsage")

        col = layout.column()
        col.operator("object.set_lineart_settings")

        row = col.row(align=True)
        row.operator("scene.reset_lineart_settings")

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

        col = layout.column()
        col.separator()

        col = layout.column()
        col.label(text="Booleans:")

        col = layout.column()
        col.prop(bpy.context.window_manager, "ftbBoolScope")

        if bpy.context.window_manager.ftbBoolScope == 'COLLECTION':
            col = layout.column()
            col.prop_search(bpy.context.window_manager, "ftbBoolCollection", bpy.data, "collections")

        col = layout.column()
        row = col.row(align=True)
        row.operator("object.set_exact_booleans")
        row.operator("object.set_fast_booleans")
        row = col.row(align=True)
        row.operator("object.self_intersection_booleans")
        row.operator("object.hole_tolerant_booleans")

        col = layout.column()
        row = col.row(align=True)
        row.operator("object.hide_booleans_viewport", text="Hide", icon='RESTRICT_VIEW_ON')
        row.operator("object.unhide_booleans_viewport", text="Show", icon='RESTRICT_VIEW_OFF')

        col = layout.column()
        row = col.row(align=True)
        row.operator("object.hide_booleans_render", text="Hide", icon='RESTRICT_RENDER_ON')
        row.operator("object.unhide_booleans_render", text="Show", icon='RESTRICT_RENDER_OFF')

        col = layout.column()
        col.separator()

        col = layout.column()
        col.label(text="Lattice:")

        col = layout.column()
        col.prop(bpy.context.window_manager, "ftbLatticeScope")

        col = layout.column()
        row = col.row(align=True)
        row.operator("object.hide_lattice_modifiers", text="Hide", icon='RESTRICT_VIEW_ON').showViewport = False
        row.operator("object.hide_lattice_modifiers", text="Show", icon='RESTRICT_VIEW_OFF').showViewport = True

        
        # Objects/Collections Visibility Editing
        col = layout.column()
        col.separator()
        col.label(text="Visibilities:")
        col.prop(bpy.context.window_manager, "ftbVisibilityScope")
        if bpy.context.window_manager.ftbVisibilityScope in {'OBJ_IN_COLLECTION', 'COL_IN_COLLECTION'}:
            col.prop_search(bpy.context.window_manager, "ftbVisibilityCollection", bpy.data, "collections")
        col.operator("ftb.conform_visibilities", text="Use Render Visibility", icon='RESTRICT_RENDER_OFF').use_render = True
        col.operator("ftb.conform_visibilities", text="Use Viewport Visibility", icon='RESTRICT_VIEW_OFF').use_render = False




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

                            nameString = mod.name + ": "
                            layerNumberString = str(BinToDec(mod.use_intersection_mask))

                            # create warning string if "Exact Match" option is unchecked
                            if not mod.use_intersection_match:
                                layerNumberString = layerNumberString + ", Exact Match disabled!"

                            row = layout.row()

                            row.label(text=nameString)
                            row.label(text=layerNumberString)

                            usageString = ""

                            for usage in mod.use_intersection_mask:
                                if usage:
                                    usageString = usageString + "X"
                                else:
                                    usageString = usageString + "0"
                            outputString = usageString[0:4] + " | " + usageString[4:8]

                            row.label(text=outputString)


class FTB_UL_ViewLayer_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property):
        layout.scale_x = 1.2
        if self.layout_type in {'DEFAULT', 'COMPACT', 'GRID'}:
            if item:
                layout.label(text=item.name)
                icon_str = ('RESTRICT_RENDER_ON', 'RESTRICT_RENDER_OFF')[item.use]
                layout.prop(item, "use", text="", icon=icon_str)


# probably not possible to use this for bpy.types.LayerCollections
class FTB_UL_ViewLayerCollections_List(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property):
        if self.layout_type in {'DEFAULT', 'COMPACT', 'GRID'}:
            if item:
                layout.label(text=item.name, icon='OUTLINER_COLLECTION')
                vcol = get_all_layer_collection_children(
                    context.scene.view_layers[0].layer_collection)
                for vlayer in context.scene.view_layers:
                    for collection in vcol:
                        if collection.name != item.name:
                            continue
                        layout.prop(collection, "exclude", text="", emboss=False)


class FTB_PT_ViewLayerManagement_Panel(Panel):
    bl_label = "View Layer Management"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    bl_category = "FTB"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # list header
        row = layout.row(align=True)
        row.label(text="Name")
        split = row.split(factor=0.8)
        split.alignment = 'RIGHT'
        split.label(text="Render")
        # draw list
        list_data = context.scene
        layout.template_list("FTB_UL_ViewLayer_List", "", list_data,
                             "view_layers", list_data, "active_view_layer")

        # draw list
        # list_data = get_all_layer_collection_children(
        #     context.scene.view_layers[0].layer_collection)
        # layout.template_list("FTB_UL_ViewLayerCollections_List", "",
        #                      list_data, "children", context.scene, "active_view_layer_collection")


class FTB_PT_ViewLayerManagementCollections_Panel(Panel):
    bl_label = "Collection Excludes"
    bl_parent_id = "FTB_PT_ViewLayerManagement_Panel"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    bl_category = "FTB"

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.alignment = 'CENTER'

        if context.scene.active_view_layer < len(context.scene.view_layers):
            # list header
            row = layout.row(align=True)
            row.label(text="Name")
            split = row.split(factor=0.8)
            split.alignment = 'RIGHT'
            split.label(text="Exclude")

            # draw list
            box = layout.box()
            box.scale_x = 1.5
            box.scale_y = 0.5

            viewlayer_collections = sorted(get_all_layer_collection_children(
                context.scene.view_layers[context.scene.active_view_layer].layer_collection),
                key=lambda name: name.name)
            for col in viewlayer_collections:
                row = box.row(align=True)
                row.label(text=col.name, icon='OUTLINER_COLLECTION')
                row.prop(col, "exclude", text="", emboss=False)
        else:
            row.label(text="Please select a View Layer in the list above")


class FTB_PT_ShotFixing_Panel(Panel):
    bl_label = "Shot Fixing"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "FTB"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("scene.split_in_shots")


classes = (
    FTB_PT_DataEditing_Panel, FTB_PT_CollectionLineUsage_Panel, FTB_UL_ViewLayer_List, FTB_UL_ViewLayerCollections_List,
    FTB_PT_ViewLayerManagement_Panel, FTB_PT_ViewLayerManagementCollections_Panel, FTB_PT_ShotFixing_Panel
)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.types.OUTLINER_MT_context_menu.append(draw_outliner_tools)
    bpy.types.MATERIAL_MT_context_menu.append(draw_mat_gnodes_menu)
    bpy.types.DOPESHEET_MT_context_menu.append(add_to_dopesheet_context_menu)


def unregister():
    bpy.types.DOPESHEET_MT_context_menu.remove(add_to_dopesheet_context_menu)
    bpy.types.MATERIAL_MT_context_menu.remove(draw_mat_gnodes_menu)
    bpy.types.OUTLINER_MT_context_menu.remove(draw_outliner_tools)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
