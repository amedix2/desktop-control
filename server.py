import logging
import numpy as np
import cv2
import pyautogui
import socket
import dxcam
import time
import keyboard
import pickle


logging.basicConfig(level=logging.INFO)


def get_frame(
        cm, size_x: int = 1280, size_y: int = 720, cursor: bool = True
) -> np.ndarray or None:
    frame = cm.grab()
    if frame is None:
        return None
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (size_x, size_y))
    if cursor:
        frame = add_cursor(frame)
    return frame


def add_cursor(
        image: np.ndarray, cursor_size: int = 3, thickness: int = 1
) -> np.ndarray:
    screen_size = pyautogui.size()
    x, y = pyautogui.position()
    x = int(x * image.shape[1] / screen_size[0])
    y = int(y * image.shape[0] / screen_size[1])
    cv2.line(
        image,
        (x - cursor_size, y),
        (x + cursor_size, y),
        (255, 255, 255),
        thickness,
    )
    cv2.line(
        image,
        (x, y - cursor_size),
        (x, y + cursor_size),
        (255, 255, 255),
        thickness,
    )
    return image


class Sock:
    def __init__(self, host: str, port: int, listen: int) -> None:
        self.s = socket.socket()
        self.s.bind((host, port))
        self.s.listen(listen)
        self.conn, self.addr = self.s.accept()
        logging.info(f'connected: {self.addr}')

    def send_data(self, dt: bytes) -> None:
        self.conn.send(dt)

    def wait(self):
        return self.conn.recv(1024)

    def close(self) -> None:
        self.conn.send(b'close')
        self.conn.close()


if __name__ == '__main__':
    loop_time = time.time()
    camera = dxcam.create()
    s = Sock('0.0.0.0', 9998, 1)
    fps = 120
    quality = 1
    prev_frame = None
    i = 0
    interval = 4
    while not keyboard.is_pressed('f12'):
        img_time = time.time()
        img = get_frame(camera, cursor=True, size_x=1280, size_y=720)
        if img is None:
            continue
        logging.info(f'frame {time.time() - img_time}')

        comp_time = time.time()
        if prev_frame is None or i % interval == 0:
            send_frame = img
        else:
            frame_delta = cv2.absdiff(prev_frame, img)
            _, threshold_delta = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)
            threshold_delta = threshold_delta.astype(np.uint8)
            threshold_delta = cv2.cvtColor(threshold_delta, cv2.COLOR_BGR2GRAY)
            threshold_delta = cv2.resize(threshold_delta, (img.shape[1], img.shape[0]))
            send_frame = cv2.bitwise_and(img, img, mask=threshold_delta)
        i += 1

        logging.info(f'compression {time.time() - comp_time}')
        prev_frame = img

        send_time = time.time()
        data = pickle.dumps(send_frame)
        s.send_data(pickle.dumps(len(data)))
        s.wait()
        s.send_data(data)
        s.wait()
        logging.info(f'send {time.time() - send_time}')

        try:
            fps = 1 / (time.time() - loop_time)
            logging.info(f'FPS {fps} ({time.time() - loop_time})')
        except ZeroDivisionError:
            pass
        loop_time = time.time()
        # time.sleep(1)
    s.close()
