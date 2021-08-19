import bpy
import math
import re

from bpy.types import Operator

from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.types import OperatorFileListElement
from bpy.props import BoolProperty, CollectionProperty
from bpy.props import StringProperty

from math import radians


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
            # addGrid()
            pass

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


class FTB_OT_Preview_Import_Op(Operator, ImportHelper):
    bl_idname = "object.preview_import"
    bl_label = "Import Previews"
    bl_description = "Import previews"
    bl_options = {"REGISTER", "UNDO"}

    bpy.types.Object.isRefObject = BoolProperty()

    # Collection Property accessed by ImportHelper to store all selected File filepaths in
    files: CollectionProperty(
        name="FilePaths", type=OperatorFileListElement)

    # String Property accessed by ImportHelper to store directory path of selected files
    directory: StringProperty(subtype='DIR_PATH')

    def loadReference(self, refCollection, refFile, refDirectory,  refRotation, refOffset):
        """Loads a image from file and assigns it to a new reference Empty in the current scene.

        Keyword arguments:\n
        refCollection -- the collection the new Empty should be placed in\n
        file -- the file from which the images is loaded\n
        directory -- directory path of file\n
        refRotation -- the rotation in euler angles of the new Empty\n
        """

        # Create Image datablock and load file
        image = bpy.data.images.load(
            refDirectory + refFile.name, check_existing=False)

        previewEmpty = bpy.data.objects.new("ref_" + refFile.name, None)
        previewEmpty.empty_display_type = 'IMAGE'

        previewEmpty.data = image

        previewEmpty.empty_display_size = 4.0
        previewEmpty.empty_image_offset = refOffset
        previewEmpty.location[2] = -0.125
        previewEmpty.rotation_euler[0] = radians(90)

        previewEmpty.empty_image_side = 'FRONT'
        previewEmpty.empty_image_depth = 'BACK'
        previewEmpty.rotation_euler = refRotation
        previewEmpty.isRefObject = True

        refCollection.objects.link(previewEmpty)

    def execute(self, context):

        for file in self.files:
            if file.name == "":
                self.report({'WARNING'}, "No files selected")
                return{'CANCELLED'}

        previewCollection = bpy.data.collections.new(name="fs_refs")
        bpy.context.collection.children.link(previewCollection)

        for file in self.files:

            if (re.search('_left', file.name, flags=re.I)):
                self.loadReference(
                    refCollection=previewCollection, refFile=file, refDirectory=self.directory, refRotation=(radians(90), 0, radians(-90)), refOffset=(-0.5, 0))

            elif (re.search('_right', file.name, flags=re.I)):
                self.loadReference(
                    refCollection=previewCollection, refFile=file, refDirectory=self.directory, refRotation=(radians(90), 0, radians(90)), refOffset=(-0.5, 0))

            elif (re.search('_front', file.name, flags=re.I)):
                self.loadReference(
                    refCollection=previewCollection, refFile=file, refDirectory=self.directory, refRotation=(radians(90), 0, 0), refOffset=(-0.5, 0))

            elif (re.search('_back', file.name, flags=re.I)):
                self.loadReference(
                    refCollection=previewCollection, refFile=file, refDirectory=self.directory, refRotation=(radians(90), 0, radians(180)), refOffset=(-0.5, 0))

            elif (re.search('_top', file.name, flags=re.I)):
                self.loadReference(
                    refCollection=previewCollection, refFile=file, refDirectory=self.directory, refRotation=(0, 0, 0), refOffset=(-0.5, -0.5))

            elif (re.search('_bottom', file.name, flags=re.I)):
                self.loadReference(
                    refCollection=previewCollection, refFile=file, refDirectory=self.directory, refRotation=(radians(180), 0, 0), refOffset=(-0.5, -0.5))

        return {'FINISHED'}


class FTB_OT_Preview_Reload_Op(Operator):
    bl_idname = "object.preview_reload"
    bl_label = "Reload all Previews"
    bl_description = "Reload all FTB previews"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        for obj in bpy.data.objects:
            if ("isRefObject" in obj and obj.isRefObject):
                obj.data.reload()

        return {'FINISHED'}


def register():

    bpy.utils.register_class(FTB_OT_Preview_Render_Op)
    bpy.utils.register_class(FTB_OT_Set_JPG_Output_Op)
    bpy.utils.register_class(FTB_OT_Preview_Import_Op)
    bpy.utils.register_class(FTB_OT_Preview_Reload_Op)


def unregister():

    bpy.utils.unregister_class(FTB_OT_Preview_Reload_Op)
    bpy.utils.unregister_class(FTB_OT_Preview_Import_Op)
    bpy.utils.unregister_class(FTB_OT_Set_JPG_Output_Op)
    bpy.utils.unregister_class(FTB_OT_Preview_Render_Op)
