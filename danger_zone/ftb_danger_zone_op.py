import numpy as np

import bpy

from bpy.types import Operator, Image, Material, FloatColorAttribute, ShaderNode, ShaderNodeTree
from .. utility_functions import ftb_logging as log
from ..utility_functions.ftb_string_utils import is_name_duplicate, strip_End_Numbers
from ..utility_functions.ftb_transform_utils import apply_bone_world_matrix


def is_image_duplicate(source: Image, duplicate: Image):
    # perform naive image comparison to avoid unnecessary pixel by pixel comparisons
    equal_size = source.size[0] == duplicate.size[0] and \
        source.size[1] == duplicate.size[1]
    equal_depth = source.depth == duplicate.depth

    if not (equal_size and equal_depth):
        return False

    # if naive comparison is passed perform in depth pixel by pixel check on thumbnails to save on iterations
    if source.preview and duplicate.preview:
        source_pixels = np.array(source.preview.icon_pixels)
        duplicate_pixels = np.array(duplicate.preview.icon_pixels)
    else:
        source_pixels = np.array(source.pixels)
        duplicate_pixels = np.array(duplicate.pixels)

    return np.array_equal(source_pixels, duplicate_pixels)


def has_equal_color(color_a: FloatColorAttribute, color_b: FloatColorAttribute):
    is_equal: bool = True
    for i in range(len(color_a)):
        is_equal &= (color_a[i] == color_b[i])
    return is_equal


def is_equal_node(node_a: ShaderNode, node_b: ShaderNode):
    return node_a.type == node_b.type and node_a.name == node_b.name


def is_material_duplicate(source: Material, duplicate: Material) -> bool:

    if not has_equal_color(source.diffuse_color, duplicate.diffuse_color):
        return False

    source_nodes = None
    duplicate_nodes = None
    if source.node_tree:
        source_nodes = sorted(source.node_tree.nodes, key=lambda node: node.name)
    if duplicate.node_tree:
        duplicate_nodes = sorted(duplicate.node_tree.nodes, key=lambda node: node.name)

    identical_node_tree = (source_nodes == duplicate_nodes)
    if source_nodes and duplicate_nodes:
        if len(source_nodes) != len(duplicate_nodes):
            return False

        identical_node_tree = True
        for i in range(len(source_nodes)):
            identical_node_tree &= is_equal_node(source_nodes[i], duplicate_nodes[i])

    source_pixels = np.array(list())
    duplicate_pixels = np.array(list())
    if source.preview and duplicate.preview:
        # using material thumbnail comparison to further validate a duplicate match
        # not ideal but better than looping over every input, on every node in the node_tree for all materials...
        # recently changed materials won't update their thumbnail immediately. This obviously affects the
        # outcome of the script
        source_pixels = np.array(source.preview.icon_pixels)
        duplicate_pixels = np.array(duplicate.preview.icon_pixels)

    return identical_node_tree and np.array_equal(source_pixels, duplicate_pixels)


def is_linked(object) -> bool:
    return object.library is not None  # or object.override_library != None


def get_duplicates_of_image(source_image: Image):

    images = bpy.data.images
    duplicates: bpy.types.Image = list()

    for current_image in images:
        # skip checking self and linked images
        if current_image == source_image or is_linked(current_image) or current_image.users <= 0:
            continue

        if is_name_duplicate(source_image.name_full, current_image.name_full):
            if is_image_duplicate(source_image, current_image):
                duplicates.append(current_image)

    return duplicates


def get_duplicates_of_material(source_mat: Material):
    materials = bpy.data.materials
    duplicates: bpy.types.Material = list()

    for current_mat in materials:
        # skip checking self and linked materials
        if current_mat == source_mat or is_linked(current_mat) or current_mat.users <= 0:
            continue

        if is_name_duplicate(source_mat.name_full, current_mat.name_full):
            if is_material_duplicate(source_mat, current_mat):
                duplicates.append(current_mat)

    return duplicates


