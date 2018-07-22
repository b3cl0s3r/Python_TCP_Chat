# Python_TCP_Chat
TCP Chat written in Python. (POC. Made just for learning)

Allows:

* Send private messages between users.
* Check which users are online.
* Clients can get random username (from a list of 10) or choose one.

Take care:

* By default, accepts 10 clients simultaneously. You can set to accept less clients. If setting more than 10, you have to make some changes to color and name assignment from server side.
* It was made just for learning. Communication is not encrypted.

# Example how to use this program

Server and client are in the same file (functionality isn't separated)

# Run program as Server

* python -s

Run chat as server on localhost (0.0.0.0) on port 8080 (by default). 10 Users online as maximum. 
* python -s -m 5

Run chat as server on localhost (0.0.0.0) on port 8080. 5 Users online as maximum.
* python -s  -i 192.168.1.40 -p 4444 -m 7

Run chat as server on IP 192.168.1.40, on port 4444 and 7 users online as maximum.

# Run program as Client

* python -c

Try to connect as client to localhost (0.0.0.0) on port 8080.
* python -c -i 192.168.1.40 -p 4444

Try to connect as client to 192.168.1.40 on port 4444
* python -c -p 5000 -u Robert

Try to connect as client to localhost (0.0.0.0) on port 5000 with Robert as username.

Note: -m option does nothing if you use it as client.

# Server commands when running

Nothing for now

# Client commands when running

/help : show which commands you can use as client.

/online : show who is online.

/msg <username> <text> : send a private msg to <username> with <text> as message.
 
/clear : clear screen.

/private <username> : yet not implemented. 
 
/exit : exit program
 
