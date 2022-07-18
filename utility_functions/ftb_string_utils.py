import os
import re
import bpy

OS_SEPARATOR = os.sep
PROPID_REGEX = "(hpr|pr|bg|vg)\d{1,}"
WORKSPACE_ROOT = "fritzi_serie"
WORKSPACE_FOLDERS = ["015_software", "020_tutorials", "030_material_fritzi_film", "040_rnd",
                     "050_production_design", "060_assets", "070_storyboard", "075_capture", "080_scenes"]
INVALID_CHARS = ["ä", "Ä", "ü", "Ü", "ö", "Ö", "ß", ":", ")", "("]


def strip_End_Numbers(inputString: str):
    """Strip trailing numbers and dot from string, if any"""
    if ("." in inputString[-4:] and any(i.isdigit() for i in inputString[-4:])):
        return inputString[:-4]

    else:
        return inputString


def is_name_duplicate(source: str, duplicate: str):
    """
    Returns True if the Duplicate and Source strings are identical except for the trailing numbering scheme added by blender. 
    e.g. name == name.001 == name.002
    but name.001 != name001
    """
    return strip_End_Numbers(source) == strip_End_Numbers(duplicate)


def asset_path_is_absolute(path: str):
    """
    Returns True if the blender internal file path does not begin with "//"
    """
    return len(path) > 1 and path[1] != "/"


def file_is_in_workspace():
    """
    Returns True if the file is saved within fritzi workspace.
    """
    is_saved = bpy.data.is_saved and bpy.data.filepath
    if not is_saved:
        return False

    if bpy.data.filepath.find(WORKSPACE_ROOT) != -1:
        return True

    for folder in WORKSPACE_FOLDERS:
        if bpy.data.filepath.find(folder) != -1:
            return True

    return False


def GetFilenameString():
    """Returns the filename of the current blend file without the '.blend' file ending"""
    return bpy.data.filepath[bpy.data.filepath.rindex(OS_SEPARATOR) + 1: -6]


def ContainsPropID(Name: str):
    """
    Return True if Name contains valid Fritzi PropID, otherwise False
    param Name: Name to check for valid PropID
    """
    match = re.search(PROPID_REGEX, Name)
    if not match:
        return False

    return True


def GetPropID(Name: str):
    """
    Returns Fritzi PropID string if Name contains it, otherwise None
    param Name: Name to check for valid PropID
    """
    match = re.search(PROPID_REGEX, Name)
    if match:
        return match.group()

    return None


def UsesInvalidChars(Name: str):
    """
    Returns True if Name contains invalid characters listed in constant INVALID_CHARS, otherwise False
    param Name: Name to check for invalid characters
    """
    umlaut = 0
    for char in INVALID_CHARS:
        umlaut += Name.find(char)

    # no special char found
    if umlaut == (len(INVALID_CHARS) * -1):
        return False

    return True


def ReplaceInvalidChars(Name: str):
    """
    Replaces all invalid characters listed in the constant INVALID_CHARS with appropriate characters
    param Name: Name to replace invalid characters
    """
    replacechars = ["ae", "AE", "ue", "UE", "oe", "OE", "ss", "", "", ""]

    if UsesInvalidChars(Name):
        for i in range(len(INVALID_CHARS)):
            Name = Name.replace(INVALID_CHARS[i], replacechars[i])
        return Name
    return Name
