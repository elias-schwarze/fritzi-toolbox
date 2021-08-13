import bpy
import math

from bpy.types import Operator


class FTB_OT_Preview_Render_Op(Operator):
    bl_idname = "object.preview_render"
    bl_label = "Render Previews"
    bl_description = "Render previews"
    bl_options = {"REGISTER", "UNDO"}

    def addGrid():
        gridMesh = bpy.data.meshes.new("gridMesh")
        gridObject = bpy.data.objects.new("ftb_preview_grid", gridMesh)
        bpy.context.scene.collection.objects.link(gridObject)

    def removeGrid():
        pass

    def invoke(self, context, event):
        if(bpy.context.scene.render.image_settings.file_format in ['AVI_JPEG', 'AVI_RAW', 'FFMPEG']):
            self.report(
                {'WARNING'}, "Please select a non-animation output format")
            return {'CANCELLED'}
        else:
            return self.execute(context)

    def execute(self, context):

        wm = bpy.context.window_manager
        storedRenderPath = bpy.context.scene.render.filepath
        storedRenderCam = bpy.context.scene.camera

        renderElements = [wm.bEnableFront, wm.bEnableBack, wm.bEnableLeft, wm.bEnableRight,
                          wm.bEnable45FrontLeft, wm.bEnable45FrontRight, wm.bEnable45RearLeft,
                          wm.bEnable45RearRight, wm.bEnableTop, wm.bEnableBottom]

        if (not wm.sOutputPath):
            self.report({'WARNING'}, 'Output path is not set')
            return {'CANCELLED'}

        if (not wm.sFileName):
            self.report({'WARNING'}, 'File name is not set')
            return {'CANCELLED'}

        if (sum(renderElements) == 0):
            self.report({'WARNING'}, 'No preview angles selected')
            return {'CANCELLED'}

        previewEmpty = bpy.data.objects.new("ftb_preview_empty", None)
        bpy.context.scene.collection.objects.link(previewEmpty)

        previewCamData = bpy.data.cameras.new(name='ftb_previewCamera')
        previewCamObject = bpy.data.objects.new(
            "ftb_previewCamera", previewCamData)
        bpy.context.scene.collection.objects.link(previewCamObject)

        previewCamObject.parent = previewEmpty

        previewCamData.type = 'ORTHO'
        previewCamData.ortho_scale = 4.0

        previewCamObject.location = (0, -5.53, 1)
        previewCamObject.rotation_euler = ((90*math.pi/180), 0, 0)

        if (wm.bRenderGrid):
            # bpy.ops.mesh.primitive_grid_add(x_subdivisions=60, y_subdivisions=60, size=6,
            # enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(0, 0, 0))
            addGrid()
            
        bpy.context.view_layer.update()
        bpy.context.view_layer.depsgraph.update()
        bpy.context.scene.camera = previewCamObject
        bpy.context.view_layer.update()
        bpy.context.view_layer.depsgraph.update()

        totalRenderCount = sum(renderElements)
        currentRenderCount = 0

        wm.progress_begin(0, totalRenderCount)
        wm.progress_update(0)

        if wm.bEnableFront:
            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

            previewEmpty.rotation_euler[2] = 0
            bpy.context.scene.render.filepath = (
                wm.sOutputPath + wm.sFileName + "_front")
            bpy.ops.render.render(write_still=1)
            currentRenderCount += 1
            wm.progress_update(currentRenderCount)

            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

        if wm.bEnableBack:
            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

            previewEmpty.rotation_euler[2] = math.pi
            bpy.context.scene.render.filepath = (
                wm.sOutputPath + wm.sFileName + "_back")
            bpy.ops.render.render(write_still=1)
            currentRenderCount += 1
            wm.progress_update(currentRenderCount)

            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

        if wm.bEnableLeft:
            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

            previewEmpty.rotation_euler[2] = -90*math.pi/180
            bpy.context.scene.render.filepath = (
                wm.sOutputPath + wm.sFileName + "_left")
            bpy.ops.render.render(write_still=1)
            currentRenderCount += 1
            wm.progress_update(currentRenderCount)

            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

        if wm.bEnableRight:
            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

            previewEmpty.rotation_euler[2] = 90*math.pi/180
            bpy.context.scene.render.filepath = (
                wm.sOutputPath + wm.sFileName + "_right")
            bpy.ops.render.render(write_still=1)
            currentRenderCount += 1
            wm.progress_update(currentRenderCount)

            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

        if wm.bEnable45FrontLeft:
            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

            previewEmpty.rotation_euler[2] = -45*math.pi/180
            bpy.context.scene.render.filepath = (
                wm.sOutputPath + wm.sFileName + "_45frontleft")
            bpy.ops.render.render(write_still=1)
            currentRenderCount += 1
            wm.progress_update(currentRenderCount)

            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

        if wm.bEnable45FrontRight:
            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

            previewEmpty.rotation_euler[2] = 45*math.pi/180
            bpy.context.scene.render.filepath = (
                wm.sOutputPath + wm.sFileName + "_45frontright")
            bpy.ops.render.render(write_still=1)
            currentRenderCount += 1
            wm.progress_update(currentRenderCount)

            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

        if wm.bEnable45RearLeft:
            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

            previewEmpty.rotation_euler[2] = -135*math.pi/180
            bpy.context.scene.render.filepath = (
                wm.sOutputPath + wm.sFileName + "_45rearleft")
            bpy.ops.render.render(write_still=1)
            currentRenderCount += 1
            wm.progress_update(currentRenderCount)

            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

        if wm.bEnable45RearRight:
            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

            previewEmpty.rotation_euler[2] = 135*math.pi/180
            bpy.context.scene.render.filepath = (
                wm.sOutputPath + wm.sFileName + "_45rearright")
            bpy.ops.render.render(write_still=1)
            currentRenderCount += 1
            wm.progress_update(currentRenderCount)

            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

        if wm.bEnableTop:
            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

            previewEmpty.rotation_euler[2] = 0
            previewEmpty.rotation_euler[0] = -90*math.pi/180
            previewCamObject.location[2] = 0
            bpy.context.scene.render.filepath = (
                wm.sOutputPath + wm.sFileName + "_top")
            bpy.ops.render.render(write_still=1)
            currentRenderCount += 1
            wm.progress_update(currentRenderCount)

            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

        if wm.bEnableBottom:
            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

            previewEmpty.rotation_euler[2] = 0
            previewEmpty.rotation_euler[0] = 90*math.pi/180
            previewCamObject.location[2] = 0
            bpy.context.scene.render.filepath = (
                wm.sOutputPath + wm.sFileName + "_bottom")
            bpy.ops.render.render(write_still=1)
            currentRenderCount += 1
            wm.progress_update(currentRenderCount)

            bpy.context.view_layer.update()
            bpy.context.view_layer.depsgraph.update()

        bpy.context.scene.render.filepath = storedRenderPath
        bpy.context.scene.camera = storedRenderCam
        bpy.data.objects.remove(previewCamObject, do_unlink=True)
        bpy.data.objects.remove(previewEmpty, do_unlink=True)
        bpy.data.cameras.remove(previewCamData, do_unlink=True)
        wm.progress_end()
        self.report({'INFO'}, "Finished")

        return {'FINISHED'}


class FTB_OT_Set_JPG_Output_Op(Operator):
    bl_idname = "scene.set_jpg_output"
    bl_label = "Set JPEG Output"
    bl_description = "Set output format to still image JPG with 90% Quality"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        bpy.context.scene.render.image_settings.file_format = 'JPEG'
        bpy.context.scene.render.image_settings.quality = 90
        self.report({'INFO'}, "Output set to JPEG")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_Preview_Render_Op)
    bpy.utils.register_class(FTB_OT_Set_JPG_Output_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_Set_JPG_Output_Op)
    bpy.utils.unregister_class(FTB_OT_Preview_Render_Op)
