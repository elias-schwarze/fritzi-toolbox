import bpy
from bpy import context
import random
from math import radians, degrees


def ftb_random_rotation(randomizeDirection = True):
        
    wm = context.window_manager
    randomRot = random.uniform(wm.fMinRotation, wm.fMaxRotation)

    if (wm.bRandomRotDirection == True):
            if(random.getrandbits(1) == True):
                randomRot*= -1
        
    return radians(randomRot)