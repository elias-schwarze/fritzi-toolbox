import bpy

from bpy.types import GreasePencil, Operator


class FTB_OT_DefaultAddLineart_Op(Operator):
    bl_idname = "object.default_add_lineart"
    bl_label = "Add Line Art Object"
    bl_description = "Add a GPencil Object with the active collection as source. Automatically sets up default Line Art settings."
    bl_options = {"REGISTER", "UNDO"}

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object

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

        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_DefaultAddLineart_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_DefaultAddLineart_Op)
