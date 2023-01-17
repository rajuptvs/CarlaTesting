import random
import glob
import os
import sys
import time
from ego_agents import EgoAgent,CarlaSyncMode


try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
print(sys.path)
import carla

def saveAllSensors(out_root_folder, sensor_data, sensor_types):
    sensor_data.pop(0)

    for i in range(len(sensor_data)):
        sensor_name = sensor_types[i]
        if(sensor_name == 'sensor.camera.rgb'):
            saveImage(sensor_data[i], os.path.join(out_root_folder, sensor_name))
        if(sensor_name == 'sensor.lidar.ray_cast' or sensor_name == 'sensor.lidar.ray_cast_semantic'):
            saveLidar(sensor_data[i], os.path.join(out_root_folder, sensor_name))
        if(sensor_name=='sensor.camera.semantic_segmentation'):
            saveImageSeg(sensor_data[i], os.path.join(out_root_folder, sensor_name))
        if(sensor_name=='sensor.camera.instance_segmentation'):
            saveImageIns(sensor_data[i], os.path.join(out_root_folder, sensor_name))

def saveLidar(output, filepath):
    output.save_to_disk(filepath + '/%05d'%output.frame)
    with open(filepath + "/lidar_metadata.txt", 'a') as fp:
        fp.writelines(str(output) + ", ")
        fp.writelines(str(output.transform) + "\n")


def saveImage(output, filepath):
    output.save_to_disk(filepath + '/%05d'%output.frame)
    with open(filepath + "/camera_metadata.txt", 'a') as fp:
        fp.writelines(str(output) + ", ")
        fp.writelines(str(output.transform) + "\n")
    return
def saveImageSeg(output, filepath):
    output.save_to_disk(filepath + '/%05d'%output.frame,carla.ColorConverter.CityScapesPalette)
    with open(filepath + "/camera_seg_metadata.txt", 'a') as fp:
        fp.writelines(str(output) + ", ")
        fp.writelines(str(output.transform) + "\n")
    return
def saveImageIns(output, filepath):
    output.save_to_disk(filepath + '/%05d'%output.frame)
    with open(filepath + "/camera_insseg_metadata.txt", 'a') as fp:
        fp.writelines(str(output) + ", ")
        fp.writelines(str(output.transform) + "\n")
    return

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
    for i in range(2):
        egos.append(EgoAgent('CarlaTesting/sensors.json',world))
    
    print(str(len(egos))+" Ego Agents added..")

    world.tick()
    
    k=0
    try:
        print("entered loop")
        with CarlaSyncMode(world, []) as sync_mode:
            print("entered inner loop")
            while True:
                print("entered inner inner loop")
                frame_id,data = sync_mode.tick(timeout=5.0)
                if(k < 70):
                    k = k + 1
                    continue
                for i in range(len(egos)):
                    data = egos[i].getSensorData(frame_id)
                    output_folder = os.path.join("data", "ego_" + str(i))
                    saveAllSensors(output_folder, data, egos[i].sensor_types)
                    print("next")
    finally:
        print("Do the destruction here!!!!!!!!!!!!!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('\ndone.')
