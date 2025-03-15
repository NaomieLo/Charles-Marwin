import numpy as np
import transformations
import time

"""
This class has the logic of motors for battery consumption

It assumes a batter bar where there are 'solar panels' on the robot.
-Every action, the robot's batter charges %2 every 5 seconds. 
-When it stops, it gains %3 charge.
-While going on flat ground, the battery is consumed %1
-While climbing a hill (the more steep the more consumption), %2.5
-Downhill consumes %0.5 

Functions:
charging()

"""

class Motors:
    DOWNHILL_POWER = 0.5
    UPHILL_POWER = 2.5
    FLATGROUND_POWER = 1
    CHARGING_RATE = 1.02

    def __init__(self, elevation_map, affine_transform):
        self.battery = 100.0                       # Keep track of battery percentage
        self.elevation_map = elevation_map
        self.affine_transform = affine_transform
        

    def charge_battery(self):
        """
        While battery > 0, every 5 seconds charge the batters by %2 percent
            - If battery 100, stop charging
        """
        if self.battery < 100:
            self.battery = min(100, self.battery * self.CHARGING_RATE)
            print(f"Charging... Battery: {self.battery}%")
        else:
            print("Battery full")

    def consume_battery(self, terrain_type): # not completed yet
        self.battery = max(0, self.battery)

        if self.battery == 0:
            print("Stop rover, must stop and recharge. 0 battery")

    def run(self):
        while self.battery > 0:
            self.charge_battery()
            time.sleep(5)       # charge every 5 seconds
    







    

