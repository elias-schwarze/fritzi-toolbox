import bpy
import math
import time
from bpy.types import Operator, ViewLayer, Material, SolidifyModifier, AOV, Collection, Object, Text
from bpy.app.handlers import persistent
from ..utility_functions.ftb_path_utils import getFritziPreferences
from ..utility_functions import ftb_logging as log


IH_VIEWLAYER_NAME = "lines_invertedhull"
IH_OBJECTS_COLLECTION_NAME = "OBJECTS_InvertedHull"
IH_AOV_NAME = "AOV_Inverted_Hull"
IH_MATERIAL_NAME = "mat_inverted_hull_outline"
IH_MODIFIER_NAME = "mod_inverted_hull"
DRIVER_PATHS = ("show_viewport", "show_render")

AOV_COLLECTION_NAME = "OBJECTS_AOVPass"
AOV_PASS_NAME = "AOV_transparent_object"


class FTB_OT_DefaultAddLineart_Op(Operator):
    bl_idname = "object.default_add_lineart"
    bl_label = "Add Default Line Art"
    bl_description = "Add a GPencil Object with the active collection as source. Sets up default Line Art settings."
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if not obj:
            return True
        if obj:
            if obj.mode == "OBJECT":
                return True
        return False

    def invoke(self, context, event):
        if (bpy.context.collection is None):
            self.report(
                {'WARNING'}, "No active collection selected")
            return {'CANCELLED'}

        else:
            return self.execute(context)

    def execute(self, context):
        # bpy.ops.object.gpencil_add(align='WORLD', location=(
        #     0, 0, 0), scale=(1, 1, 1), type='LRT_COLLECTION')
        previewLineData = bpy.data.grease_pencils.new(name='ftb_previewLines')
        previewLineLayer = previewLineData.layers.new(
            "gplayer", set_active=True)
        previewLineLayer.frames.new(frame_number=1)

        previewLineData.stroke_depth_order = '2D'
        previewLineData.pixel_factor = 0.1

        previewLineData.stroke_thickness_space = 'WORLDSPACE'

        previewLineMaterial = bpy.data.materials.new("previewLinesMat")

        # convert material to be grease pencil compatible
        bpy.data.materials.create_gpencil_data(previewLineMaterial)

        previewLineObj = bpy.data.objects.new(
            "ftb_previewLines", previewLineData)

        # assign Material to object
        previewLineObj.data.materials.append(previewLineMaterial)
        previewLineObj.show_in_front = True

        # add line art modifier to gp object
        lineModifier = previewLineObj.grease_pencil_modifiers.new(
            "FS_Lines", 'GP_LINEART')

        lineModifier.target_layer = "gplayer"
        lineModifier.target_material = previewLineMaterial
        lineModifier.source_collection = bpy.context.view_layer.active_layer_collection.collection

        # lineModifier.source_collection
        bpy.context.scene.collection.objects.link(previewLineObj)

        # add thickness modifier to gp object
        thickModifier = previewLineObj.grease_pencil_modifiers.new(
            "FS_Thickness", 'GP_THICK')

        thickModifier.thickness_factor = 2.5
        thickModifier.use_custom_curve = True
        thickModifier.curve.curves[0].points.new(0.25, 0.5)
        thickModifier.curve.curves[0].points.new(0.5, 0.5)
        thickModifier.curve.curves[0].points.new(0.65, 0.85)
        thickModifier.curve.curves[0].points.new(0.85, 0.4)
        thickModifier.curve.update()
        if bpy.context.scene.frame_current < 1:
            bpy.context.scene.frame_set(1)

        return {'FINISHED'}


class FTB_OT_Copy_Optimize_Lines_Op(Operator):
    bl_idname = "outliner.copy_optimize_lines"
    bl_label = "Copy and Delete Lineart Modifier"
    bl_description = "Makes a copy of this GP object and removes lineart modifiers from it. If lines are baked, line layers will render much faster without these modifiers."
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        newName = bpy.context.object.name
        originalLines = bpy.context.object
        bpy.ops.object.duplicate(linked=False, mode='DUMMY')
        dupliLines = bpy.context.object
        lineMods = list()
        for mod in dupliLines.grease_pencil_modifiers:
            if mod.type == 'GP_LINEART':
                lineMods.append(mod)

        if lineMods:
            for item in lineMods:
                dupliLines.grease_pencil_modifiers.remove(item)

        newName += "_baked"
        dupliLines.name = newName

        if originalLines.hide_render is False:
            originalLines.hide_render = True

        if dupliLines.hide_render:
            dupliLines.hide_render = False

        if originalLines.hide_viewport is False:
            originalLines.hide_viewport = True

        if dupliLines.hide_viewport:
            dupliLines.hide_viewport = False

        bpy.context.view_layer.objects.active = originalLines
        bpy.ops.object.lineart_clear()
        bpy.context.view_layer.objects.active = dupliLines
        return {'FINISHED'}


