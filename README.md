# User Documentation
### Installation
**Access PyArcade here:** http://ec2-3-81-100-51.compute-1.amazonaws.com:5000/
### Using the Application
**Logging in:**
Enter your preferred username and password in the correct fields. Then click the 'Log In' button and you will be redirected to the game menu. Alternatively, you can click directly on the 'Guest User' button in the main menu in order to login to the guest account automatically.

**Logging out:**
At the top right of any screen (including the main menu or games) you will be able to log out by clicking the 'Log Out' button.

**Starting Game:**
If you are currently not at the game menu click the "Main Menu" button at the top right. From here you will be able to choose whichever game you would like to play by clicking on the game name, such as 'Mastermind', 'Connect 4', or 'Mancala'.

**Instruction Video:**
These instructions listed above are in a tab when you log in called "How to Use PyArcade" and there are also instruction pages + videos within each of the game pages.

### Playing Games
#### Connect Four
*Starting Game*
> To play Connect Four you will need to open two different browsers (i.e. Google Chrome and Firefox) and log in to two different users. <br />
> In order to start a game click the 'New' button at the top right of the screen for one of the users, once you have done this, it will ask you to enter an opponent Id. <br />
> Enter the username of the person you would like to play against (the other user that you logged in as in the other browser). <br />
> This will send a request to the other user. From here you can begin playing the game. <br />
> To refresh the page after a move, click the refresh button on the page to make sure you have the newest updated game. When the instruction video was made,
> returning to the sessions page and clicking resume game on the session you were playing was necessary to refresh the page.<br /> 
> You are able to have multiple game sessions playing at once, so you are able to start as many new games as you would like.

*Resuming Game*
> If you have left your computer and would like to come back to play the game, you can navigate to the connect 4 game and from there click resume on the session you are trying to play.

*Ending/Deleting Game*
> This is the same as resuming the game, you navigate over to the connect 4 game menu and then click delete on the session you want to end.

*Changing Team Colors*
> If you would like to change the team colors you can do so by clicking on the colored bar next to the text, 'Choose color for player x'. Then you are able to change the color using RGB values or the color palette. 

*Playing the game*
> In order to know whose turn it is or if the game is over yet, you look at the text above the game board. It should read in one of these formats:
	"The current player is PlayerX"
	"Game Over and the winner is Player X"
	"Game Over and it is a Draw"
Once the game is over you can you can delete the game with the instructions above. In order to place a chip you can place anywhere on the column you are wanting to drop the chip into. 

*Rules*
> In order to win you must have a row of your same colored chips, this can be vertical, horizontal or diagonal.
The turns alternate between players and you can drop a chip into any column and it will fall to the lowest available slot.
If you would like to access the instructions for this game, you can click the ''How to Play Connect Four'' button at the top right of the screen.

### Mastermind
*Starting Game*
> In order to start a game click the 'New' button at the top right of the screen, once you have done this a text box and button will appear. From here you can begin playing the game. You are able to have multiple game sessions playing at once, so you are able to start as many new games as you would like.

*Resuming Game*
> If you have left your computer and would like to come back to play the game, you can navigate to the Mastermind game from the main menu. From there, click resume on the session you are trying to play.

*Ending/Deleting Game*
> This is the same as resuming the game, you navigate over to the Mastermind game menu and then click delete on the session you want to end.


*Playing the game*
> Enter in 4 digits to make your guess. After testing each input, you will be able to see how many bulls and cows you have based on that particular guess. Repeat until you have completed the game.
Once the game is over (4 bulls), you can delete the game with the instructions above.

*Rules*
> If you would like to access the instructions for this game, you can click the ''How to Play Mastermind'' button at the top right of the screen.

### Mancala
*Starting Game*
> To play Mancala you will need to open two different browsers (i.e. Google Chrome and Firefox) and log in to two different users. <br />
> In order to start a game click the 'New' button at the top right of the screen for one of the users, once you have done this, it will ask you to enter an opponent Id. <br />
> Enter the username of the person you would like to play against (the other user that you logged in as in the other browser). <br />
> This will send a request to the other user. From here you can begin playing the game. <br />
> To refresh the page after a move, click the refresh button on the page to make sure you have the newest updated game. When the instruction video was made,
> returning to the sessions page and clicking resume game on the session you were playing was necessary to refresh the page.<br /> 
> You are able to have multiple game sessions playing at once, so you are able to start as many new games as you would like.

*Resuming Game*
> If you have left your computer and would like to come back to play the game, you can navigate to the Mancala game menu and then click resume on the session you are trying to play.

*Ending/Deleting Game*
> This is the same as resuming the game, you navigate over to the Mancala game menu and then click delete on the session you want to end.

*Playing the game*
> In order to know whose turn it is or if the game is over yet, you look at the text above the game board. It should read in one of these formats:
	"Next player: Player X"
	"Game Over and the winner is Player X"
	"Game Over and it is a Draw"
Once the game is over you can you can delete the game with the instructions above. In order to make your move, click the pocket of pieces that you want to distribute. 

*Rules*
> In order to win you must have more pieces collected than your opponent by the end of the game.
The turns alternate between players and you select which pocket of pieces to distribute over the board in the hopes of getting as many pieces in your Mancala.
If you would like to access the instructions for this game, you can click the ''How to Play Mancala'' button at the top right of the screen.

### Tests
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

# Developer Documentation
> Make sure you have Sphinx and sphinx-rtd-theme installed on your computer. <br />
> To access the developer documentation, navigate to final-project/docs and run 'make.bat html' on windows and 'make html' on linux. <br />
> This will generate a build directory inside the docs directory. <br />
> Open up the html directory inside build and find index.html. <br />
> Open up index.html in your browser and this will take you to the developer documentation home page, <br />
> From there you can navigate to the documentation for individual modules. <br />
