import random
import glob
import os
import sys
import time
from ego_agents import EgoAgent

##############
## This is used to load the path for the carla library
##############
############
### 
# loading custom libraries


# from load_world import test

####
from spawn_actors import getVehicles,getWalkers
try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
print(sys.path)
import carla

def main():
    #initial settings
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    avail_maps = client.get_available_maps()
    world = client.load_world("Town02")
    blueprint_library = world.get_blueprint_library()
    settings = world.get_settings()
    settings.fixed_delta_seconds = 0.03
    settings.synchronous_mode = True
    world.set_pedestrians_cross_factor(0.0)
    world.apply_settings(settings)
    tm = client.get_trafficmanager(8000)
    tm.set_synchronous_mode(True)

    blueprintsVehicles = blueprint_library.filter('vehicle.*')
    vehicles_spawn_points = world.get_map().get_spawn_points()
    blueprintsWalkers = blueprint_library.filter('walker.pedestrian.*')
    walker_controller_bp = blueprint_library.find('controller.ai.walker')
    walkers_spawn_points = world.get_random_location_from_navigation()

    egos=[]
    for i in range(3):
        egos.append(EgoAgent(world))
    
    print(str(len(egos))+"Ego Agents added..")
    world.tick()
    spectator = world.get_spectator()
    transform = egos[0].ego.get_transform()
    spectator.set_transform(carla.Transform(transform.location + carla.Location(z=100), carla.Rotation(pitch=-90)))
    print("Spectator position set to the first ego agent")

    ### Testing still Lidar Data yet to be recieved
    lidar_segment_bp = blueprint_library.find('sensor.lidar.ray_cast_semantic')

    w_all_actors, w_all_id = getWalkers(client, world, blueprintsWalkers, 10)
    v_all_actors, v_all_id = getVehicles(client, world, vehicles_spawn_points, blueprintsVehicles, 20)
    
    while True:
        world.tick()


if __name__ == '__main__':
    main()