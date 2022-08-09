import bpy
from ..utility_functions.ftb_string_utils import strip_End_Numbers


def createSetMatNodes(replaceMat=False):
    """
    Create a Geometry Node Setup to replace Materials on any Mesh
    param replaceMat: Set to True to create a setup to replace only specific Material slots, set to False to create setup that overrides all material slots of the given object
    """

    # create node group, set name
    if replaceMat:
        nodeGroupName = "FTB_replaceLocalMaterial"
        setMatNodeGroup = bpy.data.node_groups.new(name=nodeGroupName, type='GeometryNodeTree')

    else:
        nodeGroupName = "FTB_setLocalMaterial"
        setMatNodeGroup = bpy.data.node_groups.new(name=nodeGroupName, type='GeometryNodeTree')

    # I/O Nodes
    geoInput = setMatNodeGroup.nodes.new(type="NodeGroupInput")
    geoOutput = setMatNodeGroup.nodes.new(type="NodeGroupOutput")
    geoOutput.location = (700.0, 0.0)

    # I/O Sockets for the entire node group
    setMatNodeGroup.inputs.new(name="Geometry", type="NodeSocketGeometry")

    if replaceMat:
        setMatNodeGroup.inputs.new(name="Replace", type="NodeSocketMaterial")
        setMatNodeGroup.inputs.new(name="With", type="NodeSocketMaterial")
        geoSetMat = setMatNodeGroup.nodes.new(type="GeometryNodeReplaceMaterial")

    else:
        setMatNodeGroup.inputs.new(name="Material", type="NodeSocketMaterial")
        geoSetMat = setMatNodeGroup.nodes.new(type="GeometryNodeSetMaterial")

    setMatNodeGroup.outputs.new(name="Geometry", type="NodeSocketGeometry")
    geoSetMat.location = (350.0, 0.0)

    # create links between available nodes
    setMatNodeGroup.links.new(input=geoInput.outputs[0], output=geoSetMat.inputs["Geometry"])

    if replaceMat:
        setMatNodeGroup.links.new(input=geoInput.outputs[1], output=geoSetMat.inputs[1])
        setMatNodeGroup.links.new(input=geoInput.outputs[2], output=geoSetMat.inputs[2])

    else:
        setMatNodeGroup.links.new(input=geoInput.outputs[1], output=geoSetMat.inputs[2])

    setMatNodeGroup.links.new(input=geoSetMat.outputs[0], output=geoOutput.inputs[0])


class FTB_OT_GnodesSetMaterials_Op(bpy.types.Operator):
    bl_idname = "object.set_gnodes_materials"
    bl_label = "Set Gnodes Material"
    bl_description = "Set Gnodes Material"
    bl_options = {"REGISTER", "UNDO"}

    replaceMats: bpy.props.BoolProperty(name="replaceMats", default=False)
    matName: bpy.props.StringProperty(name="matName", default="")

    # should only work in object mode
    @classmethod
    def poll(cls, context):

        if not context.object:
            return True
        obj = context.object

        if obj:
            if obj.mode == "OBJECT":
                return True

        return False

    def execute(self, context):

        obj = bpy.context.active_object

        if "FTB_setLocalMaterial" not in bpy.data.node_groups:
            createSetMatNodes(replaceMat=False)

        if "FTB_replaceLocalMaterial" not in bpy.data.node_groups:
            createSetMatNodes(replaceMat=True)

        mod = obj.modifiers.new(name="FTBGeoNodesMat", type='NODES')
        oldMat = obj.material_slots[obj.active_material_index].material

        newMat = oldMat.copy()
        newMat.name = strip_End_Numbers(newMat.name) + "_local"

        if self.replaceMats:
            mod.node_group = bpy.data.node_groups["FTB_replaceLocalMaterial"]
            mod["Input_1"] = oldMat
            mod["Input_2"] = newMat

        else:
            mod.node_group = bpy.data.node_groups["FTB_setLocalMaterial"]
            mod["Input_1"] = newMat

        return {'FINISHED'}

    def invoke(self, context, event):
        obj = bpy.context.active_object
        oldMat = obj.material_slots[obj.active_material_index].material
        if not oldMat.library:
            return context.window_manager.invoke_confirm(self, event)
        else:
            return self.execute(context)


def register():
    bpy.utils.register_class(FTB_OT_GnodesSetMaterials_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_GnodesSetMaterials_Op)
