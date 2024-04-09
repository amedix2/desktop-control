import numpy as np
import cv2
import pyautoguis


def screen(size_x: int = 1280, size_y: int = 720):
    image = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(image),
                         cv2.COLOR_RGB2BGR)
    image = cv2.resize(image, (size_x, size_y))
    return image


if __name__ == '__main__':
    import time
    start_time = time.time()
    img = screen()
    print(time.time() - start_time)
    cv2.imshow('screen', img)
    cv2.waitKey(0)
