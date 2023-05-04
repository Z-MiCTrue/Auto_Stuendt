import sys
import time
import unicodedata

import pyautogui
import jieba
from xpinyin import Pinyin


# 倒数计时并打印
def countdown(total_time: int):
    for t in range(total_time):
        r = '\rcountdown: %ds [%s%s]' % ((total_time - t), '=' * (total_time - t), ' ' * t)
        sys.stdout.write(r)
        time.sleep(1)
        sys.stdout.flush()
    print('\nstart to work')


# 读取txt数据
def txt2str(filename):
    with open(filename, 'r', encoding='utf-8') as cache_data_txt:
        cache_data = cache_data_txt.read()
    return cache_data


# 自动输入函数
def auto_key(words: str):
    pinyin = Pinyin()
    countdown(5)  # 倒计时缓冲
    words_list = ('#'.join(jieba.cut(words)).split('#'))  # 将中文字符串切分成词组 list
    for char in words_list:
        if char not in list('（，。、：——；）'):
            char = pinyin.get_pinyin(char, '')  # 将词组转化为拼音
        else:
            char = unicodedata.normalize('NFKC', char)  # 将标点转化为u英文
        char = list(char)
        for key_input in char:
            pyautogui.keyDown(key_input)  # 依次将拼音键入
        time.sleep(0.1)
        pyautogui.keyDown(' ')  # 键入空格选定词组
    print('finish')


if __name__ == '__main__':
    all_words = txt2str('source.txt')
    auto_key(all_words)
