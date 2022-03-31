import json
import socket
import sys
import os

ip = "127.0.0.1"
port = 8000
filepath = "./Kuliah01 - Review Jarkom dan Pengenalan Python.pdf"

if os.path.isfile(filepath) == False:
  print("File does not exist")
  sys.exit(0)

server_address = (ip, int(port))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

# Send filename first
meta = {
    "filename": os.path.basename(filepath),
    "size": os.path.getsize(filepath)
}
client_socket.send(json.dumps(meta).encode())

while True:
    while input('continue (y/n) > ') != 'y':
        pass

    file = open(filepath, 'rb')
    content = file.read(1024)
    while content:
        client_socket.send(content)
        content = file.read(1024)

        # client_socket.shutdown(socket.SHUT_WR)
        # client_socket.close()
    file.close()

sys.exit(0)