class FTB_OT_RemoveMaterials_Op(Operator):
    bl_idname = "object.remove_all_materials"
    bl_label = "Remove All Materials"
    bl_description = "Remove all Material slots from all selected Objects"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        for m in bpy.data.materials:
            bpy.data.materials.remove(m)

        self.report({'INFO'}, 'Removed all Materials')
        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_RemoveModifiers_Op(Operator):
    bl_idname = "object.remove_modifers"
    bl_label = "Remove Modifiers"
    bl_description = "Remove all Modifiers from all selected objects"
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):
        for obj in bpy.context.selected_objects:
            for mod in obj.modifiers:
                obj.modifiers.remove(mod)
        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_EditShaderProperty_Op(Operator):
    bl_idname = "material.edit_shader_prop"
    bl_label = "Edit Shader Property"
    bl_description = "Sets selected shader property to selected value for all materials within scope."
    bl_options = {"REGISTER", "UNDO"}

    def setShaderProperty(self, materialObject):

        wm = bpy.context.window_manager

        # temporary list of already edited materials, in case some materials are looped over multiple times
        editedMatList = list()

        for matSlot in materialObject.material_slots:
            if matSlot.material is not None:
                if matSlot.material not in editedMatList:
                    editedMatList.append(matSlot.material)
                    if (matSlot.material.node_tree is not None):
                        for node in matSlot.material.node_tree.nodes:
                            if (type(node) == bpy.types.ShaderNodeGroup and node.node_tree is not None):
                                if (node.node_tree.name == wm.ftbShaderType.name):
                                    for dinput in node.inputs:
                                        if (dinput.identifier == wm.ftbShaderInput):

                                            if (dinput.type == 'RGBA'):

                                                if (wm.ftbShaderOperation == 'SET'):
                                                    dinput.default_value = wm.ftbShaderInputColor

                                                elif (wm.ftbShaderOperation == 'ADD'):
                                                    dinput.default_value[0] += wm.ftbShaderInputColor[0]
                                                    dinput.default_value[1] += wm.ftbShaderInputColor[1]
                                                    dinput.default_value[2] += wm.ftbShaderInputColor[2]
                                                    dinput.default_value[3] += wm.ftbShaderInputColor[3]

                                                elif (wm.ftbShaderOperation == 'MUL'):
                                                    dinput.default_value[0] *= wm.ftbShaderInputColor[0]
                                                    dinput.default_value[1] *= wm.ftbShaderInputColor[1]
                                                    dinput.default_value[2] *= wm.ftbShaderInputColor[2]
                                                    dinput.default_value[3] *= wm.ftbShaderInputColor[3]

                                            if dinput.type == ('VECTOR'):
                                                if (wm.ftbShaderOperation == 'SET'):
                                                    dinput.default_value = wm.ftbShaderInputVector

                                                elif (wm.ftbShaderOperation == 'ADD'):
                                                    dinput.default_value[0] += wm.ftbShaderInputVector[0]
                                                    dinput.default_value[1] += wm.ftbShaderInputVector[1]
                                                    dinput.default_value[2] += wm.ftbShaderInputVector[2]

                                                elif (wm.ftbShaderOperation == 'MUL'):
                                                    dinput.default_value[0] *= wm.ftbShaderInputVector[0]
                                                    dinput.default_value[1] *= wm.ftbShaderInputVector[1]
                                                    dinput.default_value[2] *= wm.ftbShaderInputVector[2]

                                            if dinput.type == ('VALUE'):
                                                if (wm.ftbShaderOperation == 'SET'):
                                                    dinput.default_value = wm.ftbShaderInputValue

                                                elif (wm.ftbShaderOperation == 'ADD'):
                                                    dinput.default_value += wm.ftbShaderInputValue

                                                elif (wm.ftbShaderOperation == 'MUL'):
                                                    dinput.default_value *= wm.ftbShaderInputValue

    def execute(self, context):

        wm = bpy.context.window_manager

        # Case limit = View Layer
        if (wm.editShaderScope == 'VIEW_LAYER'):
            if (not bpy.context.view_layer.objects):
                self.report(
                    {'ERROR'}, "No valid objects found in current view layer")
                return {'CANCELLED'}
            else:
                for obj in bpy.context.view_layer.objects:
                    self.setShaderProperty(obj)

                self.report(
                    {'INFO'}, "Shader property was changed for all materials in view layer.")

        # Case limit = Active Collection
        if (wm.editShaderScope == 'COLLECTION'):
            if (not bpy.context.collection):
                self.report({'ERROR'}, "No active collection")
                return {'CANCELLED'}

            else:
                for obj in bpy.context.collection.all_objects:
                    self.setShaderProperty(obj)

                self.report(
                    {'INFO'}, "Shader property was changed for all materials in active collection.")

        # Case limit = Current Selection
        if (wm.editShaderScope == 'SELECTION'):
            if (not bpy.context.selected_objects):
                self.report({'ERROR'}, "No objects selected")

            else:
                for obj in bpy.context.selected_objects:
                    self.setShaderProperty(obj)
                self.report(
                    {'INFO'}, "Shader property was changed for all materials in selection.")

        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


