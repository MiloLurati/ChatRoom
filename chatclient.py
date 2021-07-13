import socket
import threading

def printFormat(recv_data):
    response = recv_data.split()[0]
    if response == "SEND-OK":
        pass
    elif response == "WHO-OK":
        res_len = len(response)+1
        print(recv_data[res_len:])
    elif response == "UNKNOWN":
        print("Requested user does not exist or is currently offline")
    elif response == "BAD-RQST-BODY":
        print("ERROR: bad request body")
    elif response == "BAD-RQST-HDR":
        print("ERROR: bad request Header")
    else:
        print(recv_data)

def reciveMessage():                                                            #Listen for messages from the server
    recv_data = ""

    while True:
        data = sock.recv(1).decode("utf-8")
        if not data:
            t.join()
            sock.close()
            break
        else:
            if '\n' in data:
                recv_data += data
                printFormat(recv_data)
                recv_data = ""
            else:
                recv_data += data

t = threading.Thread(target= reciveMessage, daemon=True)                       #Create a daemon thread


while True:                                                                     #Begin the program
    username = input("Username: ")                                              
    if username == '!quit':                                                     #Quits program if input = !quit
        break

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                #Creates a socket

        host_port = ("127.0.0.1", 60476)                                     
        sock.connect(host_port)                                                 #Connects to server host_port
        string_bytes = ("HELLO-FROM " + username + "\n").encode("utf-8")
    
        sock.sendall(string_bytes)                                              #Sends first handshake

        data = sock.recv(4096).decode("utf-8")                                  #Recieves server response (2nd handshake)
        if data == "IN-USE\n":                                                  #Conditionals for potential respones
            print("Username is taken please try again.")
            sock.close()
        elif data == "BUSY\n":
            print("Server reached limit!")
            sock.close()
        elif data == "BAD-RQST-BODY\n":
            print("Bad request body. Username may have unsupported characters")
            sock.close()
        else:
            break
    except OSError as msg: 
        print(msg)
        continue

print(data)                                                                      #Prints server response
t.start()                                                                        #Run the daemon thread

while True:                                                                      #Begin communicating with server and users
    try:
        command = input()                                                        #User command Input
        if command != '':
            if command == '!quit':                                                   #Quits program if input = !quit
                sock.close()
                break
            elif command == '!who':                                                  #Ask for list of online users if input = !who
                message = ("WHO\n").encode('utf-8')
                sock.sendall(message)
            elif command[0] == '@':                                                  #Send message to a user if input = @
                user = command.split()[0]                                            #Gets the user name as '@username'
                message = command[len(user):]                                        #Gets the message to send
                name = user[1:]                                                      #Removes the @ from the username
                commandSend = ("SEND " + name + " " + message + "\n").encode("utf-8")
                sock.sendall(commandSend)
            else:
                print("Command unidentified")               
                continue
        else:
            print("Please input a command")               
            continue

    except OSError as msg: 
        print(msg)