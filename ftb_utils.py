import bpy
from bpy import context
import random
from math import radians, degrees

# function to return 
def ftb_random_rotation(minRot = 0.0, maxRot = 0.0, randomizeDirection = True):

    randomRot = random.uniform(minRot, maxRot)

    if (randomizeDirection == True):
            if(random.getrandbits(1) == True):
                randomRot*= -1
        
    return radians(randomRot)