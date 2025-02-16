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
