import socket
import keyboard
import cv2
import numpy as np

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('127.0.0.1', 9998))

# cv2.namedWindow('Screen', cv2.WINDOW_NORMAL)
# cv2.setWindowProperty('Screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while not keyboard.is_pressed('f12'):
    data = sock.recv(22_118_400)
    if data:
        if data == b'close':
            sock.close()
            break

        img = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        try:
            cv2.imshow('screen', img)
            sock.send(b'done')
            cv2.waitKey(1)
        except cv2.error:
            sock.send(b'done')
            print('wrong image')

sock.close()
cv2.destroyAllWindows()
