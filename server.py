import socket
import threading

HOST = '127.0.0.1'
PORT = 50002

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
nicknames = []
rooms = {}  # key: client, value: room


def broadcast(message, room):
    for client in clients:
        if rooms.get(client) == room:
            try:
                client.send(message.encode('utf-8'))
            except:
                clients.remove(client)
                nicknames.remove(nicknames[clients.index(client)])
                del rooms[client]


def remove_client(index):
    client = clients[index]
    nickname = nicknames[index]
    room = rooms.get(client)

    clients.pop(index)
    nicknames.pop(index)
    del rooms[client]

    broadcast(f"[{room}] {nickname} 👋 has left the chat.", room)


def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            room = rooms.get(client)
            broadcast(message, room)
        except:
            index = clients.index(client)
            client.close()
            nickname = nicknames[index]
            room = rooms.get(client)

            broadcast(f"[{room}] {nickname} 👋 has left the chat.", room)

            clients.remove(client)
            nicknames.remove(nickname)
            del rooms[client]
            break


def receive():
    print("Server Listening.....")
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        
        client.send('ROOM'.encode('utf-8'))
        room = client.recv(1024).decode('utf-8')

        nicknames.append(nickname)
        clients.append(client)
        rooms[client] = room

        print(f"Nickname is {nickname} | Room: {room}")
        broadcast(f"{nickname} joined...!", room)

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


receive()
