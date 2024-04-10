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

    def close(self) -> None:
        self.conn.send(b'close')
        self.conn.close()


if __name__ == '__main__':
    # cv2.namedWindow('screen', cv2.WINDOW_NORMAL)
    # cv2.setWindowProperty('screen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    loop_time = time.time()
    avg = []
    camera = dxcam.create()
    while True:
        img = get_frame(camera, cursor=True)
        try:
            FPS = 1 / (time.time() - loop_time)
        except ZeroDivisionError:
            FPS = 1000
        print(f'FPS {FPS}')
        avg.append(FPS)
        loop_time = time.time()

        if img is None:
            continue
        cv2.imshow('screen', img)
        cv2.waitKey(1)
        if keyboard.is_pressed('f12'):
            break

    cv2.destroyAllWindows()
    print(sum(avg) / len(avg))

    # s = Sock('0.0.0.0', 9999, 1)
    # s.send_data(b'hello')
    # s.close()

    # import time
    #
    # start_time = time.time()
    # img = screen()
    # print(time.time() - start_time)
    # print(type(img))
    # cv2.imshow('screen', img)
    # cv2.waitKey(0)
