# 导入套接字模块
import socket
import struct
# 导入线程模块
import sys
import threading
# 定义个函数,使其专门重复处理客户的请求数据（也就是重复接受一个用户的消息并且重复回答，直到用户选择下线）
import time
import cv2
import numpy as np
from PyQt5.QtCore import pyqtSignal, QRect, QObject
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from pyqt5_plugins.examplebutton import QtWidgets

from SocketTcpTools import TcpSererTools
from Form1 import Form1
from FrmInitialize import FrmInitialize



# 仅仅包含进度条和状态栏的运行过程提醒窗口
class ProgressBar(QtWidgets.QWidget):
    signal_update = pyqtSignal(float, int, int, str)
    def __init__(self, signal_exit):
        super(ProgressBar, self).__init__()
        # 进度条设置
        self.pbar = QtWidgets.QProgressBar(self)
        self.lbl_status = QtWidgets.QLabel(self)
        self.lbl_status.setGeometry(QRect(5, 30, 499, 43))
        self.lbl_status.setText('initialize...')
        # self.setWindowFlags(Qt.WindowMaximizeButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.pbar.setMinimum(0)  # 设置进度条最小值
        self.pbar.setMaximum(100)  # 设置进度条最大值
        self.pbar.setValue(0)  # 进度条初始值为0
        self.pbar.setGeometry(QRect(2, 3, 499, 28))  # 设置进度条在 QDialog 中的位置 [左，上，右，下]

        self.signal_update.connect(self.update)
        self.signal_exit = signal_exit  # (bool变量用来表示运行是否成功)

        # 窗口初始化
        self.setGeometry(300, 300, 500, 70)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)
        self.setWindowTitle('正在处理中')
        # self.show()

    def update(self, progress, task_run, task_total, msg):
        self.pbar.setValue(progress*100)
        label = "正在处理：" + "第" + str(task_run) + "/" + str(task_total) + '个任务'
        self.setWindowTitle(self.tr(label))  # 顶部的标题
        self.lbl_status.setText(msg)
        # 判断当前窗口任务是否运行完毕，如果运行完毕自动关闭窗口
        if progress == 1 and task_run >= task_total:
            # self.signal_exit.emit(True, "")
            self.close()

class MainForm(QObject):
    signal_connect_client = pyqtSignal(str, int)
    signal_server_stop = pyqtSignal()
    signal_add_client = pyqtSignal(str, int)
    signal_remove_client = pyqtSignal(str, int)
    def __init__(self):
        super(MainForm, self).__init__()
        # 窗口初始化
        self.server = None
        self.login_form = FrmInitialize()
        self.form1 = Form1()
        # self.pbar = ProgressBar(self.signal_connect_client)
        # 信号量初始化
        self.login_form.signal_login.connect(self.initializeServer)     # 服务器初始化验证通过，尝试初始化服务器
        # 窗口显示
        self.login_form.show()
        self.form1.hide()

    def callback_function(self, recv_data):
        # print("receive data from: {}, data are: {}".format(tcp_client_address, recv_data.decode()))
        tim_start = time.time()
        image = np.frombuffer(recv_data, dtype=np.uint8)
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        '''
        请在此处编写处理并显示图片的代码
        '''
        # mainForm.form1.setPicture(img=image)
        edge_image = cv2.cvtColor(cv2.Canny(image, 100, 200), cv2.COLOR_GRAY2BGR)
        mainForm.form1.setPicture(img=edge_image)
        # send_data = "pong"
        # tcp_client_1.send(send_data.encode("utf-8"))
        '''
        发送的数据格式主要包括三部分，数据头：2 byte，数据长度：4 byte(int)，后面跟的是数据长度的内容
        '''
        image_send_back = cv2.imencode('.jpg', edge_image)
        # image_send_back = cv2.imencode('.jpg', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        image_send_back = image_send_back[1].tobytes()
        # print("\rtime cost: {}".format(time.time() - tim_start), end="")
        self.server.send(self.server.pack_data(image_send_back, b'\1'))

    # 初始化服务器函数
    def initializeServer(self, ip, port):
        # self.thd.start()
        self.server = TcpSererTools(ip, port)
        self.server.set_callback_fun(self.callback_function)
        self.server.start()
        # 窗体显示
        self.form1.show()
        self.login_form.hide()


if __name__ == '__main__':
    host = "127.0.0.1"
    port = 4444
    # #####################################################################
    # 可视化窗口部分
    app = QApplication(sys.argv)
    mainForm = MainForm()
    sys.exit(app.exec_())
