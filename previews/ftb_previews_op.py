import bpy
import inspect
import math
import os
import re
import sys

from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator, OperatorFileListElement
from bpy.props import BoolProperty, CollectionProperty, StringProperty
from .. utility_functions import ftb_logging as log

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
        if (bpy.context.scene.render.image_settings.file_format in ['AVI_JPEG', 'AVI_RAW', 'FFMPEG']):
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
                return {'CANCELLED'}

        previewCollection = bpy.data.collections.new(name="fs_refs")
        bpy.context.collection.children.link(previewCollection)

        for file in self.files:

            if (re.search('_left', file.name, flags=re.I)):
                self.loadReference(refCollection=previewCollection,
                                   refFile=file,
                                   refDirectory=self.directory,
                                   refRotation=(radians(90), 0, radians(-90)),
                                   refOffset=(-0.5, 0))

            elif (re.search('_right', file.name, flags=re.I)):
                self.loadReference(refCollection=previewCollection,
                                   refFile=file,
                                   refDirectory=self.directory,
                                   refRotation=(radians(90), 0, radians(90)), refOffset=(-0.5, 0))

            elif (re.search('_front', file.name, flags=re.I)):
                self.loadReference(refCollection=previewCollection,
                                   refFile=file,
                                   refDirectory=self.directory,
                                   refRotation=(radians(90), 0, 0),
                                   refOffset=(-0.5, 0))

            elif (re.search('_back', file.name, flags=re.I)):
                self.loadReference(refCollection=previewCollection,
                                   refFile=file,
                                   refDirectory=self.directory,
                                   refRotation=(radians(90), 0, radians(180)),
                                   refOffset=(-0.5, 0))

            elif (re.search('_top', file.name, flags=re.I)):
                self.loadReference(refCollection=previewCollection,
                                   refFile=file,
                                   refDirectory=self.directory,
                                   refRotation=(0, 0, 0),
                                   refOffset=(-0.5, -0.5))

            elif (re.search('_bottom', file.name, flags=re.I)):
                self.loadReference(refCollection=previewCollection,
                                   refFile=file,
                                   refDirectory=self.directory,
                                   refRotation=(radians(180), 0, 0),
                                   refOffset=(-0.5, -0.5))

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


class FTB_OT_Render_Shot_Preview_Op(Operator):
    bl_idname = "render.ftb_preview"
    bl_label = "FTB: Viewport Animation"
    bl_description = "Uses the active viewport to render a preview animation with specific render settings"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene

        initial_res_percent = scene.render.resolution_percentage
        initial_fps = scene.render.fps
        initial_frame_step = scene.frame_step
        initial_samples = scene.eevee.taa_samples
        initial_file_format = scene.render.image_settings.file_format

        scene.render.resolution_percentage = 25
        scene.render.fps = 25
        scene.frame_step = 2
        scene.eevee.taa_samples = 64
        scene.render.image_settings.file_format = 'AVI_JPEG'

        try:
            context.space_data.overlay.show_overlays = False
            bpy.ops.render.opengl(animation=True)
        except:
            self.report({'ERROR'}, "Error rendering preview")
        finally:
            scene.render.resolution_percentage = initial_res_percent
            scene.render.fps = initial_fps
            scene.frame_step = initial_frame_step
            scene.eevee.taa_samples = initial_samples
            scene.render.image_settings.file_format = initial_file_format
            context.space_data.overlay.show_overlays = True
        self.report({'INFO'}, "Preview rendered!")
        return {'FINISHED'}


