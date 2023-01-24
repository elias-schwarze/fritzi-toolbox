import bpy

from bpy.types import Operator


class ctx:
    graph_ed: bpy.types.Area = None
    nla_ed: bpy.types.Area = None
    viewport: bpy.types.Area = None

    @classmethod
    def is_valid(self) -> bool:
        self.graph_ed = None
        self.nla_ed = None
        self.viewport = None
        for area in bpy.context.screen.areas:
            if area.type == "NLA_EDITOR":
                self.nla_ed = area
            elif area.type == "GRAPH_EDITOR":
                self.graph_ed = area
            elif area.type == 'VIEW_3D':
                self.viewport = area

        return self.nla_ed and self.graph_ed and self.viewport


class FTB_OT_PrepareNLAStrip_OP(Operator):
    bl_idname = "nla.ftb_prepare_strip"
    bl_label = "Prepare Active Strip"
    bl_description = ("Prepares the active strip for Fritzi animations. Disables 'Sync Length', performs 'Smooth Keys'"
                      " and 'Clean Keyframes' automatically on the active strip")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        cls.b_in_pose_mode = context.mode == 'POSE'
        if not context.mode == 'POSE':
            cls.poll_message_set("Active object must be in 'POSE' mode")
            return False
        if not context.active_nla_strip:
            return False

        selected_strips_belongs_to_active_object = context.active_object == context.active_nla_strip.id_data
        if not selected_strips_belongs_to_active_object:
            cls.poll_message_set("Active strip must belong to active object")
            return False

        is_valid_context = ctx.is_valid()
        missing_areas = []
        if not ctx.graph_ed:
            missing_areas.append("Graph-Editor")
        if not ctx.nla_ed:
            missing_areas.append("NLA-Editor")
        if not ctx.viewport:
            missing_areas.append("3D-Viewport")

        if not is_valid_context:
            areas_str = "".join(area + ", " for area in missing_areas)
            cls.poll_message_set(f"Need {areas_str[:-2]} window in workspace")
            return False

        return True

    def execute(self, context):
        strip = context.active_nla_strip
        strip.use_sync_length = False

        with context.temp_override(area=ctx.nla_ed):
            if not context.scene.is_nla_tweakmode:
                bpy.ops.nla.tweakmode_enter(use_upper_stack_evaluation=False)

            with context.temp_override(area=ctx.viewport):
                try:
                    bpy.ops.pose.select_all(action='SELECT')
                except:
                    self.report({'ERROR'}, "Bone selection failed")
                    return {'CANCELLED'}

            with context.temp_override(area=ctx.graph_ed):
                try:
                    bpy.ops.graph.select_all(action='SELECT')
                except:
                    self.report({'ERROR'}, "selection failed")
                    return {'CANCELLED'}

                try:
                    bpy.ops.graph.smooth()
                    bpy.ops.graph.clean(channels=False)
                except:
                    self.report({'ERROR'}, "Cleaning failed")
                    return {'CANCELLED'}

            bpy.ops.nla.tweakmode_exit()

        return {'FINISHED'}


class FTB_OT_BatchPrepareNLAStrip_OP(Operator):
    bl_idname = "nla.ftb_batch_prepare_strips"
    bl_label = "Prepare Selected Strips"
    bl_description = "YADA YADA"
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if not context.mode == 'POSE':
            return False
        if not len(context.selected_nla_strips) > 1:
            return False

        selected_strips_belongs_to_active_object = True

        for strip in context.selected_nla_strips:
            selected_strips_belongs_to_active_object &= (context.active_object == strip.id_data)

        return ctx.is_valid() and selected_strips_belongs_to_active_object

    def execute(self, context):
        return {'FINISHED'}

        # hack to batch process strips:
        # move strip to new temp nla-track to make it active?
        # perform operations
        # move back to original layer?
        # repeat?

        temp_track = context.active_object.animation_data.nla_tracks.new(prev=None)
        temp_track.name = "temp_track"

        _str = context.selected_nla_strips[0]
        eval(_str)

        for strip in context.selected_nla_strips:
            break
            _action = strip.action
            _track = strip.id_data.animation_data.ia
            #context.active_nla_strip = strip
            prepare_nla_strip(strip)

        context.active_object.animation_data.nla_tracks.remove(temp_track)
        return {'FINISHED'}


classes = (FTB_OT_PrepareNLAStrip_OP, FTB_OT_BatchPrepareNLAStrip_OP)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