class FTB_OT_Bake_Interval_Op(Operator):
    bl_idname = "object.bake_interval"
    bl_label = "Bake Interval"
    bl_description = "Bakes lineart of active object but in intervals to reduce crashes in large scenes"
    bl_options = {"REGISTER", "UNDO"}

    intervalSize: bpy.props.IntProperty(
        name="Interval Size",
        description="Number of frames baked in a single interval",
        default=30, min=1)
    sleepTime: bpy.props.FloatProperty(
        name="Pause Time",
        description="Pause between intervals in seconds. Needed to prevent crashes from starting next interval too early",
        default=3.0, min=0.0001)
    saveIntervals: bpy.props.BoolProperty(
        name="Save after Interval",
        description="Save blend file after each interval is completed",
        default=True)
    saveAfterBake: bpy.props.BoolProperty(
        name="Save after Bake",
        description="Save blend file after bake is completed",
        default=True)

    @classmethod
    def poll(cls, context):
        if not bpy.data.is_saved:
            cls.poll_message_set("File needs to be saved")
            return False
        if not context.active_object:
            return False
        if context.active_object.type == 'GPENCIL':
            return True

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        scene = bpy.context.scene

        scene.render.use_simplify = False

        initial_frame_start = scene.frame_start
        initial_frame_end = scene.frame_end
        bake_range = scene.frame_end - scene.frame_start

        print("")
        iterations = math.ceil(bake_range/self.intervalSize)

        for i in range(0, iterations):
            if i != 0:
                scene.frame_start += self.intervalSize

            if i == (iterations - 1):
                scene.frame_end = initial_frame_end
            else:
                scene.frame_end = scene.frame_start + self.intervalSize - 1
            print(f"Iteration {i}: {scene.frame_start} - {scene.frame_end}")
            bpy.ops.object.lineart_bake_strokes()
            print("Interval finished")
            print("Waiting for " + str(self.sleepTime) + " seconds...")
            time.sleep(self.sleepTime)
            if self.saveIntervals:
                bpy.ops.wm.save_mainfile()
                time.sleep(self.sleepTime)

        # reset start frame to original start frame from before starting increment loop
        scene.frame_start = initial_frame_start
        scene.render.use_simplify = True
        print("Bake completed")
        if self.saveAfterBake:
            bpy.ops.wm.save_mainfile()

        return {'FINISHED'}


def get_data_by_type_and_name(bpy_type: bpy.types.Collection | bpy.types.Material | bpy.types.ViewLayer,
                              key: str) -> bpy.types:
    index = 0
    if bpy_type.bl_rna.identifier == bpy.types.Collection.bl_rna.identifier:
        index = bpy.data.collections.find(key)
        if index != -1:
            return bpy.data.collections[index]
    elif bpy_type.bl_rna.identifier == bpy.types.Material.bl_rna.identifier:
        index = bpy.data.materials.find(key)
        if index != -1:
            return bpy.data.materials[index]
    elif bpy_type.bl_rna.identifier == bpy.types.ViewLayer.bl_rna.identifier:
        index = bpy.context.scene.view_layers.find(key)
        if index != -1:
            return bpy.context.scene.view_layers[index]
    else:
        return None


