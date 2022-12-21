import os
import re
import bpy

from bpy.types import Operator
from bpy.app.handlers import persistent

OS_SEPARATOR = os.sep
TEXTURES_PATH = "060_textures" + OS_SEPARATOR + "010_textures_basic" + OS_SEPARATOR
SHADERS_PATH = "050_shaders" + OS_SEPARATOR
ASSETS_DIRNAME = "060_assets"
FRITZISHADER_FILENAME = "fritzi_shader_props.blend"
BRUSHTEXTURE_NAME = "fs_tx001_pinselflecke.jpg"
SPLATTEXTURE_NAME = "fs_tx002_gesprenkelt.png"


class MaterialHelper:
    FritziNodeGroup = None
    BrushTexture = None
    SplatTexture = None


@persistent
def DepsgraphCustomUpdate(self, context):
    MaterialHelper.FritziNodeGroup = FindFritziShaderGroup()
    MaterialHelper.BrushTexture = FindImageTextureByName("(fs_tx001|Fritzi_env)")
    MaterialHelper.SplatTexture = FindImageTextureByName("(fs_tx002|paint_splat)")


def FindPropID(Name):
    match = re.search("(hpr|pr|bg|vg)[0-9]*", Name)
    if match:
        return match.group()

    return None


def GetAssetsDirPath(FilePath):
    if FilePath.find(ASSETS_DIRNAME) == -1:
        return ""

    return FilePath[:FilePath.find(ASSETS_DIRNAME) + len(ASSETS_DIRNAME)]


def FindFritziShaderGroup():
    for group in bpy.data.node_groups:
        if group.library is not None:  # skip if group is a linked asset
            continue

        bFoundGroup = re.search("Fritzi_Props", group.name_full)
        if bFoundGroup:
            return group

    return None


def FindImageTextureByName(RegExSearch):
    for image in bpy.data.images:
        if image.library is not None:  # skip if image is a linked asset
            continue

        match = re.search(RegExSearch, image.name_full)
        if match:
            return image

    return None


def CreateFritziMaterial(Name):
    Material = bpy.data.materials.new(name=Name)

    Material.use_nodes = True
    nodes = Material.node_tree.nodes

    MaterialOutput = nodes.get('Material Output')
    nodes.remove(nodes.get('Principled BSDF'))

    FritziNode = nodes.new('ShaderNodeGroup')

    FritziNode.node_tree = MaterialHelper.FritziNodeGroup
    if FritziNode:
        FritziNode.width = 220
        FritziNode.inputs[0].default_value = (0.3, 0.3, 0.3, 1.0)
        FritziNode.inputs[2].default_value = 0
        FritziNode.inputs[5].default_value = 0
        FritziNode.inputs[9].default_value = 100

    FritziNode.location = (10, 300)

    BrushMRNode = nodes.new('ShaderNodeMapRange')
    BrushMRNode.inputs[3].default_value = 0.3
    BrushMRNode.inputs[4].default_value = 0.7
    BrushMRNode.location = (-180, 200)

    BrushImageNode = nodes.new('ShaderNodeTexImage')
    BrushImageNode.image = MaterialHelper.BrushTexture
    BrushImageNode.interpolation = 'Smart'
    BrushImageNode.projection = 'BOX'
    BrushImageNode.projection_blend = 0.5
    BrushImageNode.location = (-480, 200)

    BrushMappingNode = nodes.new('ShaderNodeMapping')
    BrushMappingNode.location = (-670, 200)

    BrushTCNode = nodes.new('ShaderNodeTexCoord')
    BrushTCNode.location = (-860, 200)

    SplatMRNode = nodes.new('ShaderNodeMapRange')
    SplatMRNode.inputs[3].default_value = 0.5
    SplatMRNode.location = (-180, -200)

    SplatImageNode = nodes.new('ShaderNodeTexImage')
    SplatImageNode.image = MaterialHelper.SplatTexture
    SplatImageNode.interpolation = 'Smart'
    SplatImageNode.projection = 'BOX'
    SplatImageNode.projection_blend = 0.5
    SplatImageNode.location = (-480, -200)

    SplatMappingNode = nodes.new('ShaderNodeMapping')
    SplatMappingNode.location = (-670, -200)

    SplatTCNode = nodes.new('ShaderNodeTexCoord')
    SplatTCNode.location = (-860, -200)

    # begin linking
    links = Material.node_tree.links

    links.new(BrushMappingNode.inputs[0], BrushTCNode.outputs[3])
    links.new(BrushImageNode.inputs[0], BrushMappingNode.outputs[0])
    links.new(BrushMRNode.inputs[0], BrushImageNode.outputs[0])

    links.new(SplatMappingNode.inputs[0], SplatTCNode.outputs[3])
    links.new(SplatImageNode.inputs[0], SplatMappingNode.outputs[0])
    links.new(SplatMRNode.inputs[0], SplatImageNode.outputs[0])

    if FritziNode:
        links.new(FritziNode.inputs[1], BrushMRNode.outputs[0])
        links.new(FritziNode.inputs[4], SplatMRNode.outputs[0])
        links.new(MaterialOutput.inputs[0], FritziNode.outputs[0])

    return Material


