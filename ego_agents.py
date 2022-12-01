
import os
import sys
import time
import random
import glob
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import json
import queue


def findClosestSpawnPoint(spawn_points, target):
    dist = [(target.location.x-spawn_points[i].location.x)**2 + (target.location.y-spawn_points[i].location.y)**2 + (target.location.z-spawn_points[i].location.z)**2 for i in range(len(spawn_points))]
    return spawn_points[dist.index(min(dist))]


class EgoAgent:
    def __init__(self,world):
        self.world=world
        blueprint_library = world.get_blueprint_library()
        blueprintsVehicles = blueprint_library.filter('vehicle.*')
        vehicles_spawn_points = world.get_map().get_spawn_points()
        self.ego_bp = random.choice(blueprint_library.filter('vehicle.*'))
        self.ego_bp.set_attribute('role_name','ego')
        test=random.choice(vehicles_spawn_points)
        print(test)
        
        self.ego = world.spawn_actor(self.ego_bp, findClosestSpawnPoint(spawn_points=vehicles_spawn_points, target=test))
        self.ego.set_autopilot(True)
        self.queues = []
        q = queue.Queue()
        world.on_tick(q.put)
        self.queues.append(q)
 