# Charles-Marwin
## How to setup 101
### Install Python
We are using python 3.13 while 3.10 has been tested to be wroking fine so far. You can install the installer on *https://www.python.org/downloads/*.
### Install libraries
'pip install -r requirements.txt'

## Database 101
-The first time you run the project/a function that reads or writes to the file, you will have to log 
into your google account and authorize the app.
-You can copy the link that appears in the output (this should avoid any permission errors from your browser but if you're having trouble double check this first).
-After authorization, a token.json file will be created locally, allowing future access without re-authentication. 
-token.json has been added to the gitignore (double check) so that it won't be shared to everyone else 

There are 4 functions you need to know about : read_history(), write_history(data), update_history() and input_data(startLocation, endLocation, robot, ai, distance, time, cost). 

read_history(): reads the dababase and returns results in a list []
input_data(startLocation, endLocation, robot, ai, distance, time, cost): allows some data validation. This will need to be updated when we know more about what we want to call our robots and AI but for now, 
I put some placement values that you can verify in this function. 

write_history(data): writes the above formatted data to both the local csv and the cloud csv. 

update_history(): I wrote this function to serve as a type of delete function in a simple sense. It will update the online csv with your local csv e.g if you want to delete an entry you can do it locally and then call update_history() and it will basically make the online history your local history 

## Application set up: main.py
Once the requirements have been installed and the database components are understood by the user, they must run the following command on their terminal:

'python src/main.py'

This script unzips the tif file with the elevation data and the vtk file with the terrain mesh. It also tests whether rasterio is functional and able to extract the required information.

## Running the app: screens.py
Once the previous steps have been completed, the app will be functional and the user will be able to use it by running the following command:

'python src/screens.py'
 
## Using the app
A Welcome Screen will be shown to the user. From here, they will be able to continue to the Main Menu, where they can choose to find a path or view the history with information about previous uses of the app. 
In the case that the user chooses to find a path, they will be prompted to select a robot (Perseverance, Curiosity or Spirit) and a Brain (A*, Bidirectional A* or Multiresolution). When this is done, the user might need to wait for a couple of seconds for the rover to be set up. 

Subsequently, the app will display a map and two collapsable frames where the user can choose the start and end locations. The user **must** select one option for each endpoint. When the **"Go"** button is pressed, the pathfinding process will start. It is possible that the app will take varying amounts of time to complete this procedure depending on the distance between the endpoints and the complexity of the terrain. When a path is found, the app will display a simulation, where the user will see the behavior of the robot during the traversal of the terrain. 

In the end, the user will have a chance to view the information of the recently completed traversal. From here, the user can also choose to go back and try a different robot model or another brain.