ObjWhitelist = ['MESH', 'CURVE', 'FONT', 'SURFACE', 'META']


class FTB_OT_AppendFritziShader_Op(Operator):
    bl_idname = "wm.appendfritzishader"
    bl_label = "Click to append Fritzi Prop Shader"
    bl_description = "Tries to append the Fritzi Prop Shader. File needs to be saved beforehand to execute this command"

    @classmethod
    def poll(cls, context):
        if not bpy.data.is_saved or bpy.data.filepath == '':
            return False

        return True

    def execute(self, context):
        path = bpy.data.filepath

        if path.find("fritzi_serie") == -1:
            self.report({'WARNING'}, "File does not seem to be a part of the Fritzi-Project folder structure! Please save it within the Fritzi Project to use this feature")
            return {'CANCELLED'}

        abspath = GetAssetsDirPath(path) + OS_SEPARATOR + SHADERS_PATH + FRITZISHADER_FILENAME

        if not os.path.exists(abspath):
            self.report({'WARNING'}, "Couldn't find shader file in path: " + abspath + ". Please check if you have downloaded all assets to you machine.")
            return {'CANCELLED'}

        section = "\\NodeTree\\"
        object = "shader-Fritzi_Props"

        filepath = abspath + section + object
        directory = abspath + section
        filename = object

        try:
            bpy.ops.wm.append(filepath=filepath, filename=filename, directory=directory)
        except RuntimeError as err:
            self.report({'WARNING'}, str(err), end="")
            return {'CANCELLED'}

        self.report({'INFO'}, "Fritzi Props Shader appended")
        return {'FINISHED'}


class FTB_OT_OpenBrushTexture_Op(Operator):
    bl_idname = "image.openbrushtexture"
    bl_label = "Click to open brush"
    bl_description = "Tries to add the '" + BRUSHTEXTURE_NAME + "' texture to the scene"

    @classmethod
    def poll(cls, context):
        if not bpy.data.is_saved or bpy.data.filepath == '':
            return False

        return True

    def execute(self, context):
        path = bpy.data.filepath

        if path.find("fritzi_serie") == -1:
            self.report({'WARNING'}, "File does not seem to be a part of the Fritzi-Project folder structure! Please save it within the Fritzi Project to use this feature")
            return {'CANCELLED'}

        abspath = GetAssetsDirPath(path) + OS_SEPARATOR + TEXTURES_PATH + BRUSHTEXTURE_NAME

        if not os.path.exists(abspath):
            self.report({'WARNING'}, "Couldn't find texture file in path: " + abspath + ". Please check if you have downloaded all assets to you machine.")
            return {'CANCELLED'}

        try:
            bpy.ops.image.open(filepath=abspath, relative_path=True)
        except RuntimeError as err:
            self.report({'WARNING'}, str(err), end="")
            return {'CANCELLED'}

        self.report({'INFO'}, "Brush Texture added to scene.")
        return {'FINISHED'}


class FTB_OT_OpenSplatTexture_Op(Operator):
    bl_idname = "image.opensplattexture"
    bl_label = "Click to open splat texture"
    bl_description = "Tries to add the '" + SPLATTEXTURE_NAME + "' texture to the scene"

    @classmethod
    def poll(cls, context):
        if not bpy.data.is_saved or bpy.data.filepath == '':
            return False

        return True

    def execute(self, context):
        path = bpy.data.filepath

        if path.find("fritzi_serie") == -1:
            self.report({'WARNING'}, "File does not seem to be a part of the Fritzi-Project folder structure! Please save it within the Fritzi Project to use this feature")
            return {'CANCELLED'}

        abspath = GetAssetsDirPath(path) + OS_SEPARATOR + TEXTURES_PATH + SPLATTEXTURE_NAME

        if not os.path.exists(abspath):
            self.report({'WARNING'}, "Couldn't find texture file in path: " + abspath + ". Please check if you have downloaded all assets to you machine.")
            return {'CANCELLED'}

        try:
            bpy.ops.image.open(filepath=abspath, relative_path=True)
        except RuntimeError as err:
            self.report({'WARNING'}, str(err), end="")
            return {'CANCELLED'}

        self.report({'INFO'}, "Splat Texture added to scene.")
        return {'FINISHED'}