class FTB_OT_AddToInvertedHullOutline_Op(Operator):
    bl_idname = "object.add_ih_outline"
    bl_label = "FTB: Add Inverted Hull Outline"
    bl_description = "Adds selected objects to inverted hull outline setup. Only works on local objects"
    bl_options = {"REGISTER", "UNDO"}

    DRIVER_EXPRESSION = "is_inverted_hull_view_layer(depsgraph)"

    @ classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            cls.poll_message_set("Must be in Object Mode!")
            return False
        if not context.selected_objects:
            cls.poll_message_set("Select at least one object")
            return False
        return True

    def execute(self, context):
        from ..ftb_prefs import FTBPreferences
        prefernces: FTBPreferences = getFritziPreferences()

        # check for inverted Hull view layer and get reference to it
        initial_view_layer: ViewLayer = context.view_layer
        inverted_hull_viewlayer: ViewLayer = get_data_by_type_and_name(ViewLayer, IH_VIEWLAYER_NAME)

        # if it does not exist, create it and get reference
        if not inverted_hull_viewlayer:
            try:
                bpy.ops.scene.view_layer_add(type='COPY')
                inverted_hull_viewlayer = context.view_layer
                inverted_hull_viewlayer.name = IH_VIEWLAYER_NAME
                context.window.view_layer = initial_view_layer
            except:
                log.report(self, log.Severity.ERROR, "View Layer creation failed! Task aborted.")
                return {'CANCELLED'}

        # check if inverted hull AOV exists and get a reference
        lf_index = inverted_hull_viewlayer.aovs.find(IH_AOV_NAME)
        ih_aov: AOV = None
        if lf_index != -1:
            ih_aov = inverted_hull_viewlayer.aovs[lf_index]

        # if AOV does not exist, create it
        if not ih_aov:
            ih_aov = inverted_hull_viewlayer.aovs.add()
            ih_aov.type = 'VALUE'
            ih_aov.name = IH_AOV_NAME

        # check for existing inverted hull collection
        inverted_hull_collection: Collection = get_data_by_type_and_name(Collection, IH_OBJECTS_COLLECTION_NAME)

        # if inverted hull collection does not exist, create it
        if not inverted_hull_collection:
            try:
                inverted_hull_collection = bpy.data.collections.new(name=IH_OBJECTS_COLLECTION_NAME)
                context.scene.collection.children.link(inverted_hull_collection)
            except:
                log.report(self, log.Severity.ERROR, "Inverted Hull Collection creation failed! Task aborted.")
                return {'CANCELLED'}

        ih_outline_material: Material = get_data_by_type_and_name(Material, IH_MATERIAL_NAME)

        # generate new material with aov pass
        if not ih_outline_material:
            try:
                ih_outline_material = bpy.data.materials.new(name=IH_MATERIAL_NAME)

                ih_outline_material.use_nodes = True
                ih_outline_material.use_backface_culling = True
                ih_outline_material.shadow_method = 'NONE'
                ih_outline_material.diffuse_color = prefernces.ih_material_diffuse_color
                ih_outline_material.roughness = prefernces.ih_material_roughness
                ih_outline_material.metallic = prefernces.ih_material_metallic

                _nodes = ih_outline_material.node_tree.nodes
                _nodes.remove(_nodes.get('Principled BSDF'))

                _aov_node = _nodes.new('ShaderNodeOutputAOV')
                _aov_node.name = IH_AOV_NAME
                _aov_node.inputs[1].default_value = 1.0
                _aov_node.location = (300, 140)
                _aov_node.width = 200

                _emission_node = _nodes.new(type='ShaderNodeEmission')
                _emission_node.inputs[0].default_value = (0, 0, 0, 1)
                _emission_node.location = (20, 280)

                _mat_output_node: bpy.types.ShaderNode = _nodes.get('Material Output')

                _links = ih_outline_material.node_tree.links

                _links.new(_mat_output_node.inputs[0], _emission_node.outputs[0])
            except:
                log.report(self, log.Severity.ERROR, "Inverted Hull Material creation failed! Task aborted.")
                return {'CANCELLED'}

        object_counts = {"successful": 0, "incompatible": 0}
        for object in context.selected_objects:
            if object.type not in ('MESH', 'FONT', 'CURVE', 'SURFACE') or object.library or object.override_library:
                object_counts["incompatible"] += 1
                continue

            # check if object is already linked to inverted hull collection
            object_is_not_linked = True
            for collection in object.users_collection:
                if collection != inverted_hull_collection:
                    continue
                object_is_not_linked = False
                break

            if object_is_not_linked:
                inverted_hull_collection.objects.link(object)

            # add additional material id
            outline_material_missing = (object.material_slots.find(IH_MATERIAL_NAME) == -1)
            if outline_material_missing:
                object.data.materials.append(ih_outline_material)

            # check if solidify modifier already exists, otherwise create it
            lf_index = object.modifiers.find(IH_MODIFIER_NAME)
            ih_modifier: SolidifyModifier = None
            if lf_index != -1:
                ih_modifier = object.modifiers[lf_index]
                if ih_modifier.type != 'SOLIDIFY':
                    ih_modifier = None

            if not ih_modifier:
                try:
                    ih_modifier = object.modifiers.new(name=IH_MODIFIER_NAME, type='SOLIDIFY')

                    # set thickness based on object scale to achieve similiar thickness for scaled objects
                    scale_average = sum(abs(n) for n in object.scale) / len(object.scale)
                    ih_modifier.thickness = prefernces.ih_modifier_thickness / scale_average

                    ih_modifier.offset = prefernces.ih_modifier_offset
                    ih_modifier.use_even_offset = prefernces.ih_modifier_even_thickness
                    ih_modifier.use_quality_normals = prefernces.ih_modifier_use_quality_normals
                    ih_modifier.thickness_clamp = prefernces.ih_modifier_thickness_clamp
                    ih_modifier.use_rim = prefernces.ih_modifier_use_rim
                    ih_modifier.use_rim_only = prefernces.ih_modifier_use_rim_only

                    ih_modifier.use_flip_normals = True

                    _mat_offset = len(object.material_slots)-1
                    ih_modifier.material_offset = _mat_offset
                    ih_modifier.material_offset_rim = _mat_offset

                    for d_path in DRIVER_PATHS:
                        _d = ih_modifier.driver_add(d_path)
                        _d.driver.expression = self.DRIVER_EXPRESSION
                except:
                    lf_index = object.material_slots.find(IH_MATERIAL_NAME)
                    object.data.materials.pop(index=lf_index)

                    inverted_hull_collection.objects.unlink(object)
                    message = f"Could not create Solidify Modifier for object: {object.name}. "
                    if object_counts["successful"] > 0:
                        message += f"Objects successfully processed: {object_counts['successful']}"
                    log.report(self, log.Severity.ERROR, message)
                    return {'CANCELLED'}

            object_counts["successful"] += 1

        message = (f"IH-Outline Setup successfully performed for {object_counts['successful']} "
                   f"{('object', 'objects')[object_counts['successful'] > 1]}.")
        incompatible_objects_processed = object_counts["incompatible"] > 0
        if incompatible_objects_processed:
            lf_index = message.find(str(object_counts["successful"])) + 1
            message = f"{message[:lf_index]} out of {len(context.selected_objects)}{message[lf_index:]}"
            message += (f" {object_counts['incompatible']} "
                        f"{('object was', 'objects were')[object_counts['incompatible'] > 1]}"
                        f" incompatible!")

        # bpy.ops.scene.ih_view_layer_setup()
        log.report(self, (log.Severity.INFO, log.Severity.WARNING)[incompatible_objects_processed], message)
        return {'FINISHED'}


