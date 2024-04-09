import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 9999))
while True:
    data = sock.recv(1024)
    if data:
        if data == b'close':
            sock.close()
            break
        print(data)
