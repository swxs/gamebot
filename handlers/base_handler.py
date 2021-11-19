import os
import cv2
import time
import random
import win32api
import win32gui
import win32con
import win32ui
import numpy as np

class Base():
    @classmethod
    def is_visible_tree(cls, hwnd):
        return win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd)
    
    @classmethod
    def get_hwnd_list(cls):
        '''
        获取所有窗口句柄
        '''
        hwnd_list = list()
        def _get_hwnd(hwnd, mouse):
            if Base.is_visible_tree(hwnd):
                hwnd_list.append({
                    "hwnd": hwnd,
                    "title": win32gui.GetWindowText(hwnd),
                })
        win32gui.EnumWindows(_get_hwnd, 0)
        return hwnd_list
    
    @classmethod
    def get_hwnd(cls, name):
        hwnd_list = Base.get_hwnd_list()
        for hwnd in hwnd_list:
            if hwnd.get("title") == name:
                return hwnd["hwnd"]
        else:
            return None
    
    @classmethod
    def get_children_hwnd(cls, parent_hwnd):        
        '''     
        获得parent的所有子窗口句柄
        返回子窗口句柄列表
        '''     
        if not parent_hwnd:         
            return      
        hwndChildList = []
        try:
            win32gui.EnumChildWindows(
                parent_hwnd, 
                lambda hwnd, param: param.append(
                    (hwnd, win32gui.GetWindowText(hwnd))
                ),
                hwndChildList
            )
        except:
            pass
        return hwndChildList
    
    @classmethod
    def find_idxSubHandle(cls, pHandle, winClass, index=0):
        """
        已知子窗口的窗体类名
        寻找第index号个同类型的兄弟窗口
        """
        assert type(index) == int and index >= 0
        handle = win32gui.FindWindowEx(pHandle, 0, winClass, None)
        while index > 0:
            handle = win32gui.FindWindowEx(pHandle, handle, winClass, None)
            index -= 1
        return handle
    
    @classmethod
    def find_subHandle(cls, pHandle, winClassList):
        """
        递归寻找子窗口的句柄
        pHandle是祖父窗口的句柄
        winClassList是各个子窗口的class列表，父辈的list-index小于子辈
        """
        assert type(winClassList) == list
        if len(winClassList) == 1:
            return Base.find_idxSubHandle(pHandle, winClassList[0][0], winClassList[0][1])
        else:
            return Base.find_idxSubHandle(pHandle, winClassList[0][0], winClassList[0][1])
        
    @classmethod
    def screen(cls, hwnd, filename):
        # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
        hwndDC = win32gui.GetWindowDC(hwnd)
        # 根据窗口的DC获取mfcDC
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        mfcDC_handler = mfcDC.GetHandleAttrib()
        # 截图
        win32gui.SendMessage(hwnd, win32con.WM_PRINT, mfcDC_handler,win32con.PRF_CLIENT | win32con.PRF_OWNED | win32con.PRF_ERASEBKGND | win32con.PRF_NONCLIENT)
        # mfcDC创建可兼容的DC
        saveDC = mfcDC.CreateCompatibleDC()
        # 创建bigmap准备保存图片
        saveBitMap = win32ui.CreateBitmap()
        # 获取监控器信息
        MoniterDev = win32gui.GetClientRect(hwnd)
        # 这个系数是为啥？ 之前也有碰到过
        w = MoniterDev[2] * 3 // 2
        h = MoniterDev[3] * 3 // 2
        # print w,h　　　#图片大小
        # 为bitmap开辟空间
        saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
        # 高度saveDC，将截图保存到saveBitmap中
        saveDC.SelectObject(saveBitMap)
        # 截取从左上角（0，0）长宽为（w，h）的图片
        saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
        saveBitMap.SaveBitmapFile(saveDC, filename)
        return cv2.imread(get_file_path('screen.png'))
    
    @classmethod
    def move_to(cls, hwnd, point):
        raise Exception("need")

    @classmethod
    def left_click_at_point(cls, hwnd, point):
        raise Exception("need")
    
    @classmethod
    def right_click_at_point(cls, hwnd, point):
        raise Exception("need")

    @classmethod
    def find_ellement_and_click(cls, hwnd, file, speed=0.5, sens=0.4, tmp_x=0, tmp_y=0, click=True):
        try:
            img = cls.screen()
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            template = cv2.imread(get_file_path(file), cv2.IMREAD_GRAYSCALE)
            w, h = template.shape[::-1]
            result = cv2.matchTemplate(gray_img, template, cv2.TM_CCOEFF_NORMED)

            loc = np.where(result >= sens)
            if len(loc[0]) != 0:
                pt = random.choice(list(zip(*loc[::-1])))
                x = int((pt[0] * 2 + w + tmp_x) / 2)
                y = int((pt[1] * 2 + h + tmp_y) / 2)
                print("Found " + file, x, y)
                cls.move_to(hwnd, (x, y))                
                time.sleep(0.2)
                if click:
                    cls.left_click_at_point(hwnd, (x, y))
                return True
            else:
                print(f"Not found: {file}")
                return False
        except Exception as e:
            print(e)
            return False

    @classmethod
    def get_random_point(cls, point1, point2):
        return random.randint(point1[0], point2[0]), random.randint(point1[1], point2[1])
    