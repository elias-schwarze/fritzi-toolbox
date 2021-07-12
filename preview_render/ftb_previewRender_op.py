import bpy
import math
from bpy.types import Operator
#from ..ftb_utils import

class FTB_OT_Preview_Render_Op(Operator):
    bl_idname = "object.preview_render"
    bl_label = "Render Previews"
    bl_description = "Render previews"
    bl_options = {"REGISTER", "UNDO"}

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

        if (bpy.context.scene.render.image_settings.file_format in ['AVI_JPEG', 'AVI_RAW', 'FFMPEG']):
            self.report({'WARNING'}, 'Invalid Output Format, please select an image format')
            return {'CANCELLED'}

        previewEmpty = bpy.data.objects.new("ftb_preview_empty", None)
        bpy.context.scene.collection.objects.link(previewEmpty)

        previewCamData = bpy.data.cameras.new(name='ftb_previewCamera')
        previewCamObject = bpy.data.objects.new("ftb_previewCamera", previewCamData)
        bpy.context.scene.collection.objects.link(previewCamObject)

        previewCamObject.parent = previewEmpty

        previewCamData.type = 'ORTHO'
        previewCamData.ortho_scale = 4.0

        previewCamObject.location = (0, -5.53, 1)
        previewCamObject.rotation_euler = ((90*math.pi/180), 0, 0)

        bpy.ops.mesh.primitive_grid_add(name="test" ,x_subdivisions=60, y_subdivisions=60, size=6, enter_editmode=False, align='WORLD', location=(0,0,0), scale=(0,0,0))

        bpy.context.view_layer.update()
        bpy.context.scene.camera = previewCamObject
        bpy.context.view_layer.update()

        totalRenderCount = sum(renderElements)
        currentRenderCount = 0

        wm.progress_begin(0,totalRenderCount)
        wm.progress_update(0)

        if wm.bEnableFront:
            previewEmpty.rotation_euler[2] = 0
            bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_front")
            bpy.ops.render.render(write_still = 1)
            currentRenderCount +=1
            wm.progress_update(currentRenderCount)
            bpy.context.view_layer.update()
                
        if wm.bEnableBack:
            previewEmpty.rotation_euler[2] = math.pi
            bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_back")
            bpy.ops.render.render(write_still = 1)
            currentRenderCount +=1
            wm.progress_update(currentRenderCount)
            bpy.context.view_layer.update()

        if wm.bEnableLeft:
            previewEmpty.rotation_euler[2] = -90*math.pi/180
            bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_left")
            bpy.ops.render.render(write_still = 1)
            currentRenderCount +=1
            wm.progress_update(currentRenderCount)
            bpy.context.view_layer.update()

        if wm.bEnableRight:
            previewEmpty.rotation_euler[2] = 90*math.pi/180
            bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_right")
            bpy.ops.render.render(write_still = 1)
            currentRenderCount +=1
            wm.progress_update(currentRenderCount)
            bpy.context.view_layer.update()

        if wm.bEnable45FrontLeft:
            previewEmpty.rotation_euler[2] = -45*math.pi/180
            bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_45frontleft")
            bpy.ops.render.render(write_still = 1)
            currentRenderCount +=1
            wm.progress_update(currentRenderCount)
            bpy.context.view_layer.update()

        if wm.bEnable45FrontRight:
            previewEmpty.rotation_euler[2] = 45*math.pi/180
            bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_45frontright")
            bpy.ops.render.render(write_still = 1)
            currentRenderCount +=1
            wm.progress_update(currentRenderCount)
            bpy.context.view_layer.update()

        if wm.bEnable45RearLeft:
            previewEmpty.rotation_euler[2] = -135*math.pi/180
            bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_45rearleft")
            bpy.ops.render.render(write_still = 1)
            currentRenderCount +=1
            wm.progress_update(currentRenderCount)
            bpy.context.view_layer.update()

        if wm.bEnable45RearRight:
            previewEmpty.rotation_euler[2] = 135*math.pi/180
            bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_45rearright")
            bpy.ops.render.render(write_still = 1)
            currentRenderCount +=1
            wm.progress_update(currentRenderCount)
            bpy.context.view_layer.update()

        if wm.bEnableTop:
            previewEmpty.rotation_euler[2] = 0
            previewEmpty.rotation_euler[0] = -90*math.pi/180
            previewCamObject.location[2] = 0
            bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_top")
            bpy.ops.render.render(write_still = 1)
            currentRenderCount +=1
            wm.progress_update(currentRenderCount)
            bpy.context.view_layer.update()

        if wm.bEnableBottom:
            previewEmpty.rotation_euler[2] = 0
            previewEmpty.rotation_euler[0] = 90*math.pi/180
            previewCamObject.location[2] = 0
            bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_bottom")
            bpy.ops.render.render(write_still = 1)
            currentRenderCount +=1
            wm.progress_update(currentRenderCount)
            bpy.context.view_layer.update()

        bpy.context.scene.render.filepath = storedRenderPath
        bpy.context.scene.camera = storedRenderCam
        bpy.data.objects.remove(previewCamObject, do_unlink=True)
        bpy.data.objects.remove(previewEmpty, do_unlink=True)
        bpy.data.cameras.remove(previewCamData, do_unlink=True)
        wm.progress_end()
        self.report({'INFO'}, 'Finished')

        return {'FINISHED'}
