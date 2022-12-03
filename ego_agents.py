
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

<<<<<<< Updated upstream
=======
import carla
>>>>>>> Stashed changes

def findClosestSpawnPoint(spawn_points, target):
    dist = [(target.location.x-spawn_points[i].location.x)**2 + (target.location.y-spawn_points[i].location.y)**2 + (target.location.z-spawn_points[i].location.z)**2 for i in range(len(spawn_points))]
    return spawn_points[dist.index(min(dist))]


class EgoAgent:
    def __init__(self,world):
        self.world=world
        blueprint_library = world.get_blueprint_library()
        blueprintsVehicles = blueprint_library.filter('vehicle.*')
<<<<<<< Updated upstream
=======
        
>>>>>>> Stashed changes
        vehicles_spawn_points = world.get_map().get_spawn_points()
        self.ego_bp = random.choice(blueprint_library.filter('vehicle.*'))
        self.ego_bp.set_attribute('role_name','ego')
        test=random.choice(vehicles_spawn_points)
<<<<<<< Updated upstream
        print(test)
        
        self.ego = world.spawn_actor(self.ego_bp, findClosestSpawnPoint(spawn_points=vehicles_spawn_points, target=test))
        self.ego.set_autopilot(True)
=======
        #########
        cambp=blueprint_library.find('sensor.camera.rgb')
        cambp.set_attribute("image_size_x",str(1920))
        cambp.set_attribute("image_size_y",str(1080))
        cambp.set_attribute("fov",str(105))
        
        
        cam_location = carla.Location(2,0,1)
        cam_rotation = carla.Rotation(0,0,0)
        cam_transform = carla.Transform(cam_location,cam_rotation)
        
        
        ########
        
        
        
        
        
        self.ego = world.spawn_actor(self.ego_bp, findClosestSpawnPoint(spawn_points=vehicles_spawn_points, target=test))
        self.ego.set_autopilot(True)
        ego_cam = world.spawn_actor(cambp,cam_transform,attach_to=self.ego, attachment_type=carla.AttachmentType.Rigid)
        ego_cam.listen(lambda image: image.save_to_disk('tutorial/output/%.6d.jpg' % image.frame))
        print("Step passed")
        world.tick()
        
>>>>>>> Stashed changes
        self.queues = []
        q = queue.Queue()
        world.on_tick(q.put)
        self.queues.append(q)
 