class FTB_OT_RemoveFromInvertedHullOutline_Op(Operator):
    bl_idname = "object.remove_ih_outline"
    bl_label = "FTB: Remove Inverted Hull Outline"
    bl_description = "Removes selected objects from inverted hull outline setup"
    bl_options = {"REGISTER", "UNDO"}

    @ classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            cls.poll_message_set("Must be in Object Mode!")
            return False
        if not context.selected_objects:
            cls.poll_message_set("Select at least one object")
            return False
        return True

    def remove_ih_viewlayer_aov(self, context):
        ih_viewlayer: ViewLayer = get_data_by_type_and_name(ViewLayer, IH_VIEWLAYER_NAME)
        if ih_viewlayer:
            lf_index = ih_viewlayer.aovs.find(IH_AOV_NAME)
            if lf_index != -1:
                ih_viewlayer.active_aov_index = lf_index
                bpy.ops.scene.view_layer_remove_aov()
            context.scene.view_layers.remove(ih_viewlayer)

    def execute(self, context):
        inverted_hull_collection: Collection = get_data_by_type_and_name(Collection, IH_OBJECTS_COLLECTION_NAME)

        if not inverted_hull_collection:
            self.remove_ih_viewlayer_aov(context)
            message = "Could not find inverted hull collection. Removing IH-Viewlayer and AOV."
            log.report(self, log.Severity.INFO, message)
            return {'FINISHED'}

        object_counts = {"successful": 0, "incompatible": 0}
        for object in context.selected_objects:
            # remove object from IH_collection
            object_is_linked_to_collection = False
            for collection in object.users_collection:
                if collection != inverted_hull_collection:
                    continue
                object_is_linked_to_collection = True
                break

            if object_is_linked_to_collection:
                inverted_hull_collection.objects.unlink(object)

            if object.type not in ('MESH', 'FONT', 'CURVE', 'SURFACE'):
                object_counts["incompatible"] += 1
                continue

            # remove IH_drivers and solidify modifier
            lf_index = object.modifiers.find(IH_MODIFIER_NAME)
            if lf_index != -1:
                ih_modifier = object.modifiers[lf_index]
                for d_path in DRIVER_PATHS:
                    ih_modifier.driver_remove(d_path)
                object.modifiers.remove(ih_modifier)

            # if the mesh is not a linked duplicate, remove IH material slot, otherwise keep it
            if object.data.users <= 1:
                # remove ih_outline material + slot
                lf_index = object.material_slots.find(IH_MATERIAL_NAME)
                if lf_index != -1:
                    object.data.materials.pop(index=lf_index)
                object_counts["successful"] += 1

        # if there is no object left in IH_collection remove IH related collection, aov pass, material and viewlayer
        message = (f"Removed {object_counts['successful']} {('object', 'objects')[object_counts['successful'] > 1]}"
                   f" from IH-Setup.")
        incompatible_objects_processed = object_counts['incompatible'] > 0
        if incompatible_objects_processed:
            message += (f" {object_counts['incompatible']} incompatible "
                        f"{('object', 'objects')[object_counts['incompatible'] > 1]}"
                        f" unlinked from inverted hull collection.")

        if len(inverted_hull_collection.objects) > 0:
            log.report(self, log.Severity.INFO, message)
            return {'FINISHED'}

        self.remove_ih_viewlayer_aov(context)
        bpy.data.collections.remove(inverted_hull_collection)
        message += " No items left in collection. Removing IH-Viewlayer and AOV."
        log.report(self, log.Severity.INFO, message)
        return {'FINISHED'}


