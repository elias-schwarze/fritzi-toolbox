import bpy
import time

from bpy.types import Operator, NlaStrip, NlaTrack
from .. utility_functions import ftb_logging as log

CLEANED_STRIP_SUFFIX = "_cleaned"


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
            cls.poll_message_set("No active strip selected")
            return False

        active_strip_belong_to_active_object = context.active_object == context.active_nla_strip.id_data
        if not active_strip_belong_to_active_object:
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

        with context.temp_override(area=ctx.viewport):
            try:
                bpy.ops.pose.select_all(action='SELECT')
            except:
                log.report(self, log.Severity.ERROR, "Failed selecting rig controls")
                return {'CANCELLED'}

        with context.temp_override(area=ctx.nla_ed):
            if not context.scene.is_nla_tweakmode:
                bpy.ops.nla.tweakmode_enter(use_upper_stack_evaluation=False)

            with context.temp_override(area=ctx.graph_ed):
                try:
                    bpy.ops.graph.select_all(action='SELECT')
                except:
                    log.report(self, log.Severity.ERROR, "Failed selecting graphs")
                    return {'CANCELLED'}

                try:
                    bpy.ops.graph.smooth()
                    bpy.ops.graph.clean(channels=False)
                except:
                    log.report(self, log.Severity.ERROR, ("Cleaning and smoothing step failed. Check if curves or rig"
                                                          " controls are locked."))
                    return {'CANCELLED'}

            bpy.ops.nla.tweakmode_exit()

        log.report(self, log.Severity.INFO, f"NLA-Strip: '{strip.name}' successfully cleaned")
        if not strip.name.endswith(CLEANED_STRIP_SUFFIX):
            strip.name += CLEANED_STRIP_SUFFIX
        return {'FINISHED'}


class FTB_OT_BatchPrepareNLAStrip_OP(Operator):
    bl_idname = "nla.ftb_batch_prepare_strips"
    bl_label = "Prepare Selected Strips"
    bl_description = ("Prepares selected strips for Fritzi animations. Disables 'Sync Length', performs 'Smooth Keys'"
                      " and 'Clean Keyframes' automatically on selected strips")
    bl_options = {'REGISTER', 'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if not context.mode == 'POSE':
            cls.poll_message_set("Active object must be in 'POSE' mode")
            return False
        if not len(context.selected_nla_strips) > 1:
            cls.poll_message_set("Select at least 2 strips")
            return False

        selected_strips_belong_to_active_object = True

        for strip in context.selected_nla_strips:
            selected_strips_belong_to_active_object &= (context.active_object == strip.id_data)
        if not selected_strips_belong_to_active_object:
            cls.poll_message_set("All selected strips must belong to the active object")
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

    def get_nla_track_from_strip(self, nla_strip: NlaStrip) -> NlaTrack:
        for track in bpy.context.active_object.animation_data.nla_tracks:
            for strip in track.strips:
                if strip == nla_strip:
                    return track

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.alert = True
        layout.label(text="ATTENTION!")
        layout.label(text="This operation tends to crash Blender!")
        layout.label(text="Please make sure to save your progress before pressing OK.")
        layout.label(text="Press [ESC] to Cancel.")
        layout.alert = False

    def execute(self, context):
        # hack to batch process strips since you can't set an active strip via python (strip.active is read-only):

        #
        # creates a new temporary NLA-Track
        # copy strip to new temp nla-track to make it active
        # performs cleaning operations
        # copy strip back to original NLA-Track
        # repeat...

        number_of_strips = len(context.selected_nla_strips)

        with context.temp_override(area=ctx.viewport):
            try:
                bpy.ops.pose.select_all(action='SELECT')
            except:
                log.report(self, log.Severity.ERROR, "Failed selecting rig controls")
                return {'CANCELLED'}

        temp_track = context.active_object.animation_data.nla_tracks.new(prev=None)
        temp_track.name = "temp_track"

        for strip in context.selected_nla_strips:
            _action = strip.action
            _original_track: NlaTrack = self.get_nla_track_from_strip(strip)

            _copy_strip_temp = temp_track.strips.new(_action.name, int(strip.frame_start_ui), _action)
            _copy_strip_temp.frame_end_ui = strip.frame_end_ui
            _strip_name = _copy_strip_temp.name
            _original_track.strips.remove(strip)
            _copy_strip_temp.name = _strip_name

            _copy_strip_temp.use_sync_length = False

            def cleanup(remove_temp_nla_track: bool = True):
                _copy_strip_back = _original_track.strips.new(
                    _action.name, int(_copy_strip_temp.frame_start_ui), _action)
                _copy_strip_back.frame_end_ui = _copy_strip_temp.frame_end_ui
                _copy_strip_back.use_sync_length = False
                _copy_strip_back.name = _strip_name
                temp_track.strips.remove(_copy_strip_temp)

                if remove_temp_nla_track:
                    context.active_object.animation_data.nla_tracks.remove(temp_track)
                else:
                    if not _copy_strip_back.name.endswith(CLEANED_STRIP_SUFFIX):
                        _copy_strip_back.name += CLEANED_STRIP_SUFFIX

            with context.temp_override(area=ctx.nla_ed):
                if not context.scene.is_nla_tweakmode:
                    bpy.ops.nla.tweakmode_enter(use_upper_stack_evaluation=False)

                with context.temp_override(area=ctx.graph_ed):
                    try:
                        bpy.ops.graph.select_all(action='SELECT')
                    except:
                        log.report(self, log.Severity.ERROR, f"Failed selecting graphs for '{_copy_strip_temp.name}'")
                        cleanup()
                        return {'CANCELLED'}

                    try:
                        bpy.ops.graph.smooth()
                        bpy.ops.graph.clean(channels=False)
                        log.console(self, log.Severity.INFO,
                                    f"NLA-Strip: '{_copy_strip_temp.name}' successfully cleaned")
                    except:
                        log.report(self, log.Severity.ERROR, (f"Cleaning and smoothing step failed for "
                                                              f"'{_copy_strip_temp.name}'. Check if curves or rig"
                                                              f" controls are locked."))
                        cleanup()
                        return {'CANCELLED'}

                time.sleep(0.5)  # necessary to prevent crashes during view layer updates called by tweakmode_exit()
                bpy.ops.nla.tweakmode_exit()
            cleanup(False)
        context.active_object.animation_data.nla_tracks.remove(temp_track)
        log.report(self, log.Severity.INFO, f"Successfully cleaned {number_of_strips} strips")
        return {'FINISHED'}


classes = (FTB_OT_PrepareNLAStrip_OP, FTB_OT_BatchPrepareNLAStrip_OP)


def register():
    for c in classes:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
