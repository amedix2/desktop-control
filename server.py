# import logging
import numpy as np
import cv2
import pyautogui
import socket
import dxcam
import time
import keyboard


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
        print('connected:', self.addr)

    def send_data(self, data: bytes) -> None:
        self.conn.send(data)

    def wait(self):
        return self.conn.recv(1024)

    def close(self) -> None:
        self.conn.send(b'close')
        self.conn.close()


if __name__ == '__main__':
    # cv2.namedWindow('screen', cv2.WINDOW_NORMAL)
    # cv2.setWindowProperty('screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    loop_time = time.time()
    camera = dxcam.create()
    s = Sock('0.0.0.0', 9998, 1)
    while not keyboard.is_pressed('f12'):
        img_time = time.time()
        img = get_frame(camera, cursor=True)
        if img is None:
            continue
        print('frame', time.time() - img_time)

        comp_time = time.time()
        ret, jpeg = cv2.imencode('.jpg', img)
        data = jpeg.tobytes()
        print('compression', time.time() - comp_time)

        send_time = time.time()
        s.send_data(data)
        s.wait()
        print('send', time.time() - send_time)

        try:
            fps = 1 / (time.time() - loop_time)
            print(f'FPS {fps} ({time.time() - loop_time})')
        except ZeroDivisionError:
            # too much fps lol
            pass
        loop_time = time.time()
        #time.sleep(5)
    s.close()

    # cv2.destroyAllWindows()
    # cv2.imshow('screen', img)
    # cv2.waitKey(1)
