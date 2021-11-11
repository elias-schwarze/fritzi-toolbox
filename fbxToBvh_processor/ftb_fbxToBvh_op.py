import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.types import OperatorFileListElement
from bpy.props import BoolProperty, CollectionProperty, StringProperty


class FTB_OT_BatchFbxBvh_Op(Operator, ImportHelper):
    bl_idname = "object.batch_fbx_bvh"
    bl_label = "Batch export"
    bl_description = "Batch process all selected "
    bl_options = {"REGISTER", "UNDO"}

    # Collection Property accessed by ImportHelper to store all selected File filepaths in
    files: CollectionProperty(
        name="FilePaths", type=OperatorFileListElement)

    # String Property accessed by ImportHelper to store directory path of selected files
    directory: StringProperty(subtype='DIR_PATH')

    # list of properties to be displayed in the ImportHelper sidebar
    # sOutputPath: StringProperty(
    #     subtype='DIR_PATH', name="Output path")

    # use_setting: BoolProperty(
    #     name="Example Boolean",
    #     description="Example Tooltip",
    #     default=True,
    # )

    # should only work in object mode
    @classmethod
    def poll(cls, context):
        obj = context.object
        wm = bpy.context.window_manager

        if (wm.bvhOutputPath == ""):
            return False

        if not obj:
            return True

        if obj:
            if obj.mode == "OBJECT":
                return True
        return False

    def execute(self, context):

        wm = bpy.context.window_manager

        if (not wm.bvhOutputPath):
            self.report({'WARNING'}, 'Output path is not set')
            return {'CANCELLED'}

        if (not self.files):
            self.report({'WARNING'}, "No files selected")
            return{'CANCELLED'}

        else:
            for file in self.files:
                if file.name == "":
                    self.report({'WARNING'}, "No files selected")
                    return{'CANCELLED'}

        objectList = list()

        for obj in bpy.context.collection.all_objects:
            objectList.append(obj)

        # list to keep track of already imported rigs between each single import, so that we can find out the newest imported file
        tempRigList = list()

        # list to keep track of already imported objects between each single import, so that we can find newest object and modify it
        tempObjList = list()

        # single object that is currently being processed to bvh
        tempObj: bpy.types.Object

        # object list to contain all objects that are present in scene before import starts
        for obj in bpy.context.collection.all_objects:
            tempObjList.append(obj)

        wm = bpy.context.window_manager

        bpy.context.scene.frame_set(1)

        for file in self.files:

            # import fbx file using the filepath from ImportHelper, set automatic bone orientation to true)
            bpy.ops.import_scene.fbx(filepath=(self.directory + file.name), global_scale=100,
                                     use_image_search=False, automatic_bone_orientation=True)

            for obj in bpy.context.collection.all_objects:
                if (not obj in tempObjList) and (obj.type == 'ARMATURE'):
                    obj.name = file.name[:-4]
                    endFrame = obj.animation_data.action.frame_range[1]

                    tempObjList.append(obj)
                    tempRigList.append(obj)

                    bpy.context.view_layer.objects.active = obj

                    bpy.ops.export_anim.bvh(
                        filepath=(wm.bvhOutputPath + obj.name + ".bvh"), frame_start=1, frame_end=endFrame)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(FTB_OT_BatchFbxBvh_Op)


def unregister():
    bpy.utils.unregister_class(FTB_OT_BatchFbxBvh_Op)
