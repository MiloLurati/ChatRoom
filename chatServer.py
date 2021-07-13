import socket
import _thread
import re

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverPort = ("127.0.0.1", 60476)
server.bind(serverPort)
server.listen(70)
listClients = {}
listUsername = []
print("Server online, begin accepting user at port: 60476")
def checkPunctuation(username):
    stringCheck = re.compile('[@_!#$%^&*()<>?/\|}{~:]')

    if (stringCheck.search(username) == None):
        return False
    else:
        return True

def messageHandler(message, senderUser):
    header = message.split()[0]

    if header == "SEND":
        username = message.split()[1]
        if username in listUsername:
            recieverUser = listClients[username]
            conj = " "
            msg = conj.join(message.split()[2:])
            userMsg = ("DELIVERY " + senderUser + " " + msg + "\n").encode("utf-8")
            recieverUser.sendall(userMsg)
            SEND = "SEND-OK\n".encode("utf-8")
            return SEND
        else:
            SEND = "UNKNOWN\n".encode("utf-8")
            return SEND        
    elif header == "WHO":
        seperator = ", "
        users = "WHO-OK " + seperator.join(listUsername) + "\n"
        SEND = users.encode("utf-8")
        
        return SEND
    else:
        SEND = "BAD-RQST-HDR\n".encode("utf-8")
        return SEND



def newClientThread(connection, adress):
    message = connection.recv(2048).decode("utf-8")
    header = message.split()[0]
    messageLenght = len(message.split())
    username = message.split()[1]
    
    if header == "HELLO-FROM" and messageLenght == 2 and not checkPunctuation(username):
        for client in listUsername:
            if client == username:
                connection.send("IN-USE\n".encode("utf-8"))
                connection.close()
                return
        listClients[username] = connection 
        listUsername.append(username)
        print("User: " + username + " is online")
        connection.send(("HELLO " + username).encode("utf-8"))
        
    else:
        connection.send("BAD-RQST-HDR\n".encode("utf-8"))
        connection.close()
        return
    recvMessage = ""
    while True:
        try:
            message = connection.recv(1024).decode("utf-8")
            if not message:
                listClients.pop(username)
                listUsername.remove(username)
                print("User: " + username + " is offline")
                connection.close()
                break
            else:
                if '\n' in message:
                    recvMessage += message
                    senderUser = username
                    connection.send(messageHandler(recvMessage, senderUser))
                    recvMessage = ""
                else:
                    recvMessage += message
        except:
            listClients.pop(username)
            listUsername.remove(username)
            print("User: " + username + " is offline")
            connection.close()

while True:
    try:
        connection, address = server.accept()
        _thread.start_new_thread(newClientThread, (connection, address))
    except:
        server.close()
        break
