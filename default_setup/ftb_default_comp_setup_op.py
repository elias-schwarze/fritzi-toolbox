import bpy
from bpy.types import Operator


class FTB_OT_DefaultCompSetup_Op(Operator):
    bl_idname = "scene.default_comp_setup"
    bl_label = "Default Compositing Setup"
    bl_description = "Create Default Compositing Setup."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        wm = bpy.context.window_manager

        # Enable Use Nodes
        bpy.context.scene.use_nodes = True

        # Get current compositor node tree and link collection
        compTree = bpy.context.scene.node_tree
        nodeLinks = compTree.links

        # clear any exisiting nodes
        for node in compTree.nodes:
            compTree.nodes.remove(node)

        # create input image node
        image_node = compTree.nodes.new(type='CompositorNodeImage')
        #image_node.image = bpy.data.images['YOUR_IMAGE_NAME']
        image_node.location = 0, 0

        # create output node
        comp_node = compTree.nodes.new('CompositorNodeComposite')
        comp_node.location = 400, 0

        link = nodeLinks.new(image_node.outputs[0], comp_node.inputs[0])

        self.report({'INFO'}, "Comp Setup Successful")

        return {'FINISHED'}

    def invoke(self, context, event):
        return bpy.context.window_manager.invoke_confirm(self, event)


def register():
    bpy.utils.register_class(FTB_OT_DefaultCompSetup_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_DefaultCompSetup_Op)
