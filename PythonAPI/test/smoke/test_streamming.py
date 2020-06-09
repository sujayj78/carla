# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.


from . import SmokeTest

import time
import threading
import carla

class TestStreamming(SmokeTest):

    def __init__(self):
        self.lat = 0.0
        self.lon = 0.0

    def on_gnss_set(self, event):
        self.lat = event.latitude
        self.lon = event.longitude

    def on_gnss_check(self, event):
        self.assertAlmostEqual(event.latitude, self.lat, places=4)
        self.assertAlmostEqual(event.longitude, self.lon, places=4)

    def create_client(self):
        client = carla.Client(*self.testing_address)
        client.set_timeout(60.0)
        world = client.get_world()
        actors = world.get_actors()
        for actor in actors:
            if (actor.type_id == "sensor.other.gnss"):
                actor.listen(self.on_gnss_check)
        while (1):
            time.sleep(0.1)

    def test_multistream(self):
        # create the sensor
        world = self.client.get_world()
        bp = world.get_blueprint_library().find('sensor.other.gnss')
        bp.set_attribute("sensor_tick", str(1.0))
        gnss_sensor = world.spawn_actor(bp, carla.Transform())
        gnss_sensor.listen(self.on_gnss_set)
        world.wait_for_tick()

        # create clients
        for i in range(5):
            t = threading.Thread(target=self.create_client)
            t.setDaemon(True)
            t.start()

        time.sleep(5)
        gnss_sensor.destroy()