class FTB_OT_InvertedHullViewLayerSetup(Operator):
    bl_idname = "scene.ih_view_layer_setup"
    bl_label = "IH Viewlayer Finalisation"
    bl_description = ("Excludes Inverted Hull collection on all viewlayers other than the Inverted Hull Viewlayer and "
                      "configures the IH-Viewlayer with appropriate settings for final rendering")
    bl_options = {"REGISTER", "UNDO"}

    @ classmethod
    def poll(cls, context):
        if not get_data_by_type_and_name(ViewLayer, IH_VIEWLAYER_NAME):
            cls.poll_message_set("Inverted Hull Viewlayer not found!")
            return False
        return True

    def execute(self, context):

        def set_exclude(exclude: bool, collection: bpy.types.LayerCollection):
            collection.exclude = exclude
            if collection.children:
                for child in collection.children:
                    set_exclude(exclude, child)

        def copy_layercollection_settings(source: bpy.types.LayerCollection, target: bpy.types.LayerCollection):
            target.exclude = source.exclude
            target.collection.hide_select = source.collection.hide_select
            target.hide_viewport = source.hide_viewport
            target.holdout = source.holdout
            target.indirect_only = source.indirect_only

            if source.children:
                for childsource, childtarget in zip(source.children, target.children):
                    copy_layercollection_settings(childsource, childtarget)

        def copy_viewlayer_settings(source: ViewLayer, target: ViewLayer):
            for colsource, coltarget in zip(source.layer_collection.children, target.layer_collection.children):
                copy_layercollection_settings(colsource, coltarget)

        lf_index = context.view_layer.layer_collection.children.find(IH_OBJECTS_COLLECTION_NAME)
        viewlayer_3d = get_data_by_type_and_name(ViewLayer, "3d")
        ih_viewlayer = get_data_by_type_and_name(ViewLayer, IH_VIEWLAYER_NAME)
        if lf_index == -1:
            log.report(self, log.Severity.ERROR, "Could not find Inverted Hull Collection")
            return {'CANCELLED'}
        if not viewlayer_3d:
            log.report(self, log.Severity.ERROR, "Could not find viewlayer with name \"3d\"")
            return {'CANCELLED'}
        if not ih_viewlayer:
            log.report(self, log.Severity.ERROR, "Could not find Inverted-Hull Viewlayer")
            return {'CANCELLED'}

        copy_viewlayer_settings(viewlayer_3d, ih_viewlayer)

        # exclude ih collection from all other viewlayers
        for viewlayer in context.scene.view_layers:
            if viewlayer.name != IH_VIEWLAYER_NAME:
                viewlayer.layer_collection.children[lf_index].exclude = True
                continue
        # exclude outline collections in ih viewlayer
        for child in viewlayer.layer_collection.children:
            if child.name in ("OUTLINES", "OUTLINE_groups"):
                set_exclude(True, child)

        viewlayer.layer_collection.children[lf_index].exclude = False

        return {'FINISHED'}


class FTB_OT_AdjustInvertedHullThickness(Operator):
    bl_idname = "object.adjust_ih_thickness"
    bl_label = "FTB: Adjust IH-Thickness"
    bl_description = "Adjust the inverted hull thickness for selected objects"
    bl_options = {"REGISTER", "UNDO"}

    thickness: bpy.props.FloatProperty(name="IH-Thickness",
                                       description="New thickness value for the IH-modifier",
                                       default=0.0018,
                                       precision=4,
                                       min=0.0001,
                                       max=20.0)

    apply_scale: bpy.props.BoolProperty(name="Apply Thickness Scale",
                                        description="Sets the inverted hull thickness for selected objects based on " +
                                        "their scale to achieve a similiar thickness value",
                                        default=True)

    @ classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            cls.poll_message_set("Must be in Object Mode")
            return False
        if len(context.selected_objects) < 1:
            cls.poll_message_set("Select at least one object")
            return False
        return True

    def execute(self, context):

        for object in context.selected_objects:
            for modifier in object.modifiers:
                if modifier.type != 'SOLIDIFY':
                    continue
                if modifier.name != IH_MODIFIER_NAME:
                    continue
                scale_average = sum(abs(n) for n in object.scale) / len(object.scale)
                modifier.thickness = self.thickness / (1, scale_average)[self.apply_scale]

        return {'FINISHED'}


