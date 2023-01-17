
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
import carla
from carla import Transform, Location, Rotation

def findClosestSpawnPoint(spawn_points, target):
    dist = [(target.location.x-spawn_points[i].location.x)**2 + (target.location.y-spawn_points[i].location.y)**2 + (target.location.z-spawn_points[i].location.z)**2 for i in range(len(spawn_points))]
    return spawn_points[dist.index(min(dist))]


def makedirs(config_file,n_ego=2):
  try:
        os.mkdir("data/")
  except OSError:
        print("path exists")
        pass

  with open(config_file) as f:
    data = json.load(f)
  sensors = data['sensors']
  for i in range(n_ego):
      vehicle_name="data/"+"ego_"+str(i)
      try:
        os.makedirs(vehicle_name)
      except:
          pass
      print(vehicle_name)
      try:
        for sensor in sensors:
            folder_name = sensor['type']
            os.makedirs(os.path.join(vehicle_name,folder_name))
      except:
        pass

        
def get_sensors(world, data, vehicle_actor):
    blueprint_library = world.get_blueprint_library()
    sensor_references = []
    sensor_types = []
    for i in range(len(data['sensors'])):
        sensor = data['sensors'][i]
        bp = blueprint_library.find(sensor['type'])
        json_trans = sensor["transform"][0]

        relative_transf = Transform(Location(x=float(json_trans['x']), y = float(json_trans['y']), z = float(json_trans['z'])) , Rotation(pitch = float(json_trans['pitch']), yaw = float(json_trans['yaw']), roll = float(json_trans['roll'])) )
        blacklist = ['type', 'transform']
        settable_attributes = [attribute for attribute in sensor if attribute not in blacklist]
        for attr in settable_attributes:
            try:
                bp.set_attribute(str(attr), str(sensor[attr]))
            except:
                print("Problem with setting " + attr + "to " + sensor[attr] + " in sensor " + sensor['type'])

        sensor_actor = world.spawn_actor(bp, relative_transf, attach_to=vehicle_actor)

        sensor_types.append(sensor['type'])
        sensor_references.append(sensor_actor)
        
    return sensor_references, sensor_types

class EgoAgent:
    def getSensorData(self, frame_id):
        data = [self._retrieve_data(q, frame_id) for q in self.queues]
        return data

    def _retrieve_data(self, sensor_queue, frame_id):
        while True:
            data = sensor_queue.get(timeout=5.0)
            if data.frame == frame_id:
                return data
        
        
    def __init__(self,config,world):
        self.world=world
        f=open(config)
        data=json.load(f)
        makedirs(config)
        blueprint_library = world.get_blueprint_library()
        blueprintsVehicles = blueprint_library.filter('vehicle.*')
        vehicles_spawn_points = world.get_map().get_spawn_points()
        self.ego_bp = random.choice(blueprint_library.filter('vehicle.*'))
        self.ego_bp.set_attribute('role_name','ego')
        test=random.choice(vehicles_spawn_points)
        print(test)
        
        self.ego = world.spawn_actor(self.ego_bp, findClosestSpawnPoint(spawn_points=vehicles_spawn_points, target=test))
        self.ego.set_autopilot(True)
        self.sensors_ref, self.sensor_types = get_sensors(world, data, self.ego)
        self.queues = []
        q = queue.Queue()
        world.on_tick(q.put)
        self.queues.append(q)
        for sensor in self.sensors_ref:
            q = queue.Queue()
            sensor.listen(q.put)
            self.queues.append(q)


 
 
class CarlaSyncMode(object):
    def __init__(self, world, sensors):
        self.world = world
        self.sensors = sensors
        self.frame = None
        self._queues = []
        
    def __enter__(self):

        def make_queue(register_event):
            q = queue.Queue()
            register_event(q.put)
            self._queues.append(q)

        make_queue(self.world.on_tick)
        for sensor in self.sensors:
            make_queue(sensor.listen)
        return self

    def tick(self, timeout):
        self.frame = self.world.tick()
        data = [self._retrieve_data(q, timeout) for q in self._queues]
        assert all(x.frame == self.frame for x in data)
        return self.frame,data

    def __exit__(self, *args, **kwargs):
        self.world.apply_settings(self._settings)

    def _retrieve_data(self, sensor_queue, timeout):
        while True:
            data = sensor_queue.get(timeout=timeout)
            if data.frame == self.frame:
                return data