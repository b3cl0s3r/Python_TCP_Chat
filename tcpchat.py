#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Chat TCP en python.
#
#

import socket
import os
import sys
from thread import *
from threading import *
import argparse
import random
import re
import errno
from socket import error as socket_error
import readline

# To install readline, it's necesary to have libncurses-dev in your system
# Readline blocks that users can overwrite other users' messages.

#class colors:
#    PURPLE = '\033[95m'
#    BLUE = '\033[94m'
#    LGREEN = '\033[92m'
#    YELLOW = '\033[93m'
#    WHITE = '\033[97m'
#    LBLUE = '\033[35m'
#    RED = '\033[31m'
#    GREEN = '\033[32m'
#    ORANGE = '\033[33m'
#    LBLUE = '\033[34m'
#    RESET = '\033[0m'
#    ERROR = '\033[91m'

USERNAME = ('Bobby','Snoopy','Mitnick','Jimmy','Lawrence','Dylan','Noah','Arvis','Ulises','Shane')
COLOR = ('\033[94m', '\033[97m', '\033[36m', '\033[32m', '\033[95m', '\033[92m', '\033[93m', '\033[35m', '\033[33m','\033[34m')
RESET = '\033[0m'
PRIVATE = '\033[1;91m'
HELP1 = '\033[1;96m'
HELP2 = '\033[1;97m'
WARNING = '\033[93m'

# To support more than 10 connections, is needed to provide more colours or enable that colours can be more than once. Same should be done with usernames

########################
##     SERVER SIDE    ##
########################


#
# CONSTRUCTOR: INICIO DEL SERVER, GESTIONA CONEXIONES, TERMINA CORRECTAMENTE EL PROGRAMA
#

class Server():
    def __init__(self, ip, port, max):
        self.users = list()
        self.colors = list()
        self.clients = list()

        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while True:
            try:
                serversocket.bind((ip, port))
                break

            except socket.error as msg:
                if msg[0] == 98:
                    print 'Bind failed on port '+str(port)+'. Error Code : %s   Message: %s ' %(str(msg[0]), str(msg[1]))
                    port=random.randint(1024,65535)
                    print 'Trying to bind on port '+str(port)+'...'
                else:
                    print 'Bind failed. Error Code: %s Message: %s ' %(str(msg[0]), str(msg[1]))
                    sys.exit()

        print "Server running on port "+str(port)

        try:
            #Maximo max conexiones concurrentes
            serversocket.listen(max)
            start_new_thread(self.servercommand, ())

            while True:
                if self.clients.__len__() < max:
                    conn, addr = serversocket.accept()
                else:
                    conn, addr = serversocket.accept()
                    conn.send("!{Server_Is_Full}")
                    continue
                self.clients.append(conn)
                print 'Connection with %s : %s ' %(addr[0], str(addr[1]))
                start_new_thread(self.clientthread ,(conn,))
        except:
            print "\nClosing server..."
            os.system('stty sane')
            if self.clients:
                for i in self.clients:
                    i.sendall("!{Error_Server_OFF}")

        finally:
            serversocket.close()

