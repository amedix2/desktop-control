import logging
import socket
import keyboard
import cv2
import pickle
import numpy as np


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 9998))

# cv2.namedWindow('Screen', cv2.WINDOW_NORMAL)
# cv2.setWindowProperty('Screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while not keyboard.is_pressed('f12'):
    logging.info('waiting size')
    data_size = sock.recv(1024)
    sock.send(b'got')
    logging.info(f'data size {data_size}')
    data_size = pickle.loads(data_size)
    data = b''
    while len(data) < data_size:
        logging.debug(f'packet received')
        packet = sock.recv(data_size - len(data))
        logging.debug(f'packet size {len(packet)}')
        if not packet:
            break
        data += packet
    logging.info(f'data size received {len(data)}')
    img = pickle.loads(data)
    sock.send(b'done')
    try:
        cv2.imshow('screen', img)
        cv2.waitKey(1)
    except cv2.error:
        print('wrong image')

sock.close()
cv2.destroyAllWindows()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
