#!/usr/bin/env python
import socket, sys, select

HOST = ''
PORT = 9009
BUFFER_SIZE = 4096
SOCKET_LIST = []

def chat_server():
    # Using IPv4 and TCP protocl
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

    server_socket.bind((HOST,PORT))
    server_socket.listen(5)

    # adding server socket to the list of all available sockets
    SOCKET_LIST.append(server_socket)

    print "Chat server started on port " + str(PORT)

    while True:
        # select funtion return a list of sockets that are ready to read, we also set the time out to 0 so that it will never block
        ready_to_read,ready_to_write_,in_error = select.select(SOCKET_LIST, [],[],0)

        for s in ready_to_read:

            if s == server_socket: # means a new client is trying to join
                new_sock, addr = server_socket.accept()
                SOCKET_LIST.append(new_sock)

                print "Client (%s, %s) connected." % addr
                broadcast(server_socket, new_sock, "[%s:%s] just joined the room!\n" % addr)
            else:
                try:
                    data = s.recv(BUFFER_SIZE)

                    if data:
                        # broadcast the data to all other client sockets
                        broadcast(server_socket, s, "\r" + '[' + str(s.getpeername()) + '] ' + data)
                    else:
                        # may have a connection problem, so we remove the client socket
                        if s in SOCKET_LIST:
                            SOCKET_LIST.remove(s)

                        # broadcast a message to other clients informing that this client has left
                        broadcast(server_socket, s, "Client (%s, %s) is offline\n" % addr)

                except:
                    broadcast(server_socket, s, "Client (%s, %s) is offline\n" % addr)
                    # print "Client (%s,%s) is offline"%addr
                    # s.close()
                    # SOCKET_LIST.remove(s)
                    continue

    server_socket.close()

def broadcast(server_socket, sock, message):
    """ Broadcasts chat message to all peers

    Args:
        server_socket: the server socket
        sock: the client socket sending the message
        message: the actual chat message
    """

    for socket in SOCKET_LIST:
        # send the message only to the peers
        if socket != server_socket and socket != sock:
            try:
                socket.send(message)
            except:
                # perhaps disconnected
                socket.close()

                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)

if __name__ == "__main__":
    sys.exit(chat_server())
