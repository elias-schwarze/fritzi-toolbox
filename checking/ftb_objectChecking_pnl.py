import bpy
import bpy.utils

from bpy.types import Panel
from . import Asset


def PluralizeString(ObjectCount: int):
    return (("", "s")[ObjectCount > 1])


def InitializeCheck():
    Asset.bChecked = False
    bpy.context.window_manager.bNormalsButtonClicked = False
    bpy.context.window_manager.bNormalsChecked = False


def UpdatePropEmptyReference(self, context):
    empty = context.window_manager.PropEmptyReference
    if empty:
        if not Asset.IsPropEmpty(empty):
            context.window_manager.PropEmptyReference = None
    InitializeCheck()


def UpdatePropCollectionReference(self, context):
    collection = context.window_manager.PropCollectionReference
    if collection:
        if collection.library or collection.override_library:
            context.window_manager.PropCollectionReference = None
    InitializeCheck()


class FTB_PT_Checking_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Object Checking"
    bl_category = "FTB"

    bpy.types.WindowManager.bNormalsButtonClicked = bpy.props.BoolProperty(
        default=False
    )

    bpy.types.WindowManager.bNormalsChecked = bpy.props.BoolProperty(
        default=False
    )

    bpy.types.WindowManager.PropCollectionReference = bpy.props.PointerProperty(
        type=bpy.types.Collection,
        name="",
        description="Prop Collection in this file. This will be used to scan for Prop errors",
        update=UpdatePropCollectionReference
    )

    bpy.types.WindowManager.PropEmptyReference = bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="",
        description="Prop Empty in this file. This will be used to scan for Prop errors",
        update=UpdatePropEmptyReference
    )

    def draw(self, context):

        def DrawErrorButton(ErrorList: list, OperatorString: str, Label: str):
            if ErrorList:
                ErrorCount = len(ErrorList)
                col.operator(OperatorString, text=str(ErrorCount) + " - " + Label + PluralizeString(ErrorCount))

        def DrawErrorHeader(ErrorCount: int, Label: str, Icon: str):
            col.separator(factor=2)
            col.label(text=str(ErrorCount) + " - " + Label + PluralizeString(ErrorCount), icon=Icon)

        wm = context.window_manager

        layout = self.layout
        col = layout.column()

        col.operator("utils.detect_prop_empty_collection")
        col.prop(wm, "PropCollectionReference")
        col.prop(wm, "PropEmptyReference")
        col.operator("utils.perform_asset_check")

        # continue only if we have a collection and empty and a Check has been performed
        if wm.PropCollectionReference and wm.PropEmptyReference and Asset.bChecked:

            # cancel if file has not been saved
            if not Asset.IsSaved():
                col.label(text="Please save .blend file!", icon='ERROR')
                return

            # cancel if recognized Empty Object is not an EMPTY
            if wm.PropEmptyReference.type != 'EMPTY':
                col.label(text="Empty Object Type not 'EMPTY'")
                return

            if Asset.HasFileErrors():
                DrawErrorHeader(Asset.GetFileErrorCount(), "File Error", 'FILE')

                if not Asset.IsFileInWorkspace():
                    col.operator("wm.save_file", text="File saved outside workspace!")

                if not Asset.bPropIDFileName:
                    col.operator("wm.save_file", text="Filename - Invalid Prop ID!")

                if not Asset.bProperFileName:
                    col.operator("wm.save_file", text="Filename - Invalid letters!")

                if not Asset.bFileIsClean:
                    col.operator("utils.clean_file", text="File unclean!")

            if Asset.HasCollectionErrors():
                DrawErrorHeader(Asset.GetCollectionErrorCount(), "Collection Error", 'OUTLINER_COLLECTION')

            if not wm.PropCollectionReference:
                col.label(text="Unable to find prop collection!")
            else:
                if not Asset.bEqualFileCollectionName:
                    col.operator("utils.change_collection_name", text="Name - Not Equal to Filename!")
                if not Asset.bPropIDCollectionName:
                    col.operator("utils.change_collection_name", text="Name - Invalid Prop ID!")
                if not Asset.bProperCollectionName:
                    col.operator("utils.change_collection_name", text="Name - Invalid letters!")

                if Asset.HasEmptyErrors():
                    DrawErrorHeader(Asset.GetEmptyErrorCount(), "Empty Error", 'OUTLINER_OB_EMPTY')

                    if not Asset.bEqualCollectonEmptyName:
                        col.operator("utils.changeemptyname", text="Name - Not Equal to Collection!")
                    if not Asset.bEqualFileEmptyName:
                        col.operator("utils.changeemptyname", text="Name - Not Equal to Filename!")
                    if not Asset.bPropIDEmptyName:
                        col.operator("utils.changeemptyname", text="Name - Invalid Prop ID!")
                    if not Asset.bProperEmptyName:
                        col.operator("utils.changeemptyname", text="Name - Invalid letters!")
                    if not Asset.bEmptyOnWorldOrigin:
                        col.operator("object.move_empty_to_origin", text="Not on World Origin!")

                if Asset.HasObjectErrors():
                    DrawErrorHeader(Asset.GetObjectErrorCount(), "Object Error", 'OUTLINER_OB_MESH')

                    DrawErrorButton(Asset.RogueObjectErrors, "object.show_rogues", "Invalid Object")
                    DrawErrorButton(Asset.InvalidNameErrors, "object.show_name_error", "Invalid Name")
                    DrawErrorButton(Asset.NGonErrors, "object.show_ngon_error", "NGon Error")
                    DrawErrorButton(Asset.ApplyScaleErrors, "object.show_scale_error", "Apply Scale Error")
                    DrawErrorButton(Asset.SubDLevelErrors, "object.show_subd_error", "SubD Level Error")
                    DrawErrorButton(Asset.DisplacementErrors, "object.show_displace_error", "Displacement Error")
                    DrawErrorButton(Asset.MissingSlotErrors, "object.show_missing_slot_error", "Missing Material Slot")
                    DrawErrorButton(Asset.SlotLinkErrors, "object.show_slot_link_error", "Material Link Error")
                    DrawErrorButton(Asset.UnusedSlotErrors, "object.show_unused_slot_error", "Unusued Material Slot")
                    DrawErrorButton(Asset.ParentingErrors, "object.show_parenting_error", "Parenting Error")

                errorsTotal = Asset.GetTotalErrorCount()
                col.separator(factor=2)
                if errorsTotal > 0:
                    col.alert = True
                    col.label(text=str(errorsTotal) + " Error" + PluralizeString(errorsTotal) + " found", icon='ERROR')
                    col.alert = False
                else:
                    col.label(text="No Errors found. Good Job!", icon='CHECKMARK')

                if Asset.HasNotifications():
                    DrawErrorHeader(Asset.GetTotalNotificationCount(), "Notification", 'INFO')

                    DrawErrorButton(Asset.ApplyRotNotification,
                                    "object.show_apply_rot_notification", "Unapplied Rotation")
                    DrawErrorButton(Asset.MissingDisplacementNotification,
                                    "object.show_displace_notify", "Missing Displacement")
                    DrawErrorButton(Asset.MissingShapeKeysNotification,
                                    "object.show_shape_key_notification", "Missing Shape Key")

            col.separator(factor=2)
            col.operator("view.toggle_face_orient", text="Toggle Normals Display")
            if wm.bNormalsButtonClicked:
                col.prop(wm, "bNormalsChecked", text="Normals OK?")

            if wm.bNormalsChecked and errorsTotal <= 0:
                col.label(text="All checks passed!", icon='CHECKMARK')
            elif not wm.bNormalsChecked:
                col.label(text="Normals not checked!", icon='ERROR')
            elif errorsTotal > 0:
                col.alert = True
                col.label(text="Asset still has errors!", icon='ERROR')
                col.alert = False

        else:
            InitializeCheck()


def register():
    bpy.utils.register_class(FTB_PT_Checking_Panel)
    pass


def unregister():
    bpy.utils.unregister_class(FTB_PT_Checking_Panel)
    pass
