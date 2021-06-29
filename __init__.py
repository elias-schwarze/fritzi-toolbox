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

bl_info = {
    "name" : "fritziToolbox",
    "author" : "Elias Schwarze",
    "description" : "A suite of tools for the Fritzi Project",
    "blender" : (2, 93, 0),
    "version" : (0, 0, 4),
    "location" : "View3D",
    "warning" : "",
    "category" : "Object"
}

import bpy

from . ftb_op import *
from . ftb_pnl import *
from . ftb_rotator_op import *
from . ftb_rotator_pnl import *

classes = (
    FTB_OT_Apply_All_Op,
    FTB_PT_Checking_Panel,
    FTB_PT_DataClean_Panel,
    FTB_OT_Toggle_Face_Orient_Op,
    FTB_OT_RemoveMaterials_Op,
    FTB_OT_PurgeUnusedData_Op,
    FTB_OT_SetToCenter_Op,
    FTB_OT_OriginToCursor_Op,
    FTB_OT_CheckNgons_Op,
    FTB_OT_SelectScaleNonOne_Op,
    FTB_OT_SelectScaleNonUniform_Op,
    FTB_OT_CopyRotation_Op,
    FTB_PT_Rotator_Panel
    )

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in classes:
        bpy.utils.unregister_class(c)
