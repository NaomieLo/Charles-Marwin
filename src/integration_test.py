from robot_render import UI
from robot import Robot

def __init__(self):
    self.ui = UI()
    self.robot = Robot("Testbot","A*")

    self.ui.main()