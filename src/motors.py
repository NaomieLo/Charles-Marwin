import transformations
import time
import sensors
import threading
from typing import Dict, Any, Optional

"""
This class has the logic of motors for battery consumption

It assumes a battery bar where there are 'solar panels' on the robot.
-Every action, the robot's battery charges %2 every 5 seconds. 
-When it stops, it gains %4 charge.
-While going on flat ground (less than 10m elevation), the battery is consumed %1
-While climbing a hill (more than 10m elevation), %2.5
    -> 10 - 50: %2.5
    -> 51 - 100: %3  
-Downhill consumes %0.5 

"""

class Motors:
    DOWNHILL_POWER = 0.995
    MILD_UPHILL_POWER = 0.975 # in order to consume 100 - 2.5 = 97.5
    STEEP_UPHILL_POWER = 0.97
    FLATGROUND_POWER = 0.99
    CHARGING_RATE = 1.02
    BONUS_CHARGING = 1.04

    BATTERY_LOW_THRESHOLD = 20.0 # warning level
    BATTERY_CRITICAL_THRESHOLD = 5.0 # critical leve;

    def __init__(self, elevation_map, affine_transform):
        self.battery = 100.0                       # Keep track of battery percentage
        self.elevation_map = elevation_map
        self.affine_transform = affine_transform
        self.is_running = False
        self.is_stopped = True
        self.charging_thread = None
        self.last_action_time = time.time()
        

    def charge_battery(self):
        """
        While battery > 0, every 5 seconds charge the batters by %2 percent
            - If battery 100, stop charging
        """
        current_time = time.time()
        elapsed_time = current_time - self.last_action_time

        if elapsed_time >= 5:
            if self.battery < 100.0:
                old_battery = self.battery
                self.battery = min(100, self.battery * self.CHARGING_RATE)
                print(f"Charging... Battery: {old_battery:.1f}% -> {self.battery:.1f}%\n")
            self.last_action_time = current_time
        
        if self.is_stopped and self.battery < 100.0:
            old_battery = self.battery
            self.battery = min(100.0, self.battery * self.BONUS_CHARGING)
            self.is_stopped = False
            print(f"Stop charking bonus: {old_battery:.1f}% -> {self.battery:.1f}%\n")
        


    def consume_battery(self) -> bool: # not completed yet
        """
        Consuming battery according too elevation
         
        Returns:
            bool: True if battery has sufficient charge, False otherwise
        """
        if self.battery <= 0:
            print("ERROR: Battery already depleted!\n")
            return False

        elevation = sensors.Sensor.get_elevation_at_position
        old_battery = self.battery
        
        # Apply consumption based on elevation
        if elevation < 0:
            # Downhill
            self.battery *= self.DOWNHILL_POWER
        elif 0 <= elevation <= 10:
            # Flat ground
            self.battery *= self.FLATGROUND_POWER
        elif 10 < elevation <= 50:
            # Mild uphill
            self.battery *= self.MILD_UPHILL_POWER
        elif 50 < elevation <= 100:
            # Steep uphill
            self.battery *= self.STEEP_UPHILL_POWER
        
        # Make sure battery doesn't go below 0
        self.battery = max(0.0, self.battery)

        print(f"Battery: {old_battery:.1f}% -> {self.battery:.1f}%\n")

        # check battery status and give necessary warnings
        if self.battery <= 0:
            print("CRITICAL: Battery depleted! Charles Marwin shut down until recharged\n")
            self.stop()
            return False
        elif self.battery <= self.BATTERY_CRITICAL_THRESHOLD:
            print(f"CRITICAL: Battery level at {self.battery:.1f}%. Recharge required\n")
        elif self.battery <= self.BATTERY_LOW_THRESHOLD:
            print(f"WARNING: Low battery level {self.battery:.1f}%\n")

        return True


    def background_charging(self):
        """Background thread to continuously charge"""
        while self.is_running:
            self.charge_battery()
            time.sleep(1)       # check every second and charge every 5 seconds in charge_battery()
    
    def get_battery(self):
        return max(0, self.battery)

    def start_motors(self) -> bool:
        """
        Start the motors and background charging

        Returns:
            bool: True is started successfully, False otherwise
        """
        if self.battery <= 0:
            print("Cannot start: Battery depleted\n")
            return False
    
        self.is_running = True
        self.is_stopped = False

        # Start the background charging thread
        if self.charging_thread is None or not self.charging_thread.is_alive():
            self.charging_thread = threading.Thread(target=self.background_charging)
            self.charging_thread.daemon = True
            self.charging_thread.start()
        
        print(f"Motors started\n")
        return True
    
    def stop(self):
        """Stop the motors and mark as stopped for bonus charging"""
        self.is_running = False
        self.is_stopped = True

        # Stop threads
        if self.charging_thread and self.charging_thread.is_alive():
            self.charging_thread.join(timeout=1.0)
        
        print(f"Motors stopped. Battery: {self.battery:.1f}%")