import logging
import socket
import keyboard
import cv2
import pickle
import numpy as np


logging.basicConfig(level=logging.INFO)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 9998))

# cv2.namedWindow('Screen', cv2.WINDOW_NORMAL)
# cv2.setWindowProperty('Screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

last_key_frame = None
i = 0
interval = 4
while not keyboard.is_pressed('f12'):
    data_size = sock.recv(1024)
    data_size = pickle.loads(data_size)
    logging.info(f'data size {data_size}')
    sock.send(b'got')
    data = sock.recv(data_size)
    # while len(data) < data_size:
    #     logging.debug(f'packet received')
    #     packet = sock.recv(data_size - len(data))
    #     logging.debug(f'packet size {len(packet)}')
    #     if not packet:
    #         break
    #     data += packet
    logging.info(f'data size received {len(data)}')
    img = pickle.loads(data)
    if i % interval == 0:
        last_key_frame = img
    else:
        delta_frame = cv2.bitwise_and(last_key_frame, img)
        last_key_frame = cv2.add(last_key_frame, delta_frame)
        img = last_key_frame
    i += 1
    sock.send(b'done')
    try:
        cv2.imshow('screen', img)
        cv2.waitKey(1)
    except cv2.error:
        print('wrong image')

sock.close()
cv2.destroyAllWindows()