#
# HILO DE CADA CLIENTE
#

    def clientthread(self,conn):
        data = conn.recv(1024)
        if data == "None":
            while True:
                user=USERNAME[random.randint(0,9)]
                if user in self.users:
                    continue
                else:
                    self.users.append(user)
                    break
        elif data in self.users or data.count(" "):
            conn.send("!{Error_Name_In_Use}")
            self.clients.remove(conn)
            conn.close()
            exit()
        elif data.__len__()<=10:
            user=data
            self.users.append(user)
        else:
            conn.send("!{Name_Size_Error}")
            self.clients.remove(conn)
            conn.close()
            exit()
        while True:
            color=COLOR[random.randint(0,9)]
            if color in self.colors:
                continue
            else:
                self.colors.append(color)
                break

        string = "Welcome to the server "+color+user+RESET+'. Type /exit to leave.\n'+str(self.clients.__len__())+" users are online!\n"
        conn.send(string)

        try:
            while True:

                data = conn.recv(1024)

                # Estos comandos llegan 'limpios' por parte del cliente

                if not data or data == "/exit":
                    conn.send("See you!")
                    break

                elif data == "/online":
                    data = str(self.clients.__len__())+" users are online!\n"
                    string=str()
                    for i in self.users:
                        string=string+i+"  "
                    data = data+string
                    conn.send(data)
                    continue

                elif data == "!{Error_Server_OFF}" or data == "!{Private_Message}" or data == "!{Server_Kick}":
                    continue

                ## Evita que un posible atacante intente provocar bugs en la aplicación. Entre ellos, echar a todos los clientes.

                try:
                    # Ejemplo:
                    # b3cl0s3r: /msg roberto hola que tal
                    split = data.split(" ",1)
                    # ["b3cl0s3r:", "/msg roberto hola que tal"]
                    string = split[1].split(" ",1)
                    # ["/msg", "roberto hola que tal"]
                    name = split[0]
                    # "b3cl0s3r:"
                except:
                    continue

                # Mensaje privado

                if string[0] == "/msg":
                    try:
                        duser = string[1].split(" ",1)
                        # ["roberto", "hola que tal"]

                        if duser[0] in self.users:
                            pos = self.users.index(duser[0])
                            private = PRIVATE+"[*] "+name+" "+duser[1]
                            self.clients[pos].send(private)

                        else:
                            string = duser[0]+" isn't online!"
                            conn.send(string)

                    except:
                        conn.send("Please, provide an username!")
                    continue

                self.sendtoall(conn, data)

        except socket.error:
            print user+" has left."
        finally:
            servermsg = user+" has left."
            print servermsg
            for i in self.clients:
                if conn is not i:
                    i.sendall(servermsg)
            conn.close()
            self.clients.remove(conn)
            self.users.remove(user)
            self.colors.remove(color)

#
# MUESTRA QUIEN ESTA ONLINE
#

    def online (self):
        for i in self.users:
            string=string+" "+i
        return string

#
# MANDA A TODOS LOS USUARIOS EXCEPTO SU PROPIETARIO UN MENSAJE
#

    def sendtoall (self, conn, data):
        for i in self.clients:
            if conn is not i:
                i.sendall(data)

#
# MANDA A TODOS LOS USUARIOS UN MENSAJE
#

    def servertoall (self, data):
        for i in self.clients:
            i.sendall(data)

#
# COMANDOS DEL SERVIDOR
#
# help, kick, kickall, online, clear
#

    def servercommand(self):
        while True:

            message = raw_input()

            if message == "/help":
                self.help()
                continue

            elif message == "/online":
                print str(self.clients.__len__())+" users are online!"
                if self.users:
                    for i in self.users:
                        print i+" ",
                    print ""
                continue

            elif message == "/clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue

            elif message == "/kickall":
                self.servertoall("!{Server_Kick}:¿?")
                continue
            try:
                # "/kick <username> <reason>"
                split = message.split(" ",1)
                # ["/kick", "<username> <reason>"]
                command = split[0]

                if command == "/kick":
                    # ["<username>", "<reason>"]
                    split = split[1].split(" ",1)
                    username = split[0]
                    reason = split[1]
                    # Get pos to send the message
                    try:
                        pos = self.users.index(username)
                        kick = "!{Server_Kick}"+":"+reason
                        self.clients[pos].send(kick)
                    except:
                        print WARNING+username+" isn't in the server!"+RESET
                else:
                    print WARNING+"That command doesn't exist!"+RESET
            except:
                print WARNING+"/kick <username> <reason>"+RESET


    def help(self):
        print '\033[93m'+"Commands available: "
        print HELP1+"/online : "+HELP2+"show who is online."
        print HELP1+"/kick <username> <reason> : "+HELP2+"kicks someone from the server"
        print HELP1+"/kickall : "+HELP2+"kicks everyone from the server"
        print HELP1+"/clear : "+HELP2+"clear the screen"+RESET


########################
##     CLIENT SIDE    ##
########################