class FTB_OT_AddObjectToTransparentAOV_Op(Operator):
    bl_idname = "object.add_transparent_aov"
    bl_label = "FTB: Add Transparent AOV"
    bl_description = (f"Adds selected objects to collection called \"{AOV_COLLECTION_NAME}\" and creates corresponding"
                      " AOV pass if it doesn't exist")
    bl_options = {"REGISTER", "UNDO"}

    outlinegroups_collection_name = "OUTLINE_groups"

    @ classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            cls.poll_message_set("Must be in Object Mode!")
            return False
        if not context.selected_objects:
            cls.poll_message_set("Select at least one object")
            return False
        if cls.outlinegroups_collection_name not in bpy.data.collections:
            cls.poll_message_set(f"\"{cls.outlinegroups_collection_name}\" collection not found!")
            return False
        return True

    def execute(self, context):

        def set_aov_pass_settings(aov_pass: AOV):
            aov_pass.type = 'VALUE'
            aov_pass.name = AOV_PASS_NAME

        outline_groups_collection: Collection = bpy.data.collections[self.outlinegroups_collection_name]
        aov_collection: Collection = get_data_by_type_and_name(Collection, AOV_COLLECTION_NAME)
        default_3d_viewlayer: ViewLayer = get_data_by_type_and_name(ViewLayer, "3d")

        if not default_3d_viewlayer:
            log.report(self, log.Severity.ERROR, "Could not find default \"3d\" viewlayer!")
            return {'CANCELLED'}

        if not aov_collection:
            aov_collection = bpy.data.collections.new(AOV_COLLECTION_NAME)
            outline_groups_collection.children.link(aov_collection)

        aov_collection.lineart_usage = 'EXCLUDE'
        aov_collection.hide_render = True

        for viewlayer in context.scene.view_layers:
            outline_groups_layer_collection = viewlayer.layer_collection.children[self.outlinegroups_collection_name]
            aov_layer_collection = outline_groups_layer_collection.children[AOV_COLLECTION_NAME]
            if "3d" in viewlayer.name:
                aov_layer_collection.exclude = False
            else:
                aov_layer_collection.exclude = True

        aov_pass: AOV = None
        if AOV_PASS_NAME not in default_3d_viewlayer.aovs:
            aov_pass = default_3d_viewlayer.aovs.add()
            set_aov_pass_settings(aov_pass)
        aov_pass = default_3d_viewlayer.aovs[AOV_PASS_NAME]
        set_aov_pass_settings(aov_pass)

        for object in context.selected_objects:
            if object.type not in ('MESH', 'FONT', 'CURVE', 'SURFACE'):
                continue

            if object.name not in aov_collection.all_objects:
                aov_collection.objects.link(object)

            # unlink object from other Outline group collections
            collection: Collection
            for collection in outline_groups_collection.children_recursive:
                if collection is aov_collection:
                    continue

                if collection.user_of_id(object):
                    collection.objects.unlink(object)

        if len(aov_collection.all_objects) < 1:
            bpy.ops.object.remove_transparent_aov()

        log.report(self, log.Severity.INFO, f"Selected objects added to \"{AOV_COLLECTION_NAME}\" collection")
        return {'FINISHED'}


class FTB_OT_RemoveObjectFromTransparentAOV_Op(Operator):
    bl_idname = "object.remove_transparent_aov"
    bl_label = "FTB: Remove Transparent AOV"
    bl_description = (f"Removes selected objects from \"{AOV_COLLECTION_NAME}\" collection and removes collection and "
                      "corresponding AOV pass if the collection is empty")
    bl_options = {"REGISTER", "UNDO"}

    @ classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            cls.poll_message_set("Must be in Object Mode!")
            return False
        if not context.selected_objects:
            cls.poll_message_set("Select at least one object")
            return False
        if AOV_COLLECTION_NAME not in bpy.data.collections:
            cls.poll_message_set(f"\"{AOV_COLLECTION_NAME}\" collection not found!")
            return False
        return True

    def execute(self, context):
        aov_collection: Collection = bpy.data.collections[AOV_COLLECTION_NAME]
        for object in context.selected_objects:
            if object.name not in aov_collection.objects:
                continue

            aov_collection.objects.unlink(object)

        message = f"Selected objects removed from \"{AOV_COLLECTION_NAME}\" collection"
        if len(aov_collection.all_objects) > 0:
            log.report(self, log.Severity.INFO, message)
            return {'FINISHED'}

        default_3d_viewlayer: ViewLayer = get_data_by_type_and_name(ViewLayer, "3d")

        if default_3d_viewlayer:
            if AOV_PASS_NAME in default_3d_viewlayer.aovs:
                lf_index = default_3d_viewlayer.aovs.find(AOV_PASS_NAME)
                default_3d_viewlayer.active_aov_index = lf_index
                bpy.ops.scene.view_layer_remove_aov()

        bpy.data.collections.remove(aov_collection)

        message = (f"All objects removed from \"{AOV_COLLECTION_NAME}\" collection."
                   "Removing AOV Pass and collection itself.")
        log.report(self, log.Severity.INFO, message)
        return {'FINISHED'}


