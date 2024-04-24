import logging
import socket
import keyboard
import cv2
import numpy as np
import time

logging.basicConfig(level=logging.DEBUG)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 9998))

WINDOW_SIZE = (1280, 720)

# cv2.namedWindow('Screen', cv2.WINDOW_NORMAL)
# cv2.setWindowProperty('Screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
prev_image = None
while not keyboard.is_pressed('f12'):
    # len_img = sock.recv(8)
    data = b''
    while True:
        packet = sock.recv(65536)
        logging.debug(len(packet))
        if packet.endswith(b'Q'):
            data += packet.rstrip(b'Q')
            break
        data += packet
    # logging.debug(f'{data.find(b"S")} -> {data.find(b"Q")}')
    try:
        logging.debug(f'LS {data.find(b"LS")} - LQ {data.find(b"LQ")}')
        logging.debug(f'DS {data.find(b"DS")} - DQ {data.find(b"DQ")}')
        len_img = int(data[data.find(b'LS') + 2:data.find(b'LQ')])
        data = data[data.find(b'DS') + 2:data.find(b'DQ')]
        logging.info(f'frame received: {len(data)} bytes of {len_img}')
        packet_loss = 1 - (len(data) / len_img)
        logging.info(f'packet loss: {packet_loss}')
    except ValueError:
        packet_loss = 0.1
    sock.sendall(b'PS' + bytes(str(packet_loss), encoding='utf-8') + b'PQ')
    if packet_loss < 0.1:
        if data:
            if data == b'close':
                sock.close()
                break
            st = time.time()
            img = np.frombuffer(data, dtype=np.uint8)
            img = cv2.imdecode(img, cv2.IMREAD_COLOR)
            logging.debug(time.time() - st)
            # sock.send(b'done')
            logging.debug(time.time() - st)
            try:
                img = cv2.resize(img, WINDOW_SIZE)
                cv2.imshow('screen', img)
                # sock.send(b'done')
                cv2.waitKey(1)
                logging.debug(f'update prev_image {len(img)}')
                prev_image = img
            except Exception as e:
                if prev_image is not None:
                    img = cv2.resize(prev_image, WINDOW_SIZE)
                    cv2.imshow('screen', prev_image)
                    cv2.waitKey(1)
                # sock.send(b'done')
                logging.error('wrong image')
                logging.error(e)
                # time.sleep(3)

sock.close()
cv2.destroyAllWindows()
