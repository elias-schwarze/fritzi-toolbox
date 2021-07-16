import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.types import OperatorFileListElement
from bpy.props import BoolProperty, CollectionProperty
from bpy.props import StringProperty

from math import radians

import re


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
    bpy.utils.register_class(FTB_OT_Preview_Import_Op)
    bpy.utils.register_class(FTB_OT_Preview_Reload_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_Preview_Reload_Op)
    bpy.utils.unregister_class(FTB_OT_Preview_Import_Op)
