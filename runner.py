import paho.mqtt.client as mqtt
import time
import threading
import ssl

class Data:
    # type : connect, round, dissolve, error
    def __init__(self, var1, var2=None):
        if var2 is None:
            self.type, self.data = var1.split('@del')
        else:
            self.type = var1
            self.data = var2

    def __str__(self):
        return f"{self.type}@del{self.data}"

class Player:
    def __init__(self):
        self.connected = False # connected to the broker
        self.client = None # mqtt client
        self.rounds = [] # list of rounds
        self.round_data = {} # round data received from other players
        self.player_id = 0 # player id
        self.topic = "" # topic of the player
        self.no_of_players = 0 # number of players
    
    def player_winner(self):
        global won
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!player-', self.player_id, 'wins')
        self.client.disconnect()
        won = True
        exit()
    
    def subscribe_to_all(self):
        # subscribe to all the players except itself
        for i in range(1, n + 1):
            if i == self.player_id:
                continue
            _topic = "player-" + str(i)
            self.client.subscribe(_topic)
            print('player-', self.player_id, 'subscribed to', _topic)

    def run(self):
        global sem, n, total_connections, curr_round, res, subscribed
        # check if all the players are connected
        while total_connections != n:
            continue
        
        self.subscribe_to_all() # subscribe to all the players
        subscribed[self.player_id - 1] = 1 # mark the player as subscribed
        print('waiting for every one to subscribe') 
        while sum(subscribed) != n: # wait for all the players to subscribe
            continue
        # print('player-', self.player_id, 'subscribed to all')
        time.sleep(1)
        # now add the last round as dummy rounds to complete total_rounds
        while len(self.rounds) < total_rounds:
            self.rounds.append(self.rounds[-1])
        
        for i in range(1, len(self.rounds)+1): # iterate over all the rounds
            
            
            while curr_round != i: # wait for the current round to be i from the governer
                print(player.player_id,'waiting for the governer curr_round', curr_round, 'i', i)
                time.sleep(0.2)
                continue
            print('remaining players', self.no_of_players)
            if self.no_of_players == 1: # if only one player is left then he is the winner
                self.player_winner()

            print('player-', self.player_id, 'Round', i)
            # get the x, y, p from the round
            x, y, p = self.rounds[i-1]
            data = Data(f"round@del{i} {x} {y} {p}")
            self.client.publish(self.topic, str(data)) # publish the round data
            print('player-', self.player_id, 'published round', i, (x,y,p))

            # check if all the players have responded
            while i not in self.round_data or len(self.round_data[i]) < self.no_of_players - 1:
                
                print('player-', self.player_id, 'waiting for round', i)
                if self.no_of_players == 1: # if only one player is left then he is the winner
                    self.player_winner()
                
                if i in self.round_data:
                    print('player-', self.player_id, 'received', len(self.round_data[i]), 'responses for round', i)
                    
                time.sleep(1)
                continue
            
            # compute the round

            # the player should not coincide with any other player
            for player_round in self.round_data[i]:
                x1 = player_round[1]
                y1 = player_round[2]
                if x1 == x and y1 == y:
                    print(i)
                    print ('player-'+str(self.player_id)+'Conflict:', x, y, 'with player-', player_round[0], x1, y1)
                    data = Data('error', 'Conflict') # if conflict then send error message
                    self.client.publish(self.topic, str(data)) # publish the error message
                    return 0

            # if the player neighbour has more power, then the player should dissolve and return
            for player_round in self.round_data[i]:
                x_op = player_round[1]
                y_op = player_round[2]
                power_op = player_round[3]
                # check if the player is neighbour to the other player
                if (x == x_op and y+1 == y_op) or (x == x_op and y-1 == y_op) or (x+1 == x_op and y == y_op) or (x-1 == x_op and y == y_op) or (x+1 == x_op and y+1 == y_op) or (x-1 == x_op and y-1 == y_op) or (x+1 == x_op and y-1 == y_op) or (x-1 == x_op and y+1 == y_op):
                    if power_op > p:
                        print ('player-'+str(self.player_id)+'Dissolve:', x, y)
                        data = Data('dissolve', str(self.player_id)+' by '+str(player_round[0]))
                        self.client.publish(self.topic, str(data))
                        sem.acquire()
                        n-=1
                        sem.release()
                        print('player-', self.player_id, 'dissolved')
                        self.client.disconnect()
                        return 0

            res[self.player_id - 1] = 1
        
        # if all the rounds are completed then you are winner
        time.sleep(5)
        res[self.player_id - 1] = 1
        # wait for all the players to complete the rounds
        

        if self.no_of_players == 1: # if only one player is left then he is the winner
            self.player_winner()

    # runs the player thread
    def start(self):
        self.thread = threading.Thread(target=self.run)
        self.thread.start()


