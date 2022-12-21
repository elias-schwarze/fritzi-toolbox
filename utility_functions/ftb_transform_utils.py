import random
from math import radians


def ftb_random_rotation(minRot=0.0, maxRot=0.0, randomizeDirection=True):
    """Return a random float (in radian) between the range of minRot and maxRot"""
    randomRot = random.uniform(minRot, maxRot)

    if (randomizeDirection):
        if(random.getrandbits(1) is True):
            randomRot *= -1

    return radians(randomRot)


def world_to_basis(active, obj):
    """Put world coords of active as basis coords of obj"""
    local = obj.parent.matrix_world.inverted() @ active.matrix_world
    P = obj.matrix_basis @ obj.matrix_local.inverted()
    mat = P @ local
    return(mat)


def ob_Copy_Vis_Loc(obj, sourceObj):
    """Copy visual location from sourceObj to obj"""
    if obj.parent:
        mat = world_to_basis(sourceObj, obj)
        obj.location = mat.to_translation()
    else:
        obj.location = sourceObj.matrix_world.to_translation()


def ob_Copy_Vis_Rot(obj, sourceObj):
    """Copy visual rotation from sourceObj to obj"""
    if obj.parent:
        mat = world_to_basis(sourceObj, obj)
        rot_copy(obj, mat.to_3x3())
    else:
        rot_copy(obj, sourceObj.matrix_world.to_3x3())


def ob_Copy_Vis_Sca(obj, sourceObj):
    """Copy visual Scale from sourceObj to obj"""
    if obj.parent:
        mat = world_to_basis(sourceObj, obj)
        obj.scale = mat.to_scale()
    else:
        obj.scale = sourceObj.matrix_world.to_scale()


def rot_copy(item, mat):
    """Copy rotation to item from matrix mat depending on item.rotation_mode"""
    if item.rotation_mode == 'QUATERNION':
        item.rotation_quaternion = mat.to_3x3().to_quaternion()
    elif item.rotation_mode == 'AXIS_ANGLE':
        # returns (Vector((x, y, z)), w)
        rot = mat.to_3x3().to_quaternion().to_axis_angle()
        # convert to w, x, y, z
        axis_angle = rot[1], rot[0][0], rot[0][1], rot[0][2]
        item.rotation_axis_angle = axis_angle
    else:
        item.rotation_euler = mat.to_3x3().to_euler(item.rotation_mode)
