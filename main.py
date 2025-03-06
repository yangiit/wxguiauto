from time import sleep

import uiautomation as auto
import re
import keyboard
import win32api
import win32con
import win32gui

from session_options import SessionOptions


class Toolbar:
    def __init__(self, toolbar_element):
        self.element = toolbar_element

    def perform_action(self):
        print("导航栏执行操作")


class SessionWindow:
    def __init__(self, session_window_element):
        self.element = session_window_element

    def send_message(self, message):
        print(f"聊天窗口发送消息: {message}")


class WeChat:

    def __init__(self):
        wx = auto.WindowControl(ClassName='WeChatMainWndForPC')
        wx.SetActive()

        # 获取窗口句柄
        hwnd = wx.NativeWindowHandle

        # 定义窗口大小和位置
        left = 295  # 窗口左上角的 x 坐标
        top = 175  # 窗口左上角的 y 坐标
        width = 1138  # 窗口宽度
        height = 800  # 窗口高度

        # 设置窗口大小和位置
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOP, left, top, width, height, win32con.SWP_SHOWWINDOW)

        child = wx.GetChildren()[-1]

        # 导航栏
        self.toolbar = Toolbar(child.PaneControl().GetChildren()[0])

        # 会话列表
        self.session_options = SessionOptions(child.PaneControl().GetChildren()[1])

        # 聊天窗口
        self.session_window = SessionWindow(child.PaneControl().GetChildren()[2])


if __name__ == '__main__':
    wx = WeChat()
    # wx.session_options.search_bar.send_keys('空空如也')
    # wx.session_options.search_bar.clear()
    wx.session_options.search_list.flip()
