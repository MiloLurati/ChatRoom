# ChatRoom
## Chat Client
In this assignment, you implement a text-based chat client. For this, you use Python, sockets, and
the Transmission Control Protocol (TCP). Once you are comfortable using the socket interface, using
sockets in other programming languages should be straightforward.3 After completing this assignment,
you will be able to exchange messages with your fellow students using your own client.
The chat client and chat server are built on top of TCP and use their own application-layer protocol.
This means the client and server can request the other to perform actions by sending predefined types
of messages. For example, your client can ask the server to forward a message to another user’s client
by sending the string “SEND username insert your message here\n” to the server, where “username”
is the user to whom you want to send your message. If your message is correct, the server will
send two messages: one to the destination user, forwarding your message, and one back to you that
says “SEND-OK\n”, to notify you that your message was forwarded successfully.4 The full details of the
protocol are listed in Appendix A.
Similar to Web browsers and other modern applications, your chat client does not expose the protocol
it uses to the user. Instead, it provides a user-friendly text-based interface that makes it easy for users
to chat with others without knowing the protocol specifications. The specifications of this interface, and
the requirements of this assignment, are listed below.
## Chat Server
This server connects multiple clients and forwards messages between them. In this assignment, you implement your own
chat server using the same protocol. Unlike the client, the server is likely to have multiple open connections at the same time—one for
each client that is connected to it. Because it is impossible to predict when a client will send a request
or message, your server needs to keep checking all connections for incoming data. Both polling and
multi-threading are allowed as solutions to this problem.
## Appendix A
![image](https://user-images.githubusercontent.com/70884255/125481678-1564be24-e7d3-4bb7-96dd-93ab2851f12a.png)
