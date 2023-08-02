# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from . import ftb_prefs, addon_updater_ops
from .previews import ftb_previews_pnl, ftb_previews_op
from .checking import ftb_objectChecking_pnl, ftb_objectChecking_op
from .data_editing import ftb_dataEditing_pnl, ftb_dataEditing_op, ftb_gnodesMaterialReplacer_op
from .checking import ftb_objectChecking_pnl, ftb_objectChecking_op, ftb_renderChecking_pnl, ftb_renderChecking_op
from .data_editing import ftb_dataEditing_pnl, ftb_dataEditing_op, ftb_gnodesMaterialReplacer_op
from .danger_zone import ftb_danger_zone_pnl, ftb_danger_zone_op
from .batch_rotator import ftb_rotator_pnl, ftb_rotator_op
from .burn_in_render import ftb_burnInRender_pnl, ftb_burnInRender_op
from .default_setup import ftb_default_lineart_op, ftb_default_render_settings_op, ftb_defaultDisplace_op, ftb_default_setup_pnl
from .fbxToBvh_processor import ftb_fbxToBvh_op, ftb_fbxToBvh_pnl
from .index_override_remover import ftb_index_override_remover_op
from .ue_export import ftb_ueexport_op, ftb_ueexport_pnl, ftb_unreal_char_op
from .material_helper import ftb_materialhelper_op, ftb_materialhelper_pnl
from .prop_rigid_rig import ftb_prop_rigid_rig_op, ftb_prop_rigid_rig_pnl
from .alerts import ftb_alerts_op
from .animation_editing import ftb_animation_editing_op, ftb_animation_editing_pnl

bl_info = {
    "name": "fritziToolbox",
    "author": "Elias Schwarze, Robert Lehmann",
    "description": "A suite of tools for the Fritzi Project",
    "blender": (3, 3, 0),
    "version": (1, 16, 3),
    "location": "3D Viewport > Properties panel (N) > FTB Tab",
    "category": "Object"
}

classes = (ftb_prefs,
           ftb_previews_op, ftb_previews_pnl,
           ftb_objectChecking_op, ftb_objectChecking_pnl, ftb_renderChecking_pnl, ftb_renderChecking_op,
           ftb_dataEditing_op, ftb_dataEditing_pnl, ftb_gnodesMaterialReplacer_op,
           ftb_danger_zone_op, ftb_danger_zone_pnl,
           ftb_rotator_op, ftb_rotator_pnl,
           ftb_burnInRender_op, ftb_burnInRender_pnl,
           ftb_defaultDisplace_op, ftb_default_lineart_op, ftb_default_render_settings_op, ftb_default_setup_pnl,
           ftb_fbxToBvh_op, ftb_fbxToBvh_pnl,
           ftb_index_override_remover_op,
           ftb_ueexport_op, ftb_unreal_char_op, ftb_ueexport_pnl,
           ftb_materialhelper_op, ftb_materialhelper_pnl,
           ftb_prop_rigid_rig_op, ftb_prop_rigid_rig_pnl,
           ftb_alerts_op,
           ftb_animation_editing_op, ftb_animation_editing_pnl
           )


def register():

    addon_updater_ops.register(bl_info)

    for c in classes:
        c.register()


def unregister():

    for c in reversed(classes):
        c.unregister()

    addon_updater_ops.unregister()