class FTB_OT_RemoveImageDuplicates_Op(Operator):
    bl_idname = "data.remove_image_duplicates"
    bl_label = "Remove Image Dupes"
    bl_description = ("Removes image duplicates from blend file (ignores linked images). Duplicates will be remapped, "
                      "setting users to zero. All duplicates will be deleted automatically when closing the file or "
                      "after performing manual clean up using File Menu")
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        images = bpy.data.images
        remap_count = 0
        last_duplicates_found: Image = list()

        for current_image in images:
            if current_image in last_duplicates_found:
                continue

            duplicates: Image = get_duplicates_of_image(current_image)

            if duplicates:
                last_duplicates_found = duplicates
                current_image.name = strip_End_Numbers(current_image.name_full)
                for duplicate in duplicates:
                    duplicate.user_remap(current_image)
                    remap_count += 1
                    print("Remapping image \"" + duplicate.name_full +
                          "\" to \"" + current_image.name_full + "\"")

        self.report({'INFO'}, str(remap_count) + " image duplicates found and remapped." +
                    " Open the terminal for comprehensive list of remappings")

        return {'FINISHED'}


class FTB_OT_RemoveMaterialDuplicates_Op(Operator):
    bl_idname = "data.remove_material_duplicates"
    bl_label = "Remove Material Dupes"
    bl_description = ("Removes material duplicates from blend file (ignores linked materials). Duplicates will be "
                      "remapped, setting users to zero. All duplicates will be deleted when closing the file or "
                      "performing manual clean up using File Menu")
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        materials = bpy.data.materials
        remap_count = 0
        last_duplicates_found: Material = list()

        for current_mat in materials:
            if current_mat in last_duplicates_found:
                continue

            duplicates: Material = get_duplicates_of_material(current_mat)

            if duplicates:
                last_duplicates_found = duplicates
                current_mat.name = strip_End_Numbers(current_mat.name_full)
                for duplicate in duplicates:
                    duplicate.user_remap(current_mat)
                    remap_count += 1
                    print("Remapping material \"" + duplicate.name_full +
                          "\" to \"" + current_mat.name_full + "\"")

        self.report({'INFO'}, str(remap_count) + " material duplicates found and remapped." +
                    " Open the terminal for comprehensive list of remappings")

        return {'FINISHED'}


