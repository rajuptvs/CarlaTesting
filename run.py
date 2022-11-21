import random
import glob
import os
import sys
import time
##############
## This is used to load the path for the carla library
##############
############
### 
# loading custom libraries
from load_world import test

####

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla

def main():
    world= test()
    world.load_new_world()

if __name__ == '__main__':
    main()