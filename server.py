import numpy as np
import cv2
import pyautogui
import socket


def screen(size_x: int = 1280, size_y: int = 720) -> np.ndarray:
    image = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(image),
                         cv2.COLOR_RGB2BGR),
    image = cv2.resize(image, (size_x, size_y,), )
    return image


class Sock:
    def __init__(self, host: str, port: int) -> None:
        self.s = socket.socket()
        self.s.bind((host, port))
        self.s.listen(1)
        self.conn, self.addr = self.s.accept()
        print('connected:', self.addr)

    def send_data(self, data: bytes) -> None:
        self.conn.send(data)

    def close(self) -> None:
        self.conn.send(b'close')
        self.conn.close()


if __name__ == '__main__':
    s = Sock('0.0.0.0', 9999)
    s.send_data(b'hello')
    s.close()

    # import time
    #
    # start_time = time.time()
    # img = screen()
    # print(time.time() - start_time)
    # print(type(img))
    # cv2.imshow('screen', img)
    # cv2.waitKey(0)
