import socket
import os
import json
import random
import sys
from threading import Thread
from time import sleep

""" Set up socket"""
IP_ADDRESS = '127.0.0.1'
PORT = 7000
CHUNK = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect((IP_ADDRESS, PORT))

""" Thread untuk mengirim pesan ke server """
def send_msg(sock):
    while True:
        """ Menerima Input command user """
        data = input('Input >> ')

        """ Jika commandnya itu selain SEND, maka langsung kirim commandnya ke server """
        if not data.startswith('SEND'):
            sock.send(data.encode())
            continue

        """ Jika command adalah SEND, lakukan persiapan untuk streaming file ke server """
        filepath = data.split(' ')[1]
        # check file exist
        if not os.path.isfile(filepath):
            print('File not found!')
            continue

        # send file size
        sock.send(json.dumps({
            'type': 'SEND', 
            'size': os.path.getsize(filepath),
            'name': os.path.basename(filepath)
        }).encode())

        sleep(2)

        f = open(filepath, 'rb')
        while True:
            l = f.read(CHUNK)
            if not l:
                break
            sock.send(l)
        
        f.close()

""" Thread untuk menerima pesan dari server """
def recv_msg(sock):
    while True:
        """ Terima informasi meta dari server (untuk menentukan tipe pesan apa yang dikirim server) """
        data = sock.recv(CHUNK)
        if not data:
            print('Server closed!')
            sock.close()
            break

        sys.stdout.write('\r')
        data = json.loads(data.decode())

        """ Tangani response sesuai dengan commandnya """
        if data['type'] == 'CHAT' or data['type'] == 'LIST':
            print(data['content'])
        elif data['type'] == 'LOG':
            print(data['content'])
            f = open('log-{}.txt'.format(random.randint(1, 1000)), 'w')
            f.write(json.dumps(data['content']))
            f.close()
        elif data['type'] == 'DOWNZIP':
            print('Downloading file...')
            accumulator = int(0)
            f = open('client.zip', 'wb')

            size = data['size']

            while accumulator < size:
                print('acc', accumulator)
                data = sock.recv(CHUNK)
                accumulator += f.write(data)

            f.close()
            print('Downloaded!')
        sys.stdout.write('\n')


""" Menjalankan thread untuk mengirim dan menerima pesan menuju/dari server """
Thread(target=send_msg, args=(server,)).start()
Thread(target=recv_msg, args=(server,)).start()

while True:
    pass