class FTB_OT_RenderShotPreviews(Operator):
    bl_idname = "render.ftb_shot_previews"
    bl_label = "FTB: Export Shot Previews"
    bl_description = "Exports viewport stills in rendered view to the render output path of all frames you specified"
    bl_options = {"REGISTER"}

    input_error_msg: str = ""
    alternative_seps = {";", ".", "|"}

    def validate_input(self, context):
        if self.render_frames.isspace() or not self.render_frames:
            self.invalid_input = True
            FTB_OT_RenderShotPreviews.input_error_msg = "Input is empty!"
            return None

        input_has_numbers = False
        input: str = self.render_frames.replace(" ", "")
        for char in input:
            input_has_numbers |= char.isnumeric()
            valid_char = char == "," or char in FTB_OT_RenderShotPreviews.alternative_seps or char.isnumeric()

            if not valid_char:
                self.invalid_input = True
                FTB_OT_RenderShotPreviews.input_error_msg = (
                    f"Only numbers [0-9] and characters "
                    f", {''.join((c + ' ') for c in FTB_OT_RenderShotPreviews.alternative_seps)}allowed")
                return None

        if not input_has_numbers:
            self.invalid_input = True
            FTB_OT_RenderShotPreviews.input_error_msg = (f"Enter at least one number")
            return None

        self.invalid_input = False
        return None

    invalid_input: BoolProperty(default=False,
                                options={'HIDDEN'})

    open_render_dir: BoolProperty(name="Open Output directory in Explorer?",
                                  default=False)

    render_frames: StringProperty(name="Frame List",
                                  description="Specify a list of frames to export. Use , ; . | as separators",
                                  options={'TEXTEDIT_UPDATE'},
                                  update=validate_input)

    @classmethod
    def poll(cls, context):
        if context.area.type != 'VIEW_3D':
            return False
        if not bpy.data.is_saved:
            cls.poll_message_set("File is not saved. Save file on disk to use this feature")
            return False
        if context.scene.render.image_settings.file_format in {'FFMPEG', 'AVI_RAW', 'AVI_JPEG'}:
            cls.poll_message_set(
                "Output file format must be an image-format. Pick an image-format in Output Properties Tab")
            return False
        if not context.scene.render.filepath or context.scene.render.filepath.isspace():
            cls.poll_message_set("Output path is invalid. Specify a valid render output path in Output Properties Tab")
            return False
        return True

    def draw(self, context):
        if self.invalid_input:
            self.layout.alert = True
            self.layout.label(text=self.input_error_msg)
        self.layout.alert = False
        self.layout.prop(self, "render_frames")
        row = self.layout.row()
        row.alignment = 'RIGHT'
        row.prop(self, "open_render_dir")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

    def execute(self, context):
        self.validate_input(context)
        if self.invalid_input:
            return context.window_manager.invoke_props_dialog(self, width=400)

        split_sep = ","
        input: str = self.render_frames

        # clean user input
        input = input.replace(" ", "")
        for sep in self.alternative_seps:
            input = input.replace(sep, split_sep)
        frames_str = input.split(split_sep)
        frames_str = set(frames_str)
        if "" in frames_str:
            frames_str.remove("")

        frames_int = [int(frame) for frame in frames_str]

        if len(frames_int) < 1:
            log.report(self, log.Severity.ERROR, f"Could not extract valid frames from input")
            return {'CANCELLED'}

        frames_int.sort(reverse=True)

        initially_in_camview = context.area.spaces[0].region_3d.view_perspective == 'CAMERA'
        initial_overlay_setting = context.space_data.overlay.show_overlays
        initial_shading_type = context.space_data.shading.type
        initial_frame = context.scene.frame_current
        initial_path = context.scene.render.filepath

        render_dir = initial_path[0:initial_path.rindex(os.sep)]
        filename = bpy.data.filepath[bpy.data.filepath.rindex(os.sep):-6]

        def number_to_str_with_leading_char(number: int, leading_char: str, leading_count: int) -> str:
            return f"{''.join(leading_char for i in range(0, max(0, leading_count - len(str(number)))))}{number}"

        def _initialze_settings():
            context.scene.frame_current = initial_frame
            context.scene.render.filepath = initial_path
            context.space_data.overlay.show_overlays = initial_overlay_setting
            context.space_data.shading.type = initial_shading_type
            if not initially_in_camview:
                bpy.ops.view3d.view_camera()

        if not initially_in_camview:
            bpy.ops.view3d.view_camera()
        context.space_data.overlay.show_overlays = False
        context.space_data.shading.type = 'RENDERED'
        for frame in frames_int:
            if frame not in range(context.scene.frame_start, context.scene.frame_end + 1):
                _initialze_settings()
                log.report(self, log.Severity.ERROR, f"Frame {frame} is not in sequence range!")
                return {'CANCELLED'}

            context.scene.frame_set(frame)
            new_output_path = f"{render_dir}{os.sep}{filename}_frame{number_to_str_with_leading_char(frame, '0', 5)}"
            context.scene.render.filepath = new_output_path
            bpy.ops.render.opengl(write_still=True)

        _initialze_settings()

        msg = f"Frames {''.join(str(frame) + ', ' for frame in frames_int)[:-2]} exported to {render_dir}"
        log.report(self, log.Severity.INFO, msg)

        if self.open_render_dir:
            os.startfile(render_dir)

        return {'FINISHED'}


classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)


def register():
    for c in classes:
        if "FTB_" not in c[0]:
            continue
        bpy.utils.register_class(globals()[c[0]])


def unregister():
    for c in reversed(classes):
        if "FTB_" not in c[0]:
            continue
        bpy.utils.unregister_class(globals()[c[0]])
