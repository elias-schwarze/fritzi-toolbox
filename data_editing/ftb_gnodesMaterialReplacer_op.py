import bpy

def createSetMatNodes(replaceMat = False):
    """
    Create a Geometry Node Setup to replace Materials on any Mesh 
    param replaceMat: Set to True to create a setup to replace only specific Material slots, set to False to create setup that overrides all material slots of the given object
    """

    # create node group and set name
    if replaceMat:
        nodeGroupName = "FTB_replaceLocalMaterial"

    else:
        nodeGroupName = "FTB_setLocalMaterial"

    setMatNodes = bpy.data.node_groups.new(name=nodeGroupName, type='GeometryNodeTree')

    # I/O Nodes
    geoInput = setMatNodes.nodes.new(type="NodeGroupInput")
    geoOutput = setMatNodes.nodes.new(type="NodeGroupOutput")
    geoOutput.location = (700.0, 0.0)

    # I/O Sockets for the entire node group
    setMatNodes.inputs.new(name="Geometry", type="NodeSocketGeometry")

    if replaceMat:
        setMatNodes.inputs.new(name="Replace", type="NodeSocketMaterial")
        setMatNodes.inputs.new(name="With", type="NodeSocketMaterial")
        geoSetMat = setMatNodes.nodes.new(type="GeometryNodeReplaceMaterial")

    else: 
        setMatNodes.inputs.new(name="Material", type="NodeSocketMaterial")
        geoSetMat = setMatNodes.nodes.new(type="GeometryNodeSetMaterial")

    setMatNodes.outputs.new(name="Geometry", type="NodeSocketGeometry")
    geoSetMat.location = (350.0, 0.0)

    # create links between available nodes
    setMatNodes.links.new(input=geoInput.outputs[0], output=geoSetMat.inputs["Geometry"])

    if replaceMat:
        setMatNodes.links.new(input=geoInput.outputs[1], output=geoSetMat.inputs[1])
        setMatNodes.links.new(input=geoInput.outputs[2], output=geoSetMat.inputs[2])

    else:
        setMatNodes.links.new(input=geoInput.outputs[1], output=geoSetMat.inputs[2])
    
    setMatNodes.links.new(input=geoSetMat.outputs[0], output=geoOutput.inputs[0])


class FTB_OT_GnodesSetMaterials_Op(bpy.types.Operator):
    bl_idname = "object.set_gnodes_materials"
    bl_label = "Set Gnodes Material"
    bl_description = "Set Gnodes Material"
    bl_options = {"REGISTER", "UNDO"}

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

        createSetMatNodes(replaceMat=True)
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(FTB_OT_GnodesSetMaterials_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_GnodesSetMaterials_Op)