class FTB_OT_OutlineCharacterSetup(Operator):
    bl_idname = "collection.outline_character_setup"
    bl_label = "FTB: Character Outline Setup"
    bl_description = ("Loops over all objects inside the active collection and tries to sort them into the"
                      " corresponding outline groups")
    bl_options = {'REGISTER', 'UNDO'}

    collection_error: bool = False

    @ classmethod
    def poll(cls, context):
        if context.area.type != 'OUTLINER':
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        layout = self.layout
        if self.collection_error and not context.scene.outline_target_collection:
            layout.alert = True
            layout.label(text="Pick a valid Target Collection")
            layout.alert = False
        layout.prop(context.scene, "outline_target_collection")
        if self.collection_error and not context.scene.outline_mouth_collection:
            layout.alert = True
            layout.label(text="Pick a valid Mouth Collection")
            layout.alert = False
        layout.prop(context.scene, "outline_mouth_collection")

    def execute(self, context):
        L0_target_collection: Collection = context.scene.outline_target_collection
        L2_mouth_collection: Collection = context.scene.outline_mouth_collection
        if not L0_target_collection:
            self.collection_error = True
            return context.window_manager.invoke_props_dialog(self, width=500)
        if not L2_mouth_collection:
            self.collection_error = True
            return context.window_manager.invoke_props_dialog(self, width=500)

        self.collection_error = False
        L1_target_collection: Collection = get_data_by_type_and_name(Collection, L0_target_collection.name[:-2]+"L1")
        L2_target_collection: Collection = get_data_by_type_and_name(Collection, L0_target_collection.name[:-2]+"L2")

        no_intersection_collection: Collection = get_data_by_type_and_name(Collection, "OBJECTS_NoIntersection")
        force_intersection_collection: Collection = get_data_by_type_and_name(Collection, "OBJECTS_ForceIntersection")
        extra_objects_collection: Collection = get_data_by_type_and_name(Collection, "EXTRA_CharacterObjects")
        exclude_collection: Collection = get_data_by_type_and_name(Collection, "OBJECTS_Excluded")

        if not (L1_target_collection and L2_target_collection):
            log.report(self, log.Severity.ERROR,
                       f"Could not find L1 or L2 group of \"{L0_target_collection.name}\" collection.  Aborting...")
            return {'CANCELLED'}

        if not (no_intersection_collection and force_intersection_collection and extra_objects_collection
                and exclude_collection):
            log.report(self, log.Severity.ERROR, "Could not find Outline Groups Setup. Aborting...")
            return {'CANCELLED'}

        outline_log_name = "00_outline_sorting_log"
        if outline_log_name not in bpy.data.texts:
            bpy.data.texts.new(outline_log_name)
        outline_sorting_log: Text = bpy.data.texts[outline_log_name]

        def link_object_to_collection(collection: Collection, object: Object):
            if collection.all_objects.find(object.name) != -1:
                outline_sorting_log.write(
                    f"\n\t#Object \"{object.name}\" ignored -> already linked to collection \"{collection.name}\"")
                return
            collection.objects.link(object)
            outline_sorting_log.write(f"\n\tObject \"{object.name}\" linked to collection \"{collection.name}\"")

        collection_name = context.collection.name.lower()

        first_logline = "\n\nStarting sorting process for objects in collection".upper()
        outline_sorting_log.write(f"{first_logline} \"{context.collection.name}\"")
        for object in context.collection.all_objects:
            object_name = object.name.lower()

            if object.type not in ('MESH', 'CURVE'):
                outline_sorting_log.write(
                    f"\n\t#Object \"{object.name}\" ignored -> Object is of type {object.type}. Type MESH CURVE required")
                continue

            # ignore hidden objects except for eye_close
            if not object.visible_get() and "eye_close" not in object.name:
                outline_sorting_log.write(
                    f"\n\t#Object \"{object.name}\" ignored -> Object is not visible in viewport")
                continue

            if any(e in object_name for e in ("glasses_inner", "sputnik_eye_white", "eyes_geo_l", "eyes_geo_r",
                                              "glassesglas", "glasses_geo.003_inner", "glasses_geo.004_inner")):
                link_object_to_collection(exclude_collection, object)
                continue
            elif any(e in object_name for e in ("eye_", "mustache", "necklace", "earring")):
                link_object_to_collection(L1_target_collection, object)
                if "earring" in object_name:
                    link_object_to_collection(force_intersection_collection, object)
                continue
            elif any(e in object_name for e in ("eyeline", "cheekline", "eyebagline", "faceline", "mouth", "toungue")):
                eyeline_exceptions = ("demonstrant02", "c315", "c290", "c301", "c302", "c303", "crowd")
                if "mouth" in object_name and "stasibrille" in collection_name:
                    link_object_to_collection(L1_target_collection, object)
                    continue
                elif "eyeline" in object_name and any(e in collection_name for e in eyeline_exceptions):
                    link_object_to_collection(extra_objects_collection, object)
                    continue

                link_object_to_collection(L2_target_collection, object)
                continue
            elif any(e in object_name for e in ("teeth", "tongue", "tounge")):
                link_object_to_collection(L2_mouth_collection, object)
                continue
            elif any(e in object_name for e in ("beard", "earline", "eyebrow", "eyelash", "nostril", "dot", "eyes_geo",
                                                "freckles")):
                if "beard" in object_name:
                    if any(e in collection_name for e in ("demonstrant01", "c333", "kameramann", "westextramann03")):
                        link_object_to_collection(L1_target_collection, object)
                        continue
                elif "eyebrow" in object_name:
                    eyebrow_exceptions = (
                        "klaus", "rothkirch", "kameramann", "agitator", "ecki", "harry", "lauer", "c290", "c297",
                        "demonstrant01", "c332",  "westextramann04", "westextramann05")
                    if any(e in collection_name for e in eyebrow_exceptions):
                        link_object_to_collection(L1_target_collection, object)
                        continue
                elif "eyelash" in object_name and "julia" in collection_name:
                    link_object_to_collection(L2_target_collection, object)
                    continue

                link_object_to_collection(extra_objects_collection, object)
                continue
            else:
                if "glasses" in object_name and any(e in collection_name for e in ("c332", "c333")):
                    link_object_to_collection(extra_objects_collection, object)
                    continue

                link_object_to_collection(L0_target_collection, object)
                if any(e in object_name for e in ("clip", "hair", "nosepiercing", "hat")):
                    link_object_to_collection(force_intersection_collection, object)
                    continue
                elif "zwilling" in collection_name and "sphere" in object_name:
                    link_object_to_collection(force_intersection_collection, object)
                    continue
                elif any(e in object_name for e in ("ear", "nose")):
                    if "nose" in object_name and "sputnik" in collection_name:
                        continue
                    link_object_to_collection(no_intersection_collection, object)

        report_msg = f"Sorting objects from collection \"{context.collection.name}\" into Outline Groups finished!"
        outline_sorting_log.write(f"\n{report_msg}")
        outline_sorting_log.write(f"\n{''.join('_' for i in range(0,120))}")
        log.report(self, log.Severity.INFO, report_msg)
        return {'FINISHED'}


