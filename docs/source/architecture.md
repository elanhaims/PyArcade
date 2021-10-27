# Architecture

## How our code works
We structured our project in a way that would seperate our front-end code, back-end code and then have the flask in-between so it is easy to follow. More information about the actual formatting of the files in the file structure tab. 

Our code works by having the back-end, which is our python code manage how the games work and processing all the information given by the front-end. We use proxies for each game in order to ensure the information being passed through is correct and a proper move for each game. If it is valid we then send that information to the game files and from there we change the game based on that information.

Our front-end allows us to display the games visually and allow the user to see any information provided, such as high scores, all the different game sessions they are playing and who they are playing against. 

We are using dynamodb in order to store all the information about our user, their logins, and information about their game sessions. It works by the front-end sending the game information to our back-end code and then the back-end returning information about the game session, which is stored on the database. Additionally, this also works the same for when users are logging in.

### Front-End
- HTML
- Flask
- json

### Back-End
- Python
- Flask

### Cloud
- DynamoDB
- AWS
- boto3
- UUID