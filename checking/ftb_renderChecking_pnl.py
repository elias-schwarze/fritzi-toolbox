import bpy
from . import ftb_renderChecking_op as renCheck
from .ftb_renderCheckData import RenderCheckData
from bpy.types import Panel


finalSettings = RenderCheckData()

class FTB_PT_Render_Checking_Panel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Render Checking"
    bl_category = "FTB"

    bpy.types.WindowManager.ftbRenderOnlyShowErrors = bpy.props.BoolProperty(
        name="Show Only Errors",
        default=False)


    def draw(self, context):
        fs = finalSettings
        onlyErrors = bpy.context.window_manager.ftbRenderOnlyShowErrors

        layout = self.layout
        col = layout.column()
        col.operator("utils.render_check_refresh", icon='FILE_REFRESH')
        col.prop(context.window_manager, "ftbRenderOnlyShowErrors")

        if renCheck.FTB_OT_RenderCheckRefresh_op.ranOnce:
            if bpy.context.scene.ftbCurrentRenderSettings:
                cs = bpy.context.scene.ftbCurrentRenderSettings

                ### RESOLUTION
                if (onlyErrors and not cs.matchResFps(matchData=fs)) or not onlyErrors:
                    # build string to show resolution & framerate settings
                    resText = cs.getResText()

                    box = layout.box()

                    if not cs.matchResFps(matchData=fs):
                        box.label(text="Resolution:", icon='ERROR')
                    else:
                        box.label(text="Resolution:")


                    box.label(text=resText)
                    
                    # Display operator to change settings if they do not match final settings
                    if not cs.matchResFps(matchData=fs):
                        box.operator("utils.render_check_set_settings", text="Set Final Resolution"). resFps = True

                ### SHADOWS
                if (onlyErrors and not cs.matchShadows(matchData=fs)) or not onlyErrors:
                    # build string for shadow settings
                    sText = cs.getShadowsText()
                    box = layout.box()

                    if not cs.matchShadows(matchData=fs):
                        box.label(text="Shadows:", icon='ERROR')
                    else:
                        box.label(text="Shadows:")

                    box.label(text=sText[0])
                    box.label(text=sText[1])

                    # Display operator to change settings if they do not match final settings
                    if not cs.matchShadows(matchData=fs):
                        box.operator("utils.render_check_set_settings", text="Set Final Shadows").shadows = True

                ### AMBIENT OCCLUSION
                if (onlyErrors and not cs.matchAo(matchData=fs)) or not onlyErrors:
                    aoText = cs.getAoText()
                    box = layout.box()

                    if not cs.matchAo(matchData=fs):
                        box.label(text="Ambient Occlusion:", icon='ERROR')
                    else:
                        box.label(text="Ambient Occlusion:")

                    box.label(text=aoText[0])
                    box.label(text=aoText[1])
                    box.label(text=aoText[2])

                    # Display operator to change settings if they do not match final settings
                    if not cs.matchAo(matchData=fs):
                        box.operator("utils.render_check_set_settings", text="Set Final AO").ao = True

                ### OUTPUT FORMAT
                if (onlyErrors and not cs.matchOutput(matchData=fs)) or not onlyErrors:
                    outText = cs.getOutParamsText()
                    box = layout.box()

                    if not cs.matchOutput(matchData=fs):
                        box.label(text="Output: ", icon='ERROR')
                    else:
                        box.label(text="Output: ")

                    box.label(text= outText[0])
                    box.label(text= outText[1])
                    box.label(text= outText[2])

                    # Display operator to change settings if they do not match final settings
                    if not cs.matchOutput(matchData=fs):
                        box.operator("utils.render_check_set_settings", text="Set Final Output").outparams = True

                ### BOOLEANS
                if cs.invalidBoolObjects:
                    box = layout.box()
                    box.label(text= ("Found " + str(len(cs.invalidBoolObjects)) + " Boolean Issues"), icon='ERROR')
                    for name in cs.invalidBoolObjects:
                        box.label(text = name)
                        
                

def register():
    bpy.types.Scene.ftbCurrentRenderSettings = renCheck.RenderCheckData()
    bpy.utils.register_class(FTB_PT_Render_Checking_Panel)

def unregister():
    bpy.utils.unregister_class(FTB_PT_Render_Checking_Panel)
    del bpy.types.Scene.ftbCurrentRenderSettings