class FTB_OT_RemoveNodeGroupDuplicates_Op(Operator):
    bl_idname = "data.remove_nodegroup_duplicates"
    bl_label = "Remove Node Group Dupes"
    bl_description = ("Removes node group duplicates from blend file (ignores linked node groups). Duplicates will be "
                      "remapped, setting users to zero. All duplicates will be deleted when closing the file or "
                      "performing manual clean up using File Menu")
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        def is_nodegrp_duplicate(source: ShaderNodeTree, duplicate: ShaderNodeTree) -> bool:
            _result: bool = True

            _expr: list[bool] = [is_name_duplicate(source.name_full, duplicate.name_full),
                                 len(source.nodes) == len(duplicate.nodes),
                                 len(source.links) == len(duplicate.links),
                                 len(source.inputs) == len(duplicate.inputs),
                                 len(source.outputs) == len(duplicate.outputs),
                                 source.inputs.keys() == duplicate.inputs.keys(),
                                 source.outputs.keys() == duplicate.outputs.keys()
                                 ]

            for e in _expr:
                _result &= e

            return _result

        def get_nodegrp_duplicates(source_group: ShaderNodeTree) -> list[ShaderNodeTree]:

            node_groups = bpy.data.node_groups
            duplicates: list[ShaderNodeTree] = []

            for current_grp in node_groups:
                if current_grp == source_group or current_grp.library != None:
                    continue

                if is_nodegrp_duplicate(source_group, current_grp):
                    duplicates.append(current_grp)

            return duplicates

        # code to loop through grps and remove the dupes
        last_duplicates_found: list[ShaderNodeTree] = []
        remap_count = 0
        for current_grp in bpy.data.node_groups:
            if current_grp in last_duplicates_found or current_grp.name.startswith("NodeGroup"):
                continue

            duplicates: list[ShaderNodeTree] = get_nodegrp_duplicates(current_grp)

            if duplicates:
                last_duplicates_found.extend(duplicates)
                current_grp.name = strip_End_Numbers(current_grp.name_full)
                for dup in duplicates:
                    dup.user_remap(current_grp)
                    remap_count += 1
                    log.console(self, log.Severity.NONE, f"Remapping group {dup.name_full} to {current_grp.name_full}")
        log.console(self, log.Severity.NONE, "\033[96m \033[1m End of node group dupe removal \033[0m")
        log.report(self, log.Severity.INFO, f"{remap_count} node group duplicates found and remapped. "
                   "Open the terminal for comprehensive list of remappings")
        return {'FINISHED'}


class FTB_OT_Remove_Edge_Splits_Op(Operator):
    bl_idname = "object.remove_edge_splits"
    bl_label = "Remove Edge Splits"
    bl_description = "Removes all Edge Split modifiers in all objects in either selection or active collection"
    bl_options = {"REGISTER", "UNDO"}

    def removeEdgeSplit(self, obj):
        edgeSplits = list()
        for mod in obj.modifiers:
            if mod.type == 'EDGE_SPLIT':
                edgeSplits.append(mod)

        if edgeSplits:
            for item in edgeSplits:
                obj.modifiers.remove(item)

    def execute(self, context):
        wm = bpy.context.window_manager

        # Case limit = View Layer
        if (wm.ftbEdgeSplitScope == 'VIEW_LAYER'):
            if (not bpy.context.view_layer.objects):
                self.report(
                    {'ERROR'}, "No valid objects found in current view layer")
                return {'CANCELLED'}
            else:
                for obj in bpy.context.view_layer.objects:
                    self.removeEdgeSplit(obj)

                self.report(
                    {'INFO'}, "Edge splits removed for all objects in view layer.")

        # Case limit = Active Collection
        if (wm.ftbEdgeSplitScope == 'COLLECTION'):
            if (not bpy.context.collection):
                self.report({'ERROR'}, "No active collection")
                return {'CANCELLED'}

            else:
                for obj in bpy.context.collection.all_objects:
                    self.removeEdgeSplit(obj)

                self.report(
                    {'INFO'}, "Edge splits removed for all objects in active collection.")

        # Case limit = Current Selection
        if (wm.ftbEdgeSplitScope == 'SELECTION'):
            if (not bpy.context.selected_objects):
                self.report({'ERROR'}, "No objects selected")

            else:
                for obj in bpy.context.selected_objects:
                    self.removeEdgeSplit(obj)
                self.report(
                    {'INFO'}, "Edge splits removed for all objects in selection.")
        return {'FINISHED'}


