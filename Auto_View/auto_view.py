import os
import sys
import time

from PIL import ImageGrab
import numpy as np
import cv2
import pyautogui
import pynput.mouse as py_mouse
import pynput.keyboard as py_key


# 倒数计时并打印
def countdown(total_time: int):
    for t in range(total_time):
        r = '\rcountdown: %ds [%s%s]' % ((total_time - t), '=' * (total_time - t), ' ' * t)
        sys.stdout.write(r)
        time.sleep(1)
        sys.stdout.flush()
    print('\nstart to work')


# 读取txt数据
def txt2cache(filename):
    with open(filename, 'r', encoding='utf-8') as cache_data_txt:
        cache_data = cache_data_txt.read()
        cache_data = eval(cache_data)  # eval函数用来执行一个字符串表达式, 这里是实例化字典
    return cache_data


#  模板匹配
def template_match(img, template, mask=None):
    if len(img.shape) > 2:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if len(template.shape) > 2:
        template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED, mask)  # cv2的模板匹配
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)  # 返回最大最小值及索引
    (x_1, y_1) = maxLoc
    x_2 = x_1 + template.shape[1]
    y_2 = y_1 + template.shape[0]
    # cv2.rectangle(img, (x_1, y_1), (x_2, y_2), 0, 2)  # 画出匹配框
    return np.array([x_1, y_1, x_2, y_2])


class Auto_View:
    def __init__(self):
        self.screen_roi = [0, 0] + list(pyautogui.size())  # 屏幕分辨率
        self.thread_killer = False
        self.mouse_ctr = py_mouse.Controller()

    def grab_img(self):
        # 截图
        img = ImageGrab.grab(bbox=self.screen_roi)
        # 转为 cv2 格式
        img = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
        return img

    def on_mouse_click(self, x, y, button, pressed):
        # stop listener
        if self.thread_killer:
            return False
        print(f'{"Pressed" if pressed else "Released"} {button}: {(x, y)}')
        if pressed:
            button = 'left' if str(button) == 'Button.left' else 'right'
            with open('action_log.txt', 'a') as action_log:
                action_log.write(f'"click(x={x}, y={y}, button=\'{button}\')", 1,\n')

    def on_mouse_scroll(self, x, y, dx, dy):
        # stop listener
        if self.thread_killer:
            return False
        print(f'Scrolled: {(x, y, dx, dy)}')
        with open('action_log.txt', 'a') as action_log:
            action_log.write(f'"scroll({dx}, {dy})", 0.5,\n')

    def on_key_press(self, key):
        # stop listener
        if str(key) == 'Key.esc':
            self.thread_killer = True
            return False
        print(f'key pressed: {key}')

    def start_log(self):
        # 创建日志
        with open('action_log.txt', 'w') as action_log:
            action_log.write('{"commands": [\n')
        countdown(5)
        # 连接事件以及释放
        mouse_listener = py_mouse.Listener(on_click=self.on_mouse_click, on_scroll=self.on_mouse_scroll)
        key_listener = py_key.Listener(on_release=self.on_key_press)
        # 启动监听线程
        mouse_listener.start()
        key_listener.start()
        # 阻塞线程
        mouse_listener.join()
        key_listener.join()
        print('log over')
        with open('action_log.txt', 'a') as action_log:
            action_log.write(']}')
        self.thread_killer = False

    def start_work(self, params_txt):
        # 解析
        params = txt2cache(params_txt)  # 从txt中读取配置
        command_list = params['commands']  # 操作指令列表
        # 执行
        countdown(5)
        for i, command in enumerate(command_list):
            print(f'perform operation: {i}')
            if type(command) is str:
                # 如果是图片路径: 截图 + 读图匹配 + 鼠标移动
                if os.path.isfile(command):
                    img = self.grab_img()  # 截图
                    match_res = template_match(img, cv2.imread(command, 0), mask=None)  # 读图匹配
                    mouse_loc = np.array([np.mean(match_res[[0, 2]]), np.mean(match_res[[1, 3]])])
                    pyautogui.moveTo(x=mouse_loc[0], y=mouse_loc[1])
                # 如果是指令则执行
                else:
                    if 'scroll' in command:
                        eval(f'self.mouse_ctr.{command}')
                    else:
                        eval(f'pyautogui.{command}')
            # 如果是数: 则等待相应时间
            elif type(command) in (int, float):
                time.sleep(command)
        print('finish')


if __name__ == '__main__':
    auto_view = Auto_View()
    # auto_view.start_log()
    auto_view.start_work('action_log.txt')  # params.txt
