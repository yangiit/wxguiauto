import copy
from time import sleep

import keyboard
import pyautogui
import win32api
import win32con
import re

from wx.wx_auto.common.utils import Logger


class Searchbar:
    def __init__(self, search_element):
        self.element = search_element
        self.logger = Logger(self.__class__.__name__)

    def send_keys(self, name):
        """
        输入查询软件
        :param name:
        :return:
        """
        input_box = self.element.EditControl(Name='搜索', LocalizedControlType='编辑')
        input_box.Click()
        input_box.SendKeys(name)

    def clear(self):
        """
        清空按钮
        --需要在查询条件输入框为激活情况下
        依赖：
            wx/wx_auto/session_options.py:18
        :return:
        """
        button = self.element.ButtonControl(Name='清空', LocalizedControlType='按钮')
        if not button.Exists(0.1):
            self.logger.log('找不到按钮')
            return
        button.Click()


class SessionList:
    def __init__(self, element):
        self.element = element
        self.logger = Logger(self.__class__.__name__)
        self.session_list = self.element.ListControl(Name='会话', LocalizedControlType='列表')

    def get_session_list(self):
        """
        TODO: 功能待确认
        :return:
        """
        if not self.session_list.Exists(0.1):
            self.logger.log('找不到列表对象')
            return

        session_list = []
        init_session_list_object = self.session_list.GetChildren()
        [session_list.append({
            'name': options.Name,  # 假设子项有 Name 属性
            'control_type': options.ControlType,
            'runtime_id': options.GetRuntimeId(),
        }) for options in init_session_list_object]

        for page in range(1):
            self.mouse_scrol()
            sleep(1)
            session_list_object = self.session_list.GetChildren()
            for options in session_list_object:
                session_list.append({
                    'name': options.Name,
                    'control_type': options.ControlType,
                    'runtime_id': options.GetRuntimeId(),
                })

        for item in session_list:
            print(item)

    def mouse_scrol(self, line=10):
        """
        向下滚动
        :param line: 行数
        :return:
        """
        # 获取控件的 BoundingRectangle
        rect = self.session_list.BoundingRectangle
        # 计算控件的中心位置
        center_x = (rect.left + rect.right) // 2
        center_y = (rect.top + rect.bottom) // 2

        # 移动鼠标到控件中心
        win32api.SetCursorPos((center_x, center_y))
        self.session_list.SetFocus()

        # 模拟鼠标滚轮向下滚动
        for _ in range(line):
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -120, 0)  # -120 表示向下滚动

    def listen_session_list(self):
        ...


class SessionOptions:
    def __init__(self, session_options_element):
        self.element = session_options_element
        self.search_bar = Searchbar(session_options_element.GetChildren()[0])
        self.search_list = SessionList(session_options_element.GetChildren()[1])

    def display_sessions(self):
        print("会话列表显示会话")


if __name__ == '__main__':
    SessionList('')
