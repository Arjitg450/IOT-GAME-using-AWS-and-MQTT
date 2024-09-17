ARJIT GUPTA CS23MTECH12001
P KAIF ALI KHAN CS22MTECH12009

Overview-
	1.This Python script simulates a multiplayer game where players interact over MQTT, a machine-to-machine (M2M)/"Internet of Things" connectivity protocol. 
	2.Each player is represented as a thread that subscribes to MQTT topics, receives game data, and publishes actions based on game logic.
	3.The game is now connected to AWS IoT Core Server.

Dependencies-
	paho-mqtt: This package provides client libraries for interacting with MQTT brokers. Install it via pip:
	pip install paho-mqtt

Key Components-
	1. Data Class: Handles the creation and string representation of game data messages.
	2. Player Class: Manages individual player actions, subscriptions, and state within the game.
	3. MQTT Callbacks: Functions on_connect and on_message handle MQTT events like connection and message reception.

Setup and Execution-
	1. Change the policies in the aws iot core server.
	2. Player Configuration: Each player's configuration, including their moves and stats, should be stored in individual text files named player-<id>.txt.
	3. Running the Script: Execute the script directly in terminal. The script takes the number of players from player-1.txt. So make sure the file exists before running.

	python3 runner.py

	Note: In some cases the winner declaration happens a little late, so please wait for 5 secs.

Script Workflow-
	1.Initialization:
		1.Players are instantiated with unique topics and initialized from configuration files.
		2.Each player connects to the MQTT broker and starts in its own thread.
	2.Gameplay Loop:
		1.Players subscribe to each other's topics to receive round data.
		2.The script synchronizes round execution across all player threads using a semaphore.
		3.Players publish their move each round and check for game conditions like conflicts or power differences.
	3.Endgame:
		1.After all rounds are executed, the script waits for players to finish and then declares the game over.
Game Logic-
	1.Players avoid occupying the same coordinates to prevent conflicts.
	2.If a neighboring player has higher power, a player dissolves, simulating a combat or challenge mechanism.

Notes-
	1.The script uses threading and synchronization primitives like semaphores to manage the state and synchronization between player threads.
	2.Proper error handling and cleanup (such as disconnecting from the MQTT broker) should be considered for robustness.
