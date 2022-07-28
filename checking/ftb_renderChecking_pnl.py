import bpy
from . import ftb_renderChecking_op as renCheck
from bpy.types import Panel

finalSettings = renCheck.RenderCheckData()


class FTB_PT_Render_Checking_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Render Checking"
    bl_category = "FTB"

    

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.operator("utils.render_check_refresh", icon='FILE_REFRESH')

        if renCheck.FTB_OT_RenderCheckRefresh_op.ranOnce:
            if bpy.context.scene.ftbCurrentRenderSettings:
                currentSet = bpy.context.scene.ftbCurrentRenderSettings
                # build string to show resolution & framerate settings
                resText = (str(currentSet.resX) 
                    + " x " 
                    + str(currentSet.resY) 
                    + " x "
                    + str(currentSet.resPercent) 
                    + "% @ " 
                    + str(currentSet.framerate) + "fps")

                box = layout.box()
                box.label(text="Resolution:")
                box.label(text=resText)
                box.separator()

                # Objects with invalid Booleans
                if currentSet.invalidBoolObjects:
                    box.label(text= ("Found " + str(len(currentSet.invalidBoolObjects)) + " Bool Issues"), icon='ERROR')
                    for obj in currentSet.invalidBoolObjects:
                        if obj:
                            box.label(text=obj.name)

def register():
    bpy.types.Scene.ftbCurrentRenderSettings = renCheck.RenderCheckData()
    bpy.utils.register_class(FTB_PT_Render_Checking_Panel)

def unregister():
    bpy.utils.unregister_class(FTB_PT_Render_Checking_Panel)
    del bpy.types.Scene.ftbCurrentRenderSettings
