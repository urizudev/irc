import socket
import threading
import os
import glob
import importlib.util

host = "localhost"
port = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

# Load plugins
plugin_folder = "plugins"
plugin_files = glob.glob(os.path.join(plugin_folder, "*.py"))
plugins = []

for plugin_file in plugin_files:
    plugin_name = os.path.splitext(os.path.basename(plugin_file))[0]
    spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "SamplePlugin"):  # Check if the plugin defines a SamplePlugin class
        plugins.append(module.SamplePlugin())

for plugin in plugins:
    plugin.on_load()

def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except Exception as e:
            print(f"An error occurred while broadcasting: {e}")
            remove(client)

def handle(client):
    try:
        while True:
            message = client.recv(1024)
            if not message:
                remove(client)
                break
            msg_str = message.decode('ascii')
            if msg_str.startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg_str[5:]
                    kick_user(name_to_kick)
                else:
                    client.send('Command Refused!'.encode('ascii'))
            elif msg_str.startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg_str[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned by the Admin!')
                else:
                    client.send('Command Refused!'.encode('ascii'))
            else:
                broadcast(message)
    except Exception as e:
        print(f"An error occurred in the handle function: {e}")
        remove(client)

def remove(client):
    if client in clients:
        index = clients.index(client)
        nickname = nicknames[index]
        clients.remove(client)
        client.close()
        nicknames.remove(nickname)
        broadcast(f'{nickname} left the Chat'.encode('ascii'))

def receive():
    try:
        while True:
            client, address = server.accept()
            print(f"Connected with {str(address)}")
            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            with open('bans.txt', 'r') as f:
                bans = f.readlines()

            if nickname + '\n' in bans:
                client.send('BAN'.encode('ascii'))
                client.close()
                continue

            if nickname == 'admin':
                client.send('PASS'.encode('ascii'))
                password = client.recv(1024).decode('ascii')
                if password != 'blockbyeadminLOOL':
                    client.send('REFUSE'.encode('ascii'))
                    client.close()
                    continue

            nicknames.append(nickname)
            clients.append(client)

            print(f'Nickname of the client is {nickname}')
            broadcast(f'{nickname} joined the Chat'.encode('ascii'))
            client.send('Connected to the Server!'.encode('ascii'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
    except Exception as e:
        print(f"An error occurred in the receive function: {e}")

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You Were Kicked from Chat!'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked from the server!'.encode('ascii'))

print('Server is Listening ...')
receive()
