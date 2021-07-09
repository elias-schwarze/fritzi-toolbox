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

        if (not wm.sOutputPath):
            self.report({'WARNING'}, 'Output path is not set')

        elif (not wm.sFileName):
            self.report({'WARNING'}, 'File name is not set')

        elif (not wm.bEnableFront and not wm.bEnableBack and not wm.bEnableRight and not wm.bEnableLeft and not wm.bEnableTop and not wm.bEnable45Left and not wm.bEnable45Right):
            self.report({'WARNING'}, 'No preview angles selected')

        else:
            previewEmpty = bpy.data.objects.new("fs_preview_empty", None)
            bpy.context.scene.collection.objects.link(previewEmpty)

            previewCamData = bpy.data.cameras.new(name='fs_previewCamera')
            previewCamObject = bpy.data.objects.new("fs_previewCamera", previewCamData)
            bpy.context.scene.collection.objects.link(previewCamObject)

            previewCamObject.parent = previewEmpty

            previewCamData.type = 'ORTHO'
            previewCamData.ortho_scale = 4.0

            previewCamObject.location = (0, -5.53, 1)
            previewCamObject.rotation_euler = ((90*math.pi/180), 0, 0)

            bpy.context.scene.camera = previewCamObject

            renderElements = [wm.bEnableFront, wm.bEnableBack, wm.bEnableLeft, wm.bEnableRight, wm.bEnable45Left, wm.bEnable45Right, wm.bEnableTop]
            totalRenderCount = sum(renderElements)
            currentRenderCount = 0

            wm.progress_begin(0,totalRenderCount)

            if wm.bEnableFront:
                previewEmpty.rotation_euler[2] = 0
                bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_front")
                bpy.ops.render.render(write_still = 1)
                currentRenderCount +=1
                wm.progress_update(currentRenderCount)
                
            if wm.bEnableBack:
                previewEmpty.rotation_euler[2] = math.pi
                bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_back")
                bpy.ops.render.render(write_still = 1)
                currentRenderCount +=1
                wm.progress_update(currentRenderCount)

            if wm.bEnableLeft:
                previewEmpty.rotation_euler[2] = -90*math.pi/180
                bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_left")
                bpy.ops.render.render(write_still = 1)
                currentRenderCount +=1
                wm.progress_update(currentRenderCount)

            if wm.bEnableRight:
                previewEmpty.rotation_euler[2] = 90*math.pi/180
                bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_right")
                bpy.ops.render.render(write_still = 1)
                currentRenderCount +=1
                wm.progress_update(currentRenderCount)

            if wm.bEnable45Left:
                previewEmpty.rotation_euler[2] = -45*math.pi/180
                bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_45left")
                bpy.ops.render.render(write_still = 1)
                currentRenderCount +=1
                wm.progress_update(currentRenderCount)

            if wm.bEnable45Right:
                previewEmpty.rotation_euler[2] = 45*math.pi/180
                bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_45right")
                bpy.ops.render.render(write_still = 1)
                currentRenderCount +=1
                wm.progress_update(currentRenderCount)

            if wm.bEnableTop:
                previewEmpty.rotation_euler[2] = 0
                previewEmpty.rotation_euler[0] = -90*math.pi/180
                previewCamObject.location[2] = 0
                bpy.context.scene.render.filepath = (wm.sOutputPath + wm.sFileName + "_top")
                bpy.ops.render.render(write_still = 1)
                currentRenderCount +=1
                wm.progress_update(currentRenderCount)

            bpy.context.scene.render.filepath = storedRenderPath
            bpy.data.objects.remove(previewCamObject, do_unlink=True)
            bpy.data.objects.remove(previewEmpty, do_unlink=True)
            bpy.data.cameras.remove(previewCamData, do_unlink=True)
            wm.progress_end()



        return {'FINISHED'}