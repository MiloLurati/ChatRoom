# UDP chat client by Milo & Zain
####################################################################################################################
import socket
import threading
import time
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)
global serverAddress    
serverAddress = ("3.121.226.198", 5382)

##############- FUNCTIONS -########################################################################################

def byteStringToBinaryArray(bytes):
    binaryArray = []
    for i in bytes:
        b = bin(i).replace("0b", "")
        if len(b) != 8:
            j = 0
            bLenght = len(b)
            while j < (8 - bLenght):
                b = "0" + b
                j += 1
        binaryArray.append(b)
    return binaryArray

def binaryToByteString(bits):
    byteString = b''
    bitLenght = len(bits)
    byteLenght = bitLenght / 8
    i = 0
    while i < byteLenght:
        byte = int(bits[(i * 8):((i * 8) + 8)], 2)
        byteString = byteString + byte.to_bytes(1, "big")
        i += 1
    return byteString

def errorChecking(msg):
    msg.replace(b'\n', b'')
    msg = msg[:-6]
    msgToCheckList = msg.split()[2:]
    msgToCheck = msgToCheckList[0]
    i = 1
    while i < len(msgToCheckList):
        msgToCheck = msgToCheck + b' ' + msgToCheckList[i]
        i += 1
    msgToCheckBinary = byteStringToBinaryArray(msgToCheck)
    i = 0
    while i < 8:
        even = True
        for j in msgToCheckBinary:
            if j[i] == "1":
                even = not even
        if not even:
            return True
        i += 1
    return False

def checkSequenceNumber(msg):
    msg.replace("\n", "")
    hexWithZeros = msg[-12:]
    hex = ""
    i = 0
    while i < len(hexWithZeros):
        if hexWithZeros[i] == "0" and hexWithZeros[i + 1] == "x":
            hex = hexWithZeros[i:]
            break
        i += 1
    if sequenceNumberList[int(hex, 16)] == False:
        sequenceNumberList[int(hex, 16)] = True
        return True
    else:
        return False

def withChecksum(msg):
    checksum = ""
    msgUtf8 = msg.encode("utf-8")
    msgBinaryArray = byteStringToBinaryArray(msgUtf8)
    i = 0
    while i < 8:
        even = True
        for j in msgBinaryArray:
            if j[i] == "1":
                even = not even
        if even:
            checksum = checksum + "0"
        else:
            checksum = checksum + "1"
        i += 1
    msgBinaryArray.append(checksum)
    msgWithChecksum = ""
    for m in msgBinaryArray:
        msgWithChecksum = msgWithChecksum + m
    msgWithChecksum = binaryToByteString(msgWithChecksum)
    return msgWithChecksum.decode("utf-8")

def withSequenceNumber(msg, sequenceNumberGenerator):
    msg.replace("\n", "")
    zerosToAdd = 5 - len(hex(sequenceNumberGenerator))
    z = 0
    while z < zerosToAdd:
        msg += "0"
        z += 1
    msg += hex(sequenceNumberGenerator)
    return msg

def reciveMessageThread():
    global commandWho
    global commandSend
    global commandSet
    global threadControl
    threadControl = True

    while threadControl:
        data = b''
        try:
            data, address = sock.recvfrom(20000)
            dataDecoded = data.decode("utf-8")
        except socket.timeout:
            continue
        except UnicodeDecodeError:
            print("Error detected in incomming message!")
            continue
        if not data:
            continue
        elif "\n" not in dataDecoded:
            continue
        elif "HELLO" in dataDecoded:
            continue
        elif "WHO-OK" in dataDecoded:
            print(dataDecoded[len(dataDecoded.split()[0]) + 1:])
            commandWho = False
        elif "BAD-RQST-BODY" in dataDecoded:
            print("Bad request body.")
            commandSet = False
            commandSend = False
            commandWho = False
        elif "BAD-RQST-HEADER" in dataDecoded:
            print("Bad request header.")
            commandSet = False
            commandSend = False
            commandWho = False
        elif "DELIVERY" in dataDecoded and not errorChecking(data) and checkSequenceNumber(dataDecoded):
            print(dataDecoded[:-7])
        elif "DELIVERY" in dataDecoded and errorChecking(data):
            print("Error detected in incomming message by " + dataDecoded.split()[1])
        elif "SET-OK" in dataDecoded:
            print(dataDecoded)
            commandSet = False
        elif "VALUE" in dataDecoded:
            print(dataDecoded)
            commandSet = False
        elif "SEND-OK" in dataDecoded:
            print(dataDecoded)
            commandSend = False
        elif "ERROR-DETECTION" in dataDecoded:
            print(dataDecoded)

def sequnceMsgNumberTimeToLive():
    global threadControlSequenceNumbers
    global sequenceNumberList
    threadControlSequenceNumbers = True
    sequenceNumberList = [False for i in range(256)] # 8 bit sequence = 2^8 different sequence numbers
    while threadControlSequenceNumbers:
        time.sleep(32)
        sequenceNumberList = [False for i in range(256)]


##############- HANDSHAKE PROTOCOL WHILE LOOP -###############################################################################

