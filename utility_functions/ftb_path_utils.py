import bpy
import os
from addon_utils import check, paths


def get_all_addons(display=False):
    """
    Prints the addon state based on the user preferences.
    """

    # RELEASE SCRIPTS: official scripts distributed in Blender releases
    paths_list = paths()
    addon_list = []
    for path in paths_list:
        for mod_name, mod_path in bpy.path.module_names(path):
            is_enabled, is_loaded = check(mod_name)
            addon_list.append(mod_name)
            if display:  # for example
                print("%s default:%s loaded:%s" %
                      (mod_name, is_enabled, is_loaded))

    return(addon_list)


def is_fbx_enabled():
    """
    Returns True if the fbx importer addon is enabled and loaded.
    """

    paths_list = paths()
    for path in paths_list:
        for mod_name in bpy.path.module_names(path):

            if (mod_name == "io_scene_fbx"):
                is_enabled, is_loaded = check(mod_name)
                print("fbx" + is_loaded)
                if (is_loaded):
                    return True
                else:
                    return False


def is_bvh_enabled():
    """
    Returns True if the bvh importer addon is enabled and loaded.
    """

    paths_list = paths()
    for path in paths_list:
        for mod_name in bpy.path.module_names(path):
            if (mod_name == "io_anim_bvh"):
                is_enabled, is_loaded = check(mod_name)
                print("bvh" + is_loaded)
                if (is_loaded):
                    return True
                else:
                    return False


def getFritziPreferences():
    return bpy.context.preferences.addons[(__package__.split('.')[:-1])[0]].preferences


def getAbsoluteFilePath(filepath: str) -> str:
    """Gets absolute path of any given blender relative path.
    Works for every datablock that can have a relative source path, such as libraries and images.
    Returns: absolutePath: str"""

    return (os.path.realpath(bpy.path.abspath(filepath)))
