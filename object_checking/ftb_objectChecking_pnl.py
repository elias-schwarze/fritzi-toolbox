import bpy
import bpy.utils
from bpy.types import Panel

from . import Asset

def PluralizeString(ObjectCount):
    return (("", "s")[ObjectCount > 1])

class FTB_PT_Checking_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Object Checking"
    bl_category = "FTB"

    bpy.types.WindowManager.bActiveCollectionOnly = bpy.props.BoolProperty(
        default=True)

    bpy.types.WindowManager.bIgnoreWithoutSlots = bpy.props.BoolProperty(
        default=False)

    bpy.types.WindowManager.PropCollectionOverride = bpy.props.PointerProperty(
        name = "",
        description = "Prop Collection in this file. This will be used to scan for Prop errors",
        type = bpy.types.Collection)
    bpy.types.WindowManager.PropEmptyOverride = bpy.props.PointerProperty(
        name = "",
        description = "Prop Empty in this file. This will be used to scan for Prop errors",
        type = bpy.types.Object)

    def draw(self, context):
        
        def DrawErrorButton(ErrorList, OperatorString, Label):
            if ErrorList:
                ErrorCount = len(ErrorList)
                col.operator(OperatorString, text = str(ErrorCount) + " - " + Label + PluralizeString(ErrorCount))

        wm = context.window_manager

        layout = self.layout
        col = layout.column()
        col.operator("view.toggle_face_orient", text="Toggle Face Orientation")
        
        col.operator("utils.detectpropemptycollection")
        col.prop(wm, "PropCollectionOverride")
        col.prop(wm, "PropEmptyOverride")

        # continue only if we have a collection and empty
        if wm.PropCollectionOverride and wm.PropEmptyOverride:

            # cancel if file has not been saved
            if not Asset.IsSaved():
                col.label(text = "Please save .blend file!", icon = 'ERROR')
                return

            # cancel if recognized Empty Object is not an EMPTY
            if wm.PropEmptyOverride.type != 'EMPTY':
                col.label(text = "Empty Object Type not 'EMPTY'")
                return

            col.operator("utils.performassetcheck")

            # cancel error display until an initial check has been performed
            if not Asset.bChecked:
                return

            if Asset.HasFileErrors():
                col.separator(factor = 2)
                col.label(text = "File Errors", icon = 'FILE')

                if not Asset.bFileInWorkspace:
                    col.alert = True
                    col.operator("wm.savefile", text="File saved outside workspace!")
                    col.alert = False

                if not Asset.bPropIDFileName:
                    col.operator("wm.savefile", text="Filename - Invalid Prop ID!")
                
                if not Asset.bProperFileName:
                    col.operator("wm.savefile", text="Filename - Invalid letters!")
                
                if not Asset.bFileInWorkspace:
                    col.label(text = "File unclean!")

            
            if Asset.HasCollectionErrors():
                col.separator(factor = 2)
                col.label(text = "Collection Errors", icon = 'OUTLINER_COLLECTION')

            if not Asset.PropCollection:
                col.label(text="Unable to find prop collection!")
            else:
                if not Asset.bEqualFileCollectionName:
                    col.operator("utils.changecollectionname", text="Name - Not Equal to Filename!")
                if not Asset.bPropIDCollectionName:
                    col.operator("utils.changecollectionname", text="Name - Invalid Prop ID!")
                if not Asset.bProperCollectionName:
                    col.operator("utils.changecollectionname", text="Name - Invalid letters!")

                if Asset.HasEmptyErrors():
                    col.separator(factor = 2)
                    col.label(text = "Empty Errors", icon = 'OUTLINER_OB_EMPTY')

                    if not Asset.bEqualCollectonEmptyName:
                        col.label(text="Name - Not Equal to Collection!")
                    if not Asset.bEqualFileEmptyName:
                        col.label(text="Name - Not Equal to Filename!")
                    if not Asset.bPropIDEmptyName:
                        col.label(text="Name - Invalid Prop ID!")
                    if not Asset.bProperEmptyName:
                        col.label(text="Name - Invalid letters!")
                    if not Asset.bEmptyOnWorldOrigin:
                        col.label(text="Not on World Origin!")

                if Asset.HasObjectErrors():
                    col.separator(factor = 2)
                    col.label(text = "Object Errors", icon = 'OUTLINER_OB_MESH')

                    DrawErrorButton(Asset.RogueObjectErrors, "object.showrogues", "Invalid Object")
                    DrawErrorButton(Asset.SubDLevelErrors, "object.showsubderror", "SubD Level Error")
                    DrawErrorButton(Asset.MissingDisplacementErrors, "object.showdisplaceerror", "Displacement Error")
                    DrawErrorButton(Asset.ApplyScaleErrors, "object.showscaleerror", "Apply Scale Error")
                    DrawErrorButton(Asset.NGonErrors, "object.showngonerror", "NGon Error")
                    DrawErrorButton(Asset.MissingSlotErrors, "object.showmissingsloterror", "Missing Material Slot")
                    DrawErrorButton(Asset.SlotLinkErrors, "object.showslotlinkerror", "Material Link Error")
                    DrawErrorButton(Asset.UnusedSlotErrors, "object.showunusedsloterror", "Unusued Material Slot")
                    DrawErrorButton(Asset.ParentingErrors, "object.showparentingerror", "Parenting Error")


            col.label(text="", icon='ERROR')
            col.label(text="", icon='CHECKMARK')

        # ######## OLD DRAW
        # layout = self.layout

        # col = layout.column()
        # col.operator("view.toggle_face_orient", text="Toggle Face Orientation")

        # col = layout.column(align=True)
        # col.label(text="Transform Checking")

        # col.operator("object.select_location_non_zero")

        # col.operator("object.select_rotation_non_zero")

        # col.operator("object.select_scale_non_one")
        # col.operator("object.select_scale_non_unform")

        # col = layout.column(align=True)
        # col.label(text="Origin")

        # col.operator("object.center_object")
        # col.operator("object.origin_to_cursor")

        # col = layout.column(align=True)
        # col.label(text="Mesh Checking")
        # col.operator("object.check_ngons").showPolys = False
        # col.operator("object.check_ngons",
        #              text="Check and Show Ngons").showPolys = True

        # col = layout.column()
        # col.label(text="Orphan Data:")

        # col = layout.column()
        # col.operator("object.find_orphaned_objects")

        # col = layout.column()
        # col.operator("image.find_orphan_textures")

        # col = layout.column()
        # col.label(text="Material Slots")

        # row = layout.row(align=True)
        # row.operator("object.validate_mat_slots")
        # row.prop(data=wm,
        #          property="bActiveCollectionOnly", toggle=True, icon_only=True, icon='OUTLINER_COLLECTION')

        # col = layout.column()
        # col.prop(wm,
        #          "bIgnoreWithoutSlots", text="Ignore Objects Without Slots")

def register():
    bpy.utils.register_class(FTB_PT_Checking_Panel)

def unregister():
    bpy.utils.unregister_class(FTB_PT_Checking_Panel)

