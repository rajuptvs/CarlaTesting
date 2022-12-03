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

import carla

client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()
settings = world.get_settings()
world.apply_settings(settings)
settings.synchronous_mode = True
avail_maps = client.get_available_maps()
world = client.load_world("Town02")
blueprint_library = world.get_blueprint_library()

####
# Camera Setup
cambp=blueprint_library.find('sensor.camera.rgb')
cambp.set_attribute("image_size_x",str(1920))
cambp.set_attribute("image_size_y",str(1080))
cambp.set_attribute("fov",str(105))

cam_location = carla.Location(2,0,1)
cam_rotation = carla.Rotation(0,0,0)
cam_transform = carla.Transform(cam_location,cam_rotation)

########


vehicles_spawn_points = world.get_map().get_spawn_points()
ego_bp = random.choice(blueprint_library.filter('vehicle.*'))
ego_bp.set_attribute('role_name','ego')
ego_vehicle=world.spawn_actor(ego_bp,random.choice(vehicles_spawn_points))
ego_vehicle.set_autopilot(True)
ego_cam = world.spawn_actor(cambp,cam_transform,attach_to=ego_vehicle, attachment_type=carla.AttachmentType.Rigid)
ego_cam.listen(lambda image: image.save_to_disk('tutorial/output/%.6d.jpg' % image.frame))
while True:
    world.tick()