class FTB_OT_PopulateMatSlots_Op(Operator):
    bl_idname = "object.populatematerials"
    bl_label = "Create Materials for All"
    bl_description = "Creates Fritzi materials with appropriate name for all material slots of the active object.\nDoes not override already assigned materials. Only works on linked library props"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not MaterialHelper.FritziNodeGroup:
            return False

        if obj.type not in ObjWhitelist or len(obj.material_slots) < 1 or not obj.override_library:
            return False

        return True

    def execute(self, context):
        Object = bpy.context.view_layer.objects.active
        PropID = FindPropID(Object.override_library.reference.library.name_full)

        if not PropID:
            self.report({'WARNING'}, "Could not find valid Prop ID for Object. Double check prop file name. Operation cancelled.")
            return {'CANCELLED'}

        matname = PropID + "_" + Object.name_full
        if len(Object.material_slots) > 1:
            slotcount = 1
            matassignedcount = 0
            for mslot in Object.material_slots:
                if not mslot.material:
                    mslot.link = 'OBJECT'
                    mslot.material = CreateFritziMaterial(matname + "_slot" + str(slotcount))
                    matassignedcount += 1
                slotcount += 1
            if matassignedcount == 0:
                self.report({'WARNING'}, "All slots already have materials assigned. Operation cancelled.")
                return {'CANCELLED'}
            else:
                self.report({'INFO'}, str(matassignedcount) + " new material successfully created. " + str(len(Object.material_slots) - matassignedcount) + " slots skipped.")
                return {'FINISHED'}
        else:
            if not Object.material_slots[0].material:
                Object.material_slots[0].link = 'OBJECT'
                Object.material_slots[0].material = CreateFritziMaterial(matname)
                self.report({'INFO'}, "New material successfully created")
                return {'FINISHED'}
            else:
                self.report({'WARNING'}, "Slot already has material assigned. Operation cancelled.")
                return {'CANCELLED'}


class FTB_OT_PopulateMatSlotSingle_Op(Operator):
    bl_idname = "object.populatematerialslot"
    bl_label = "Create Material for Slot"
    bl_description = "Creates Fritzi materials for selected slot of active object. Only works on empty slots."
    bl_options = {'REGISTER', 'UNDO'}

    MaterialName: bpy.props.StringProperty(name="Enter Material Name", default="")

    @classmethod
    def poll(cls, context):
        obj = context.active_object

        if not MaterialHelper.FritziNodeGroup:
            return False

        if obj.type not in ObjWhitelist or len(obj.material_slots) < 1:
            return False

        if not obj.material_slots[obj.active_material_index].material is None:
            return False

        return True

    def execute(self, context):

        if not self.MaterialName:
            self.report({'WARNING'}, "Please enter a valid name. Operation cancelled.")
            return {'CANCELLED'}

        Object = bpy.context.view_layer.objects.active
        SlotID = Object.active_material_index
        Object.material_slots[SlotID].link = 'OBJECT'
        Object.material_slots[SlotID].material = CreateFritziMaterial(self.MaterialName)

        self.report({'INFO'}, "New material successfully created")
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


def register():
    bpy.utils.register_class(FTB_OT_AppendFritziShader_Op)
    bpy.utils.register_class(FTB_OT_OpenBrushTexture_Op)
    bpy.utils.register_class(FTB_OT_OpenSplatTexture_Op)
    bpy.utils.register_class(FTB_OT_PopulateMatSlots_Op)
    bpy.utils.register_class(FTB_OT_PopulateMatSlotSingle_Op)
    bpy.app.handlers.depsgraph_update_pre.append(DepsgraphCustomUpdate)


def unregister():
    bpy.app.handlers.depsgraph_update_pre.remove(DepsgraphCustomUpdate)
    bpy.utils.unregister_class(FTB_OT_PopulateMatSlotSingle_Op)
    bpy.utils.unregister_class(FTB_OT_PopulateMatSlots_Op)
    bpy.utils.unregister_class(FTB_OT_OpenSplatTexture_Op)
    bpy.utils.unregister_class(FTB_OT_OpenBrushTexture_Op)
    bpy.utils.unregister_class(FTB_OT_AppendFritziShader_Op)