class FTB_OT_AddTransparentAOVNode_Op(Operator):
    bl_idname = "node.add_transparent_aov"
    bl_label = "FTB: Add Transparent AOV Node"
    bl_description = "Adds a custom AOV Output node required for the Fritzi compositing setup"
    bl_options = {"REGISTER", "UNDO"}

    x: float = 0
    y: float = 0

    @ classmethod
    def poll(cls, context):
        if context.space_data.tree_type != "ShaderNodeTree":
            cls.poll_message_set("Can only be called from within Shader Node Editor!")
            return False
        if not context.active_object.active_material:
            cls.poll_message_set("No active material selected!")
            return False

        return True

    def invoke(self, context, event):
        region = context.region.view2d
        uiscale = context.preferences.system.ui_scale
        x, y = region.region_to_view(event.mouse_region_x, event.mouse_region_y)
        self.x = x/uiscale
        self.y = y/uiscale
        return self.execute(context)

    def execute(self, context):
        active_mat_tree = context.active_object.active_material.node_tree

        for node in active_mat_tree.nodes:
            if node.type != 'OUTPUT_AOV':
                continue

            if node.name == AOV_PASS_NAME:
                log.report(self, log.Severity.WARNING, "Transparent AOV Output node already exists.")
                return {'CANCELLED'}

        aov_node = active_mat_tree.nodes.new('ShaderNodeOutputAOV')
        aov_node.name = AOV_PASS_NAME
        aov_node.inputs[0].default_value = (1, 1, 1, 1)
        aov_node.inputs[1].default_value = 1.0

        aov_node.use_custom_color = True
        aov_node.color = (0, 0, 0.6)
        aov_node.location = (self.x, self.y)
        aov_node.width = 200

        log.report(self, log.Severity.INFO, "Transparent AOV Output node created.")
        return {'FINISHED'}


classes = (FTB_OT_DefaultAddLineart_Op, FTB_OT_Copy_Optimize_Lines_Op, FTB_OT_Bake_Interval_Op,
           FTB_OT_AddToInvertedHullOutline_Op, FTB_OT_RemoveFromInvertedHullOutline_Op,
           FTB_OT_InvertedHullViewLayerSetup, FTB_OT_AdjustInvertedHullThickness, FTB_OT_OutlineCharacterSetup,
           FTB_OT_AddObjectToTransparentAOV_Op, FTB_OT_RemoveObjectFromTransparentAOV_Op,
           FTB_OT_AddTransparentAOVNode_Op)


@ persistent
def register_inverted_hull_driver_expression(self, context) -> None:
    def is_inverted_hull_view_layer(depsgraph: bpy.types.Depsgraph) -> bool:
        return IH_VIEWLAYER_NAME in depsgraph.view_layer.name
    bpy.app.driver_namespace[is_inverted_hull_view_layer.__name__] = is_inverted_hull_view_layer


def target_collection_poll(self, object) -> bool:
    char_outline_collection: Collection = get_data_by_type_and_name(Collection, "CHARACTERS")
    if not char_outline_collection:
        return False

    return char_outline_collection.user_of_id(object) and "_L0" in object.name


def mouth_collection_poll(self, object) -> bool:
    char_outline_collection: Collection = get_data_by_type_and_name(Collection, "CHARACTERS")
    if not char_outline_collection:
        return False

    return char_outline_collection.user_of_id(object)


def register():
    for c in classes:
        bpy.utils.register_class(c)
    bpy.app.handlers.load_post.append(register_inverted_hull_driver_expression)

    bpy.types.Scene.outline_target_collection = bpy.props.PointerProperty(
        type=bpy.types.Collection,
        name="Target Collection",
        description=("Pick an outline L0 collection for the character objects to be sorted into. "
                     "The operator will try to locate L1 and L2 groups on its own"),
        options={'SKIP_SAVE'},
        poll=target_collection_poll)

    bpy.types.Scene.outline_mouth_collection = bpy.props.PointerProperty(
        type=bpy.types.Collection,
        name="Mouth Collection",
        description="Pick collection for all outline mouth objects. Usually an L2 Outline Group.",
        options={'SKIP_SAVE'},
        poll=mouth_collection_poll)


def unregister():
    del bpy.types.Scene.outline_target_collection
    del bpy.types.Scene.outline_mouth_collection
    bpy.app.handlers.load_post.remove(register_inverted_hull_driver_expression)
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
