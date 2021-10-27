# Running PyArcade

## Installation
**Access PyArcade here:** http://ec2-3-81-100-51.compute-1.amazonaws.com:5000/
## Using the Application
**Logging in:**
Enter your preferred username and password in the correct fields. Then click the 'Log In' button and you will be redirected to the game menu. Alternatively, you can click directly on the 'Guest User' button in the main menu in order to login to the guest account automatically.

**Logging out:**
At the top right of any screen (including the main menu or games) you will be able to log out by clicking the 'Log Out' button.

**Starting Game:**
If you are currently not at the game menu click the "Main Menu" button at the top right. From here you will be able to choose whichever game you would like to play by clicking on the game name, such as 'Mastermind', 'Connect 4', or 'Mancala'.

**Instruction Video:**
These instructions listed above are in a tab when you log in called "How to Use PyArcade" and there are also instruction pages + videos within each of the game pages.

## Tests
The CI/CD pipeline is configured to run and show the test results of all the games on GitLab, but if you would like to run locally you can do that as well. To do so follow these steps: <br>
Make sure pytest and pytest-cov are installed <br>
Open up a terminal and navigate to the database directory and from there run either startdb.cmd or startdb.sh <br>
Then go into the tests folder and in each of the tests change the following line (around line 23) <br>
change: ```python
config['dynamodb'] = {'dynamodb_service_endpoint': 'dynam', 'dynamodb_port': '8000'}``` <br>
to: ```pythong
config['dynamodb'] = {'dynamodb_service_endpoint': 'localhost'', 'dynamodb_port': '8000'}``` <br>
Then in a separate terminal run this command within the final_project folder:
>pytest --cov=pyarcade/Games tests/