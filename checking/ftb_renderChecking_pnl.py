import bpy
from .ftb_renderChecking_op import FTB_OT_RenderCheckRefresh_op
from .ftb_renderCheckData import RenderCheckData

finalSettings = RenderCheckData()


class FTB_PT_Render_Checking_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Render Checking"
    bl_category = "FTB"

    bpy.types.WindowManager.ftbRenderOnlyShowErrors = bpy.props.BoolProperty(
        name="Show Only Warnings",
        default=False)

    def draw(self, context):
        fs = finalSettings
        onlyErrors = bpy.context.window_manager.ftbRenderOnlyShowErrors

        layout = self.layout
        col = layout.column()
        col.operator("scene.default_render_settings")
        col.separator()
        col.operator("utils.render_check_refresh", icon='FILE_REFRESH')
        col.prop(context.window_manager, "ftbRenderOnlyShowErrors")

        if FTB_OT_RenderCheckRefresh_op.ranOnce:
            if bpy.context.scene.ftbCurrentRenderSettings:
                cs = bpy.context.scene.ftbCurrentRenderSettings

                # RESOLUTION
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
                        box.operator("utils.render_check_set_settings", text="Set Final Resolution").resFps = True

                # SAMPLES
                if (onlyErrors and not cs.matchSamples(matchData=fs)) or not onlyErrors:

                    sampleText = cs.getSamplesText()
                    box = layout.box()

                    if not cs.matchSamples(matchData=fs):
                        box.label(text=sampleText, icon='ERROR')
                    else:
                        box.label(text=sampleText)

                    # Display operator to change settings if they do not match final settings
                    if not cs.matchSamples(matchData=fs):
                        box.operator("utils.render_check_set_settings", text="Set Render Samples").samples = True

                # SHADOWS
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

                # AMBIENT OCCLUSION
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

                # OUTPUT FORMAT
                if (onlyErrors and not cs.matchOutput(matchData=fs)) or not onlyErrors:
                    outText = cs.getOutParamsText()
                    box = layout.box()

                    if not cs.matchOutput(matchData=fs):
                        box.label(text="Output: ", icon='ERROR')
                    else:
                        box.label(text="Output: ")

                    box.label(text=outText[0])
                    box.label(text=outText[1])
                    box.label(text=outText[2])

                    # Display operator to change settings if they do not match final settings
                    if not cs.matchOutput(matchData=fs):
                        box.operator("utils.render_check_set_settings", text="Set Final Output").outparams = True

                # BOOLEANS
                if cs.invalidBoolObjects:
                    box = layout.box()
                    box.label(text=(str(len(cs.invalidBoolObjects)) + " Boolean Issues"), icon='ERROR')
                    for obj in cs.invalidBoolObjects:
                        box.label(text=obj.name_full)
                    box.operator("utils.select_boolean_errors")

                # NLA + ACTIVE ACTION
                if cs.invalidNlaObjects:
                    box = layout.box()
                    box.label(text=(str(len(cs.invalidNlaObjects)) + " NLA issues"), icon='ERROR')
                    for name in cs.invalidNlaObjects:
                        box.label(text=name)

                # DATA TRANSFER MODIFIERS
                if cs.invalid_data_transfer_objects:
                    box = layout.box()
                    box.label(text=(f"{len(cs.invalid_data_transfer_objects)} Data Transfer Issues"), icon='ERROR')
                    for obj in cs.invalid_data_transfer_objects:
                        box.label(text=obj.name_full)
                    box.operator("utils.select_data_transfer_errors")

                # BURN IN
                if cs.isBurnInActive:
                    box = layout.box()
                    box.label(text="Burn In is active!", icon='ERROR')
                    box.operator("utils.render_check_set_settings", text="Disable Burn In").burnIn = True

                # ONLY 1 VIEW LAYER
                if cs.totalViewLayerCount == 1:
                    box = layout.box()
                    box.label(text="Only 1 view layer exists", icon='ERROR')

                # RENDER SINGLE LAYER ACTIVE
                if cs.render_single_layer:
                    box = layout.box()
                    box.label(text="\"Render Single Layer active\"", icon='ERROR')
                    # Display operator to change settings if they do not match final settings
                    box.operator("utils.render_check_set_settings",
                                 text="Disable Render Single Layer").renderSingleLayer = True

                # VIEW LAYER ACTIVE COUNT SMALLER THAN TOTAL COUNT
                if cs.activeViewLayerCount < cs.totalViewLayerCount:
                    box = layout.box()
                    box.label(text="Not all view layers active", icon='ERROR')

                # COLOR MANAGEMENT SETTINGS
                if (onlyErrors and not cs.matchColorMangement(matchData=fs)) or not onlyErrors:
                    # build string to show resolution & framerate settings
                    cmText = cs.getCmText()

                    box = layout.box()

                    if not cs.matchColorMangement(matchData=fs):
                        box.label(text="Color Management:", icon='ERROR')
                    else:
                        box.label(text="Color Management:")

                    box.label(text=cmText[0])
                    box.label(text=cmText[1])

                    # Display operator to change settings if they do not match final settings
                    if not cs.matchColorMangement(matchData=fs):
                        box.operator("utils.render_check_set_settings",
                                     text="Set Final Color Settings").colorMangement = True

                # RENDER SINGLE LAYER ACTIVE
                if not cs.film_transparent:
                    box = layout.box()
                    box.label(text="Background not transparent", icon='ERROR')
                    # Display operator to change settings if they do not match final settings
                    box.operator("utils.render_check_set_settings", text="Enable Transparency").filmTransparent = True

                # AOVS
                if not cs.matchAovs(matchData=fs):
                    box = layout.box()
                    box.label(text="Some AOVs missing", icon='ERROR')
                    box.operator("utils.render_check_set_settings", text="Add Missing AOVs").aovs = True

                # output not on network path
                if not cs.uncOutput:
                    box = layout.box()
                    box.label(text="Output path is not UNC", icon='ERROR')


def register():
    bpy.types.Scene.ftbCurrentRenderSettings = RenderCheckData()
    bpy.utils.register_class(FTB_PT_Render_Checking_Panel)


def unregister():
    bpy.utils.unregister_class(FTB_PT_Render_Checking_Panel)
    del bpy.types.Scene.ftbCurrentRenderSettings
