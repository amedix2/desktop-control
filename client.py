import logging
import socket
import keyboard
import cv2
import numpy as np
import time

logging.basicConfig(level=logging.INFO)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 9998))

# cv2.namedWindow('Screen', cv2.WINDOW_NORMAL)
# cv2.setWindowProperty('Screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
prev_image = None
while not keyboard.is_pressed('f12'):
    len_img = int(sock.recv(8).decode('utf-8'))
    data = b''
    while True:
        packet = sock.recv(65536)
        data += packet
        logging.debug(len(packet))
        if packet.endswith(b'Q'):
            data += packet.rstrip(b'q')
            break
    data = data[data.find(b'S') + 1:]
    logging.info(f'frame received: {len(data)} bytes of {len_img}')
    packet_loss = 1 - (len(data) / len_img)
    logging.info(f'packet loss: {packet_loss}')
    sock.sendall(str(packet_loss).encode('utf-8'))
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
            cv2.imshow('screen', img)
            # sock.send(b'done')
            cv2.waitKey(1)
            logging.info(f'update prev_image {len(img)}')
            prev_image = img
        except Exception as e:
            if prev_image is not None:
                cv2.imshow('screen', prev_image)
                cv2.waitKey(1)
            # sock.send(b'done')
            logging.error('wrong image')
            logging.error(e)
            time.sleep(3)

sock.close()
cv2.destroyAllWindows()
