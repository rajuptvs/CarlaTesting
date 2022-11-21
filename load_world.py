import random
import glob
import os
import sys
import time
##############
## This is used to load the path for the carla library
##############
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla
# Connect to the client and retrieve the world object


class test:
    def load_new_world(self):
        self.client = carla.Client('localhost', 2000)
        self.world = self.client.get_world()
        # print("World is ",world)
        self.client.load_world('Town03')