import bpy

def createSetMatNodes():
        setMatNodes = bpy.data.node_groups.new(name="FTB_setLocalMaterial", type='GeometryNodeTree')

        setMatNodes.inputs.new(name="Geometry", type="NodeSocketGeometry")
        setMatNodes.inputs.new(name="Material", type="NodeSocketMaterial")
        setMatNodes.outputs.new(name="Geometry", type="NodeSocketGeometry")

        geoInput = setMatNodes.nodes.new(type="NodeGroupInput")

        geoOutput = setMatNodes.nodes.new(type="NodeGroupOutput")
        geoOutput.location = (700.0, 0.0)

        geoSetMat = setMatNodes.nodes.new(type="GeometryNodeSetMaterial")
        geoSetMat.location = (350.0, 0.0)

        setMatNodes.links.new(input=geoInput.outputs[0], output=geoSetMat.inputs["Geometry"])
        setMatNodes.links.new(input=geoInput.outputs[1], output=geoSetMat.inputs[2])
        setMatNodes.links.new(input=geoSetMat.outputs[0], output=geoOutput.inputs[0])

def createReplaceMatNodes():
        setMatNodes = bpy.data.node_groups.new(name="FTB_replaceLocalMaterial", type='GeometryNodeTree')

        setMatNodes.inputs.new(name="Geometry", type="NodeSocketGeometry")
        setMatNodes.inputs.new(name="Replace", type="NodeSocketMaterial")
        setMatNodes.inputs.new(name="With", type="NodeSocketMaterial")
        setMatNodes.outputs.new(name="Geometry", type="NodeSocketGeometry")

        geoInput = setMatNodes.nodes.new(type="NodeGroupInput")

        geoOutput = setMatNodes.nodes.new(type="NodeGroupOutput")
        geoOutput.location = (700.0, 0.0)

        geoSetMat = setMatNodes.nodes.new(type="GeometryNodeReplaceMaterial")
        geoSetMat.location = (350.0, 0.0)

        setMatNodes.links.new(input=geoInput.outputs[0], output=geoSetMat.inputs["Geometry"])
        setMatNodes.links.new(input=geoInput.outputs[1], output=geoSetMat.inputs[1])
        setMatNodes.links.new(input=geoInput.outputs[2], output=geoSetMat.inputs[2])

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

        createReplaceMatNodes()
        
        return {'FINISHED'}

def register():
    bpy.utils.register_class(FTB_OT_GnodesSetMaterials_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_GnodesSetMaterials_Op)

