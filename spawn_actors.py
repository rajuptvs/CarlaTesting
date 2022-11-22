
import glob
import os
import sys
import time
from definitions import get_actor_blueprints

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

from carla import VehicleLightState as vls

import argparse
import logging
from numpy import random

class spawn_actors:
    def spawnme(self,number=20):
        vehicles_list = []
        walkers_list = []
        all_id = []
        self.client = carla.Client('127.0.0.1', 2000)
        self.client.set_timeout(10.0)
        synchronous_master = False
        number_of_vehicles=number   

        try:
            world = self.client.get_world()

            traffic_manager = self.client.get_trafficmanager(8000)
            traffic_manager.set_global_distance_to_leading_vehicle(2.5)
            settings = world.get_settings()
            traffic_manager.set_synchronous_mode(True)
            synchronous_master = True
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = 0.05

            blueprints = get_actor_blueprints(world, 'vehicle.*', 'All')
            blueprintsWalkers = get_actor_blueprints(world, 'walker.pedestrian.*','2')
            blueprints = sorted(blueprints, key=lambda bp: bp.id)
            spawn_points = world.get_map().get_spawn_points()
            number_of_spawn_points = len(spawn_points)
            if number_of_vehicles < number_of_spawn_points:
                random.shuffle(spawn_points)
            elif number_of_vehicles > number_of_spawn_points:
                msg = 'requested %d vehicles, but could only find %d spawn points'
                logging.warning(msg, number_of_vehicles, number_of_spawn_points)
                number_of_vehicles = number_of_spawn_points
            
            SpawnActor = carla.command.SpawnActor
            SetAutopilot = carla.command.SetAutopilot
            FutureActor = carla.command.FutureActor
            batch = []
            for n, transform in enumerate(spawn_points):
                if n >= number_of_vehicles:
                    break
                blueprint = random.choice(blueprints)
                if blueprint.has_attribute('color'):
                    color = random.choice(blueprint.get_attribute('color').recommended_values)
                    blueprint.set_attribute('color', color)
                if blueprint.has_attribute('driver_id'):
                    driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                    blueprint.set_attribute('driver_id', driver_id)
                else:
                    blueprint.set_attribute('role_name', 'autopilot')
                batch.append(SpawnActor(blueprint, transform)
                    .then(SetAutopilot(FutureActor, True, traffic_manager.get_port())))

            for response in self.client.apply_batch_sync(batch, synchronous_master):
                if response.error:
                    logging.error(response.error)
                else:
                    vehicles_list.append(response.actor_id)
            traffic_manager.global_percentage_speed_difference(30.0)
            while True:
                world.tick()


        finally:
                    
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.no_rendering_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)
            print('\ndestroying %d vehicles' % len(vehicles_list))
            self.client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])
            print('\ndestroying %d walkers' % len(walkers_list))
            self.client.apply_batch([carla.command.DestroyActor(x) for x in all_id])

            time.sleep(0.5)