usernameState = True
while usernameState:
    ackState = True
    global username
    username = input("Username: ")
    if username == "!quit":
        sock.close()
        sys.exit(0)
    helloFromMsg = ("HELLO-FROM " + username + "\n").encode("utf-8")
    header = username.split()[0]
    while ackState:
        sock.sendto(helloFromMsg, serverAddress)
        try:
            ackMsg, address = sock.recvfrom(20000)
        except socket.timeout:
            print("Problem with handshake protocol, try again.")
            break
        ackMsgDecoded = ackMsg.decode("utf-8")
        if ackMsgDecoded == "IN-USE\n":
           print("Username is taken please try again.")
           ackState = False
        elif ackMsgDecoded == "BUSY\n":
            print("Server reached limit!")
            ackState = False
        elif ackMsgDecoded == "BAD-RQST-BODY\n":
            print("Bad request body. Username may have unsupported characters")
            ackState = False
        elif header == "SET" or header == "GET" or header == "RESET":
            sock.sendto(command.encode("utf-8"), serverAddress)
            ackState = False
        else:
            print(ackMsgDecoded)
            ackState = False
            usernameState = False

##############- MAIN WHILE LOOP -###############################################################################

rcvMsgThread = threading.Thread(target=reciveMessageThread, daemon=True)
sequnceMsgNumberTimeToLiveThread = threading.Thread(target=sequnceMsgNumberTimeToLive, daemon=True)
rcvMsgThread.start()
sequnceMsgNumberTimeToLiveThread.start()

global sequenceNumberGenerator
sequenceNumberGenerator = 0

try:
    while True:
        commandWho = True
        commandSend = True
        commandSet = True
        threadControl = True
        threadControlSequenceNumbers = True
        sendToCounter = 0
        command = input()
        header = command.split()[0]
        if command == "!quit":
            sock.close()
            sys.exit(0)
        elif command == "!who":
            msg = "WHO\n"
            while commandWho:
                sock.sendto(msg.encode("utf-8"), serverAddress)
                sendToCounter += 1
                time.sleep(0.5)
                if sendToCounter > 15:
                    print("Not able to comunicate with server, please try again or restart the connection!")
                    break
        elif command[0] == "@":
            userCmd = command.split()[0]
            username = userCmd[1:]
            msg = command[len(userCmd) + 1:]
            msg = withSequenceNumber(withChecksum(msg), sequenceNumberGenerator)
            while commandSend:
                sock.sendto(("SEND " + username + " " + msg + "\n").encode("utf-8"), serverAddress)
                sendToCounter += 1
                time.sleep(0.1)
                if sendToCounter > 100:
                    print("Not able to comunicate with server, please try again or restart the connection!")
                    break
            if sequenceNumberGenerator == 256:
                sequenceNumberGenerator = 0
            else:
                sequenceNumberGenerator += 1
        elif header == "SET" or header == "GET" or header == "RESET":
            while commandSet:
                sock.sendto(command.encode("utf-8") + b'\n', serverAddress)
                sendToCounter += 1
                time.sleep(0.5)
                if sendToCounter > 15:
                    print("Not able to comunicate with server, please try again or restart the connection!")
                    break
        else:
            print("Command unidentified")
except KeyboardInterrupt as msg:
    threadControl = False
    threadControlSequenceNumbers = False
    sock.close()
    print(msg)

# The UDP Chat Client program, is made of two main while loops and eight functions. The first loop executes the 
# handshake protocol and the second loop executes all the different features required. As the assignment demanded, 
# we implemented UDP with the socket module, and used threads, with the threading module, to manage different 
# incoming and outgoing data at the same time. The second loop sends the different messages and commands to the 
# server, and a thread, that executes the function “reciveMessageThread()”, receives the incoming messages and 
# acknowledgments from the sever.
# The second loop is divided in three main parts. Each part executes a loop until it receives an acknowledgment 
# message. The first part executes the “!who” command, the second the “@” command, and the third executes the 
# “SET”, “GET” and “RESET” command. Each sections keeps looping until the “reciveMessageThread()” function 
# receives its corresponding acknowledgement message that through a global Boolean variable terminates the loop, 
# or until a counter (“sendToCounter”), that increments at each iteration, reaches a certain limit.
# Before sending the message to the server, that came along the “@” command, we pass this message to two different 
# functions. The first function, called “withChecksum(msg)”, calculates and adds a parity checksum to the message 
# for error detection once the full packet reaches destination. The second function, called 
# “withSequenceNumber(msg)”, adds to the end of the packet a number in hexadecimal that prevent duplicates in 
# case of a delay in the transmission.
# On the receiver side, we have the function “reciveMessageThread()” that executes on a separate thread. This 
# function is coded on a loop that keeps iterating. If it receives a message on the socket, it identifies the 
# type and acts upon it, if not, the socket has a timeout that gets catched by an exception that makes the loop 
# continue its iterations. If it identifies a message with the command “DELIVERY”, it checks for errors with the 
# function “errorChecking(data)”. The function will detect and error if it finds a sum of bits that is not even. 
# If there are no errors, the code will send the message to “checkSequenceNumber(data)” that checks if the 
# sequence number is not equal to a recent message sent. It does this process by check a Boolean array at the 
# position of the sequence number. This Boolean array gets reset to all false each 32 seconds. This is done on 
# another thread that executes the function sequnceMsgNumberTimeToLive(). If the sequence number has not been 
# used in the last 32 seconds, the function “reciveMessageThread()”, will print the message without the checksum 
# and the sequence number.
# The last two function convert data between bits and bytes. These two functions are called 
# “byteStringToBinaryArray(bytes)” and “binaryToByteString(bits)”.