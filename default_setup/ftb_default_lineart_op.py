import bpy

from bpy.types import Operator


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
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_DefaultAddLineart_Op)
    bpy.utils.register_class(FTB_OT_Copy_Optimize_Lines_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_Copy_Optimize_Lines_Op)
    bpy.utils.unregister_class(FTB_OT_DefaultAddLineart_Op)
