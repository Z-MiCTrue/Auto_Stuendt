import sys
import time

from PIL import ImageGrab
import numpy as np
import cv2
import pyautogui


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


class Auto_Student:
    def __init__(self, params_txt):
        params = txt2cache(params_txt)  # 从txt中读取配置
        self.screen_roi = params['screen_roi']  # 屏幕分辨率
        self.command_list = params['commands']  # 操作指令列表

    def grab_img(self):
        # 截图
        img = ImageGrab.grab(bbox=self.screen_roi)
        # 转为 cv2 格式
        img = cv2.cvtColor(np.array(img.convert('RGB')), cv2.COLOR_RGB2BGR)
        return img

    def start_work(self):
        countdown(5)
        for i, command in enumerate(self.command_list):
            print(f'perform operation: {i}')
            # 如果是路径字符串: 截图 + 读图匹配 + 鼠标点击
            if type(command) is str:
                img = self.grab_img()  # 截图
                match_res = template_match(img, cv2.imread(command, 0), mask=None)  # 读图匹配
                mouse_loc = np.array([np.mean(match_res[[0, 2]]), np.mean(match_res[[1, 3]])])
                pyautogui.click(x=mouse_loc[0], y=mouse_loc[1], clicks=1, interval=0, button='left')  # 鼠标点击
            # 如果是数: 则等待相应时间
            elif type(command) in (int, float):
                time.sleep(command)
        print('finish')


if __name__ == '__main__':
    auto_student = Auto_Student('params.txt')
    auto_student.start_work()
