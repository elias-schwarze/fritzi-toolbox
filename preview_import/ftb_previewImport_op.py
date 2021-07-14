import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.types import OperatorFileListElement
from bpy.props import CollectionProperty
from bpy.props import StringProperty


class FTB_OT_Preview_Import_Op(Operator, ImportHelper):
    bl_idname = "object.preview_import"
    bl_label = "Import Previews"
    bl_description = "Import previews"
    bl_options = {"REGISTER", "UNDO"}

    # Collection Property accessed by ImportHelper to store all selected File filepaths in
    files: CollectionProperty(
        name="FilePaths", type=OperatorFileListElement)

    directory: StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        # bpy.data.images.load(filepath, check_existing=False)

        for file in self.files:
            print(self.directory + file.name)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_Preview_Import_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_Preview_Import_Op)
