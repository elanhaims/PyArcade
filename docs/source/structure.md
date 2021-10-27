# File Structure

## How we structured our files
We structured our files in a way that seperates our pyarcade files in a way that is easy to follow. All of our docker, setup and initialization are in the project main directory under final-project. We then have a folder database, which is used to store our dynamodb database. Additionally, we have a tests folder where we keep all of our current tests and code to make pipeline work. Instance folder is used to store information about the database instance in a config file. Docs is used to run our sphinx documentation, which is what you are looking at now.
Pyarcade is where we keep all of our front-end and back-end code. We have __init__, auth, game_interface and games under pyarcade directory folder. These are used to manage the flask which communicates the html with the python. Then we have a templates folder, which is used to keep all the html code for the front-end of our games. Games folder stores all the code for the backend of games and their proxies. Dynamodb folder is used to communicate with the dynamo database in order to allow us to implement multiplayer and other features.

## Tree Path
```
└───final-project
    ├───database
    │   ├───DynamoDBLocal_lib
    │   └───third_party_licenses
    ├───docs
    │   ├───build
    │   │   ├───doctrees
    │   │   └───html
    │   │       ├───_sources
    │   │       └───_static
    │   │           ├───css
    │   │           │   └───fonts
    │   │           ├───fonts
    │   │           │   ├───Lato
    │   │           │   └───RobotoSlab
    │   │           └───js
    │   └───source
    ├───instance
    ├───pyarcade
    │   ├───dynamodb
    │   ├───Games
    │   ├───static
    │   ├───templates
    │   │   ├───auth
    │   │   └───games
    │   │       ├───connect4
    │   │       ├───mancala
    │   │       └───mastermind
    │   ├───unused_tests
    └───tests
```