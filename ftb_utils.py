import bpy
from bpy import context
import random
from math import radians, degrees
import string

# function to return a random float (in radian unit) between the range of minRot and maxRot 
def ftb_random_rotation(minRot = 0.0, maxRot = 0.0, randomizeDirection = True):

    randomRot = random.uniform(minRot, maxRot)

    if (randomizeDirection == True):
            if(random.getrandbits(1) == True):
                randomRot*= -1
        
    return radians(randomRot)


def world_to_basis(active, obj):
    """put world coords of active as basis coords of obj"""
    local = obj.parent.matrix_world.inverted() @ active.matrix_world
    P = obj.matrix_basis @ obj.matrix_local.inverted()
    mat = P @ local
    return(mat)


#copy visual location from sourceObj to obj
def obCopyVisLoc(obj, sourceObj):
    if obj.parent:
        mat = world_to_basis(sourceObj, obj)
        obj.location = mat.to_translation()
    else:
        obj.location = sourceObj.matrix_world.to_translation()

#copy visual rotation from sourceObj to obj
def obCopyVisRot(obj, sourceObj):
    if obj.parent:
        mat = world_to_basis(sourceObj, obj)
        rotcopy(obj, mat.to_3x3())
    else:
        rotcopy(obj, sourceObj.matrix_world.to_3x3())

#copy visual Scale from sourceObj to obj
def obCopyVisSca(obj, sourceObj):
    if obj.parent:
        mat = world_to_basis(sourceObj, obj)
        obj.scale = mat.to_scale()
    else:
        obj.scale = sourceObj.matrix_world.to_scale()


def rotcopy(item, mat):
    """Copy rotation to item from matrix mat depending on item.rotation_mode"""
    if item.rotation_mode == 'QUATERNION':
        item.rotation_quaternion = mat.to_3x3().to_quaternion()
    elif item.rotation_mode == 'AXIS_ANGLE':
        rot = mat.to_3x3().to_quaternion().to_axis_angle()    # returns (Vector((x, y, z)), w)
        axis_angle = rot[1], rot[0][0], rot[0][1], rot[0][2]  # convert to w, x, y, z
        item.rotation_axis_angle = axis_angle
    else:
        item.rotation_euler = mat.to_3x3().to_euler(item.rotation_mode)


# strip trailing numbers and dot from string, if any
def stripEndNumbers(inputString):
    if ("." in inputString[-4:] and any(i.isdigit() for i in inputString[-4:])):
        return inputString[:-4]

    else: return inputString
