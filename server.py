import logging
import numpy as np
import cv2
import pyautogui
import socket
import dxcam
import time
import keyboard

logging.basicConfig(level=logging.DEBUG)


def get_frame(cm, size_x: int = 1280, size_y: int = 720, cursor: bool = True) -> np.ndarray or None:
    frame = cm.grab()
    if frame is None:
        return None
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (size_x, size_y))
    if cursor:
        frame = add_cursor(frame)
    return frame


def add_cursor(image: np.ndarray, cursor_size: int = 3, thickness: int = 1) -> np.ndarray:
    screen_size = pyautogui.size()
    x, y = pyautogui.position()
    x = int(x * image.shape[1] / screen_size[0])
    y = int(y * image.shape[0] / screen_size[1])
    cv2.line(image, (x - cursor_size, y), (x + cursor_size, y), (255, 255, 255), thickness)
    cv2.line(image, (x, y - cursor_size), (x, y + cursor_size), (255, 255, 255), thickness)
    return image


class Sock:
    def __init__(self, host: str, port: int, listen: int) -> None:
        self.s = socket.socket()
        self.s.bind((host, port))
        self.s.listen(listen)
        self.conn, self.addr = self.s.accept()
        logging.info(f'connected: {self.addr}')

    def send_data(self, dt: bytes) -> None:
        self.conn.sendall(dt)

    def recv(self, size: int = 1024) -> bytes:
        return self.conn.recv(size)

    def close(self) -> None:
        self.conn.sendall(b'close')
        self.conn.close()


if __name__ == '__main__':
    loop_time = time.time()
    camera = dxcam.create()
    s = Sock('0.0.0.0', 9998, 1)
    fps = 120
    quality = 90
    while not keyboard.is_pressed('f12'):
        img_time = time.time()
        img = get_frame(camera, cursor=True)
        if img is None:
            continue
        logging.debug(f'frame {time.time() - img_time}')

        comp_time = time.time()
        # quality = min(70, int(fps * 0.5))
        logging.info(f'quality {quality}')

        ret, jpeg = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        data = jpeg.tobytes()
        logging.debug(f'compression {time.time() - comp_time}')

        send_time = time.time()
        # logging.debug(f'size {len(data)} | packets {round(len(data) / 8192)}')
        s.send_data(str(len(data)).encode('utf-8'))
        s.send_data(b'S')
        s.send_data(data)
        s.send_data(b'Q')
        packet_loss = float(s.recv(1024).decode('utf-8'))
        logging.error(f'packet loss: {packet_loss}')
        logging.debug(f'send {time.time() - send_time}')

        try:
            fps = 1 / (time.time() - loop_time)
            logging.info(f'FPS {fps} ({time.time() - loop_time})')
        except ZeroDivisionError:
            # too much fps lol
            pass
        loop_time = time.time()
        # time.sleep(5)
    s.close()
