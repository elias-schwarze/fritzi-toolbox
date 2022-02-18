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

from . import ftb_prefs
from . import addon_updater_ops

from .previews import ftb_previews_pnl
from .previews import ftb_previews_op

from .object_checking import ftb_objectChecking_pnl
from .object_checking import ftb_objectChecking_op

from .data_editing import ftb_dataEditing_pnl
from .data_editing import ftb_dataEditing_op

from .danger_zone import ftb_danger_zone_pnl
from .danger_zone import ftb_danger_zone_op

from .batch_rotator import ftb_rotator_pnl
from .batch_rotator import ftb_rotator_op

from .burn_in_render import ftb_burnInRender_pnl
from .burn_in_render import ftb_burnInRender_op

from .displacement_tools import ftb_displaceTools_op
from .displacement_tools import ftb_displaceTools_pnl

from .default_setup import ftb_default_lineart_op
from .default_setup import ftb_default_render_settings_op
#from .default_setup import ftb_default_comp_setup_op
#from .default_setup import ftb_default_comp_setup_pnl
from .default_setup import ftb_default_setup_pnl

from .fbxToBvh_processor import ftb_fbxToBvh_op
from .fbxToBvh_processor import ftb_fbxToBvh_pnl

from .index_override_remover import ftb_index_override_remover_op


bl_info = {
    "name": "fritziToolbox",
    "author": "Elias Schwarze, Robert Lehmann",
    "description": "A suite of tools for the Fritzi Project",
    "blender": (3, 0, 0),
    "version": (0, 3, 0),
    "location": "3D Viewport > Properties panel (N) > FTB Tab",
    "category": "Object"
}


def register():

    ftb_prefs.register()
    addon_updater_ops.register(bl_info)

    ftb_rotator_op.register()
    ftb_rotator_pnl.register()

    ftb_dataEditing_op.register()
    ftb_dataEditing_pnl.register()

    ftb_danger_zone_op.register()
    ftb_danger_zone_pnl.register()

    ftb_objectChecking_op.register()
    ftb_objectChecking_pnl.register()

    ftb_previews_op.register()
    ftb_previews_pnl.register()

    ftb_burnInRender_op.register()
    ftb_burnInRender_pnl.register()

    ftb_displaceTools_op.register()
    ftb_displaceTools_pnl.register()

    ftb_default_lineart_op.register()
    ftb_default_render_settings_op.register()
    ftb_default_setup_pnl.register()
    # ftb_default_comp_setup_op.register()
    # ftb_default_comp_setup_pnl.register()

    ftb_fbxToBvh_op.register()
    ftb_fbxToBvh_pnl.register()

    ftb_index_override_remover_op.register()


def unregister():

    # should be in reverse order of register()

    ftb_index_override_remover_op.unregister()

    ftb_fbxToBvh_pnl.unregister()
    ftb_fbxToBvh_op.unregister()

    # ftb_default_comp_setup_pnl.unregister()
    # ftb_default_comp_setup_op.unregister()
    ftb_default_setup_pnl.unregister()
    ftb_default_render_settings_op.unregister()
    ftb_default_lineart_op.unregister()

    ftb_displaceTools_pnl.unregister()
    ftb_displaceTools_op.unregister()

    ftb_burnInRender_pnl.unregister()
    ftb_burnInRender_op.unregister()

    ftb_previews_pnl.unregister()
    ftb_previews_op.unregister()

    ftb_objectChecking_pnl.unregister()
    ftb_objectChecking_op.unregister()

    ftb_danger_zone_op.unregister()
    ftb_danger_zone_pnl.unregister()

    ftb_dataEditing_pnl.unregister()
    ftb_dataEditing_op.unregister()

    ftb_rotator_pnl.unregister()
    ftb_rotator_op.unregister()

    addon_updater_ops.unregister()
    ftb_prefs.unregister()
