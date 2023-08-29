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


def createIndexMatNodes():
    """
    Create a Geometry Node Setup to replace Materials on any Mesh based on Material Index
    """
    # Create node group datablock
    nodeGroupName = "FTB_setIndexMaterial"
    setMatNodeGroup = bpy.data.node_groups.new(name=nodeGroupName, type='GeometryNodeTree')

    # I/O Nodes
    geoInput = setMatNodeGroup.nodes.new(type="NodeGroupInput")
    geoOutput = setMatNodeGroup.nodes.new(type="NodeGroupOutput")
    geoOutput.location = (800.0, 0.0)

    # I/O Sockets
    setMatNodeGroup.inputs.new(name="Geometry", type="NodeSocketGeometry")
    setMatNodeGroup.inputs.new(name="Replace Index", type="NodeSocketInt")
    setMatNodeGroup.inputs[1].min_value = 0

    setMatNodeGroup.inputs.new(name="With", type="NodeSocketMaterial")
    setMatNodeGroup.outputs.new(name="Geometry", type="NodeSocketGeometry")

    # Nodes
    geoSetMat = setMatNodeGroup.nodes.new(type="GeometryNodeSetMaterial")
    geoSetMat.location = (550.0, 0.0)

    getMatIndex = setMatNodeGroup.nodes.new(type="GeometryNodeInputMaterialIndex")
    getMatIndex.location = (0.0, -200.0)

    compareNode = setMatNodeGroup.nodes.new(type="FunctionNodeCompare")
    compareNode.data_type = 'FLOAT'
    compareNode.operation = 'EQUAL'
    compareNode.location = (250.0, -150.0)

    # create links
    setMatNodeGroup.links.new(input=geoInput.outputs[0], output=geoSetMat.inputs["Geometry"])
    setMatNodeGroup.links.new(input=geoInput.outputs[2], output=geoSetMat.inputs[2])
    setMatNodeGroup.links.new(input=geoSetMat.outputs[0], output=geoOutput.inputs[0])

    setMatNodeGroup.links.new(input=getMatIndex.outputs[0], output=compareNode.inputs[0])
    setMatNodeGroup.links.new(input=geoInput.outputs[1], output=compareNode.inputs[1])
    setMatNodeGroup.links.new(input=compareNode.outputs[0], output=geoSetMat.inputs[1])


def createDummyMesh():
    verts = [(0.22750002145767212, -0.28301239013671875, 0.0), (0.22750002145767212, 0.21507026255130768, 0.0), (0.000500023365020752, -0.0649297833442688, 0.0),
             (-0.22550000250339508, 0.21507026255130768, 0.0), (-0.22550000250339508, -0.28301239013671875, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0), (-1.0, 0.0, 0.0),
             (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, -1.0, 0.0)]

    edges = [(2, 3), (1, 2), (0, 1), (3, 4), (5, 6), (7, 8), (9, 10)]

    mesh = bpy.data.meshes.new(("FTB_materialDummy"))
    mesh.from_pydata(verts, edges, [])
    mesh.update()
    return mesh


def createMatDummyObject(localMaterial: bpy.types.Material = None):

    if "FTB_matDummy" in bpy.data.objects:
        matDummyObj = bpy.data.objects["FTB_matDummy"]

    else:
        matDummyObj = bpy.data.objects.new("FTB_matDummy", createDummyMesh())
        bpy.context.scene.collection.objects.link(matDummyObj)

    matDummyObj.lineart.usage = 'EXCLUDE'
    matDummyObj.hide_render = True
    matDummyObj.hide_set(False)

    matDummyObj.hide_viewport = False
    matDummyObj.location.z = -1.0

    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = matDummyObj
    matDummyObj.select_set(True)

    if len(matDummyObj.material_slots) > 0:
        matDummyObj.material_slots[0].material = localMaterial
    else:
        matDummyObj.data.materials.append(localMaterial)


class FTB_OT_GnodesSetMaterials_Op(bpy.types.Operator):
    bl_idname = "object.set_gnodes_materials"
    bl_label = "Set Gnodes Material"
    bl_description = "Set Gnodes Material"
    bl_options = {"REGISTER", "UNDO"}

    matName: bpy.props.StringProperty(name="matName", default="")
    matIndex: bpy.props.IntProperty(name="matIndex", default=0)
    replaceMode: bpy.props.EnumProperty(
        items=[
            ('SET', "Set", ""),
            ('REPLACE', "Replace", ""),
            ('INDEX', "Index Replace", "")
        ],
        default='SET'
    )

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

        if self.replaceMode == 'SET':
            if "FTB_setLocalMaterial" not in bpy.data.node_groups:
                createSetMatNodes(replaceMat=False)

        if self.replaceMode == 'REPLACE':
            if "FTB_replaceLocalMaterial" not in bpy.data.node_groups:
                createSetMatNodes(replaceMat=True)

        if self.replaceMode == 'INDEX':
            createIndexMatNodes()

        mod = obj.modifiers.new(name="FTBGeoNodesMat", type='NODES')
        oldMat = obj.material_slots[obj.active_material_index].material

        newMat = oldMat.copy()
        newMat.name = strip_End_Numbers(newMat.name) + "_local"

        if self.replaceMode == 'REPLACE':
            mod.node_group = bpy.data.node_groups["FTB_replaceLocalMaterial"]
            mod["Input_1"] = oldMat
            mod["Input_2"] = newMat

        elif self.replaceMode == 'SET':
            mod.node_group = bpy.data.node_groups["FTB_setLocalMaterial"]
            mod["Input_1"] = newMat

        elif self.replaceMode == 'INDEX':
            mod.node_group = bpy.data.node_groups["FTB_setIndexMaterial"]
            mod["Input_1"] = self.matIndex
            mod["Input_2"] = newMat

        # Create material dummy object
        createMatDummyObject(localMaterial=newMat)

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
