import bpy

from bpy.types import Panel


def draw_op(self, context):
    layout = self.layout
    if len(bpy.context.selected_nla_strips) <= 1:
        layout.operator("nla.ftb_prepare_strip")
    else:
        layout.operator_context = 'INVOKE_DEFAULT'
        layout.operator("nla.ftb_batch_prepare_strips")


class FTB_PT_ViewLayerManagement_Panel(Panel):
    bl_label = "View Layer Management"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'
    bl_category = "FTB"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        pass


def register():
    bpy.types.NLA_MT_context_menu.append(draw_op)
    bpy.types.NLA_MT_edit.append(draw_op)


def unregister():
    bpy.types.NLA_MT_edit.remove(draw_op)
    bpy.types.NLA_MT_context_menu.remove(draw_op)