class FTB_OT_Remove_Empty_Libraries_Op(Operator):
    bl_idname = "data.remove_empty_libraries"
    bl_label = "Remove Empty Libraries"
    bl_description = "Removes all linked libraries without any referenced user IDs"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        counter = 0
        for lib in bpy.data.libraries:
            if len(lib.users_id) != 0:
                continue
            log.console(self, log.Severity.INFO, f"Removing library '{lib.name_full}'")
            bpy.data.libraries.remove(lib)
            counter += 1

        log.report(self, log.Severity.INFO, f"Removed {counter} empty {('library', 'libraries')[counter != 1]}.")
        return {'FINISHED'}


class FTB_OT_UpgradeCharacterAOVs_Op(Operator):
    bl_idname = "data.upgrade_character_aovs"
    bl_label = "Upgrade Character AOVs"
    bl_description = "Adds AOV Outputs to character material"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        nodeOffsetIncrement = 100.0
        nodeTree = bpy.context.active_object.active_material.node_tree

        # explicitly copy location to avoid ending up with a reference
        # we don't want to modify the location of the original active node

        originalNode = nodeTree.nodes.active
        for i in range(6):
            nodeOffset = list(originalNode.location)

            nodeOffset[0] = nodeOffset[0] + 600.0
            nodeOffset[1] = nodeOffset[1] - 200.0 - (nodeOffsetIncrement*i)

            aovNode = nodeTree.nodes.new(type='ShaderNodeOutputAOV')
            aovNode.location = nodeOffset
            aovNode.name = originalNode.outputs[i+1].name

            nodeTree.links.new(input=originalNode.outputs[i+1], output=aovNode.inputs[1])

        nodeOffset = list(originalNode.location)

        geoInputNode = nodeTree.nodes.new(type='ShaderNodeNewGeometry')
        geoInputNode.location[0] = nodeOffset[0] + 600.0
        geoInputNode.location[1] = nodeOffset[1] - 850.0

        aovNormal = nodeTree.nodes.new(type='ShaderNodeOutputAOV')
        aovNormal.location[0] = nodeOffset[0] + 1000.0
        aovNormal.location[1] = nodeOffset[1] - 850.0

        aovNormal.name = "charNormal"

        nodeTree.links.new(input=geoInputNode.outputs[1], output=aovNormal.inputs[0])
        return {'FINISHED'}


class FTB_OT_FixPrecisionError_Op(bpy.types.Operator):
    bl_idname = "object.fix_precision_error"
    bl_label = "Fix Character Precision Error"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        if not bpy.context.active_object:
            self.report({'ERROR'}, "No armature selected.")
            return {'CANCELLED'}

        if not bpy.context.active_object.type == 'ARMATURE':
            self.report({'ERROR'}, "Active object is not an armature.")
            return {'CANCELLED'}

        armObj = bpy.context.active_object
        grpEmpty = armObj.parent
        emptyName = bpy.context.active_object.name + "_precisionEmpty"
        fixEmpty = bpy.data.objects.new(emptyName, None)
        bpy.context.scene.collection.objects.link(fixEmpty)

        poseBone = bpy.context.active_pose_bone
        childConstraint = poseBone.constraints.new('CHILD_OF')
        childConstraint.target = fixEmpty

        #bpy.ops.view3d.snap_cursor_to_selected
        #grpEmpty.location = bpy.context.scene.cursor.location

        # move empty to bone world postion via matrix_world of armature
        #apply_bone_world_matrix(poseBone=poseBone, armObject=armObj, targetObject=grpEmpty)

        return {'FINISHED'}


classes = (
    FTB_OT_RemoveMaterials_Op, FTB_OT_RemoveModifiers_Op, FTB_OT_EditShaderProperty_Op,
    FTB_OT_RemoveImageDuplicates_Op, FTB_OT_RemoveMaterialDuplicates_Op, FTB_OT_Remove_Edge_Splits_Op,
    FTB_OT_Remove_Empty_Libraries_Op, FTB_OT_UpgradeCharacterAOVs_Op, FTB_OT_RemoveNodeGroupDuplicates_Op,
    FTB_OT_FixPrecisionError_Op
)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