# callback functions for mqtt
def on_connect(client, userdata, flags, rc):
    player = userdata
    if rc == 0:
        print("Connected to broker", player.topic)
        player.connected = True # initialize the connected variable to True
    else:
        print("Connection failed")

# callback function for message
def on_message(client, userdata, message):
    global sem, n, error
    player = userdata
    if message.topic != player.topic:
        msg = message.payload.decode("utf-8")
        # convert the string to Data object
        data = Data(msg)
        print(player.player_id, "Received message '" + str(msg) + "' on topic '" + message.topic + "'")

        if data.type == 'round': # if round data is received then store it in the player object
            round, x, y, p = data.data.split()
            round = int(round)
            x = int(x)
            y = int(y)
            p = int(p)
            lis_data = [message.topic.split('player-')[1], x, y, p]
            if round not in player.round_data:
                player.round_data[round] = []
            player.round_data[round].append(lis_data)

        elif data.type == 'dissolve': # if dissolve data is received then print the message
            player.no_of_players -= 1
            print('lost', data.data)
            print(player.topic,'remaining players', player.no_of_players)
        elif data.type == 'error': # if error data is received then quit the game
            error = True
            quit()
        else:
            pass


# semaphore for sync
sem = threading.Semaphore() # semaphore for sync
# n = int(input("Enter the number of players: ")) # number of players

# to get the number of players open the first file and get the number of players
file = open("player-1.txt", "r")
for line in file:
    n = int(line.split()[0])
    break
file.close()
total_connections = 0 # total connections
subscribed = [0]*n # list to check if the player has subscribed
curr_round = 0 # current round
res = [0] * n # list to check if the player has completed the round
total_rounds = 0 # total rounds
max_rounds = 0 # max rounds
error = False # error flag
init_n = n
won = False


# create each player
for i in range(1, n + 1):
    topic = "player-" + str(i)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1 ,topic)
    # player is an object of class Player
    player = Player()
    player.topic = topic
    # pass player as userdata to the mqtt functions
    client.user_data_set(player)
    client.on_connect = on_connect
    client.on_message = on_message
    
    awshost = "a12vk58hg73akk-ats.iot.us-east-1.amazonaws.com" #replace
    awsport = 8883

    caPath = "./aws_package/root-CA.crt" # Root certificate authority, comes from AWS (Replace)
    certPath = "./aws_package/Server_1.cert.pem" #Replace
    keyPath = "./aws_package/Server_1.private.key" #Replace

    client.tls_set(caPath, 
        certfile=certPath, 
        keyfile=keyPath, 
        cert_reqs=ssl.CERT_REQUIRED, 
        tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)

    # connect to the broker

    client.connect(awshost, awsport)
    client.loop_start()


    # initialize required data for the palyer like rounds, player_id, topic
    rounds = []
    total_rounds = 0
    file = open("player-" + str(i) + ".txt", "r")
    c = 0
    for line in file:
        if c == 0:
            c += 1
            continue
        if line == '\n' or line == '' or line == ' ':
            continue
        x,y,p = line.split()
        int_pos = [int(x), int(y), int(p)]
        rounds.append(int_pos)
        total_rounds += 1

    if total_rounds > max_rounds:
        max_rounds = total_rounds
    
    # initialize the player object
    player.client = client
    player.rounds = rounds
    player.player_id = i
    player.no_of_players = n
    # player.topic = topic
    player.start()

    # wait for the player to connect
    while not player.connected:
        continue
    # increment the total connections
    total_connections += 1

total_rounds = max_rounds

# this piece of code governs the game, so that the rounds happen in sync
for i in range(1, total_rounds + 1):
    # initialize the curr_round, which is read by the player threads to work accordingly
    sem.acquire()
    curr_round = i
    sem.release()

    print("Round", i)
    
    time.sleep(1)
    print(res)
    # res is a variable which is used to check if all the players have completed the round
    # wait for all the players to complete the round
    while sum(res) != n:
        print('waiting for all the players to complete round', i)
        time.sleep(1)
        if error:
            i = total_rounds + 1
            break
        if won:
            break
        continue
    if won:
        break
    # print(sum(res))
    # clear the resp
    res = [0] * init_n
# sleep for some time unitl every one finishes.
time.sleep(5)
print("Game over, remaining players", n)