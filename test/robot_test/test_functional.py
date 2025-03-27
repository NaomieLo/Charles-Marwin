import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "../../src"))
sys.path.insert(0, src_dir)

import PathFinder
from AStar import AStar
from BidirectionalAStar import BidirectionalAStar
from MultiResolutionPathFinder import MultiResolutionPathFinder
from motors import Motors
from sensors import Sensor
from robot import Robot

#Dummy Brain
class DummyBrain:
    @staticmethod
    def get_cost():
        return