class Client():

    def __init__(self, ip, port, uname):
        self.exit = False

        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((ip, port))
        except socket.error as serr:
            if serr.errno == errno.ECONNREFUSED:
                print "The server isn't up!"
                exit()
            else:
                raise

        client.send(uname)
        message = client.recv(1024)

        if message == "!{Server_Is_Full}":
            print "Server is full! Try again later..."
            client.close()
            exit()
        elif message == "!{Error_Name_In_Use}":
            print uname+" is already in use. Choose another name."
            client.close()
            exit()
        elif message == "!{Name_Size_Error}":
            print "The name provided is longer than 10 characters"
            client.close()
            exit()

        try:
            self.setname(message, uname)
        except (AttributeError, IndexError):
            print "Error: Couldn't get an username from server."
            exit()
        print message
        message = self.name+" has connected!"
        client.send(message)

        try:
            recthread = Thread(target=self.receive, args=(client,))
            sendthread = Thread(target=self.send, args=(client,))
            recthread.start()
            sendthread.start()
            sendthread.join()
            recthread.join()
        except:
            print "Closing..."
        finally:
            client.close()

#
# Get name from server
#

    def setname(self,message, uname):
        color = re.findall('\033\[[0-9][0-9]m',message)
        self.color = color[0]
        if uname == "None":
            name = re.findall('[A-Z][a-z]*',message)
            self.name = name[1]
        else:
            self.name = uname

#
# Receive messages
#

    def receive(self, client):
        while True:
            message = client.recv(1024)
            if message == "!{Error_Server_OFF}":
                print "Server has disconnected!"
                self.exit = True
                break
            try:
                cmd = message.split(":",1)
                if cmd[0] == "!{Server_Kick}":
                    print "You have been kicked from server! Reason: "+cmd[1]+RESET
                    self.exit = True
                    break

            except:
                print message
                if self.exit:
                    break

#
# Send messages
#

    def send(self, client):
        while True:
            message = raw_input()
            ## Comandos con mensajes en claro, sin colores
            if message == "" and self.exit == False:
                continue
            elif message == "/exit":
                client.send(message)
                self.exit = True
                break
            elif message == "/help":
                self.help()
                continue
            elif message == "/clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            elif message == "/online":
                client.send(message)
                continue
            elif self.exit:
                break
            message = self.color+self.name+":"+RESET+" "+message
            #\033[A ANSII ALLOWS TO "HIDE" THE LINE WROTE BY A USER
            client.send(message)
            print "\033[A"+message

    def help(self):
        print HELP1+"/online : "+HELP2+"show who is online."
        print HELP1+"/msg <username> <text> : "+HELP2+"send a private message to someone"
        print HELP1+"/clear : "+HELP2+"clear the screen"
        print HELP1+"/exit : "+HELP2+"leave chat"+RESET

# action="store_true" utiliza la opción como un bool
# add_mutually_exclusive_group forza a que solo pueda usarse una opción de forma simultánea
# args guarda cada opción de la linea de comandos como un atributo


########
# MAIN #
########

parser = argparse.ArgumentParser(description='TCP chat.')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-s','--server', help='Run program as server', action="store_true")
parser.add_argument('-m','--max', help='Number of connections that the server will support. 10 by default', type=int, default=10)
group.add_argument('-c','--client', help='Run program as client', action="store_true")
parser.add_argument('-u','--user', help='Choose an username.', type=str, default="None")
parser.add_argument('-i','--ip', help='Specify IP address to connect to. Localhost by default', type=str, default="0.0.0.0")
parser.add_argument('-p','--port', help='Choose port. 8080 by default', type=int, default=8080)
args = parser.parse_args()

os.system('cls' if os.name == 'nt' else 'clear')

# Comprobación de argumentos válidos

if args.port > 65535 or args.port < 1024:
    print "Invalid port. Choose one between 1024 and 65535 \n"
    exit()
if args.user != None and args.user.__len__() > 10:
    print args.user+" is too long. Provide an username less than 10 characters"
    exit()
elif args.user.count(" "):
    print args.user+" is invalid. Don't use spaces in your username."
    exit()
if args.max <= 0 or args.max>10:
    print args.max+" is an invalid number! Provide one higher than 0 or one less than 10."
    exit()

if args.client:
    client = Client(args.ip, args.port, args.user)
elif args.server:
    server = Server(args.ip, args.port, args.max)

