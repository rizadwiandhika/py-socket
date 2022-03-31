import os
import socket
import threading
import json
import shutil
from time import sleep

IP_ADDRESS = '127.0.0.1'
PORT = 7000
CHUNK = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((IP_ADDRESS, PORT))
server.listen(socket.SOMAXCONN)

list_of_clients = []
history_chat = []

""" Handler functions """
def list_handler(client, *args):
    """ COMMAND 'LIST' """

    folder = 'storage'

    onlyfiles = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    payload = json.dumps({'type': 'LIST', 'content': onlyfiles})

    client['socket'].send(payload.encode())

def downzip_handler(client, *args):
    """ COMMAND 'DOWNZIP' """

    shutil.make_archive('updated', 'zip', 'storage')
    filesize = os.path.getsize('updated.zip')
    client['socket'].send(json.dumps({'type': 'DOWNZIP', 'size': filesize}).encode())

    sleep(2)

    f = open('updated.zip', 'rb')
    while True:
        l = f.read(CHUNK)
        if not l:
            break
        client['socket'].send(l)
    
    f.close()
    os.remove('updated.zip')

def send_handler(client, *args):
    # ! Belum selesai
    """ COMMAND 'SEND <file>' """

    print('Recieving file...')
    accumulator = int(0)
    f = open('client.zip', 'wb')

    size = data['size']

    while accumulator < size:
        print('acc', accumulator)
        data = sock.recv(CHUNK)
        accumulator += f.write(data)

    f.close()
    print('Recieved!')

def log_handler(client, *args):
    """ COMMAND LOG """

    client['socket'].send(json.dumps({'type': 'LOG', 'content': history_chat}).encode())

def chat_handler(client, content):
    """ COMMAND CHAT (default command) """

    history_chat.append('{}: {}\n'.format(client['name'], content))
    message = '<{}> {}\n'.format(client['name'], content)

    """ Kirim ke semua client (kecuali dirinya sendiri) """
    broadcast(client, json.dumps({'type': 'CHAT', 'content': message}))

HANDLE_COMMAND = {
    'LIST': list_handler,
    'DOWNZIP': downzip_handler,
    'SEND': send_handler,
    'LOG': log_handler,
    'CHAT': chat_handler
}

""" Thread untuk client (setiap koneksi client mendapatkan threadnya masing2) """
def clientthread(client):
    while True:
        try:
            """ Terima pesan dari clent """
            message = client['socket'].recv(CHUNK)
            if not message:
                print('\n\nClient disconnected\n\n')
                remove(client)
                continue

            """ Handle request client sesuai dengan command yang diberikan """
            message = message.decode()
            command, content = extract_command(message)
            print(command + '-apa')
            HANDLE_COMMAND[command](client, content)

        except:
            continue


def extract_command(message):
    content = ' '.join(message.split(' ')[1:])

    if message.startswith('LIST'):
        return 'LIST', content
    if message.startswith('DOWNZIP'):
        return 'DOWNZIP', content
    if message.startswith('SEND'):
        return 'SEND', content
    if message.startswith('LOG'):
        return 'LOG', content

    return 'CHAT', message

def broadcast(initiator, message):
    for client in list_of_clients:
        if client['socket'] != initiator['socket']:
            try:
                client['socket'].send(message.encode())
            except:
                client['socket'].close()
                remove(client)

def remove(client):
    if client in list_of_clients:
        client['socket'].close()
        list_of_clients.remove(client)

""" MAIN FUNCTION HERE """
count = 1
while True:
    print('Waiting for connection...')

    """ Simpan informasi koneksi client dalam dictionary """
    conn, addr = server.accept()
    client = {
        'socket': conn,
        'addr': addr,
        'name': 'Person {}'.format(count)
    }
    list_of_clients.append(client)

    print(addr[0] + ' connected!\n')

    """ Buat thread untuk client """
    threading.Thread(target=clientthread, args=(client,)).start()
    count += 1

conn.close()