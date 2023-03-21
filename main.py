# 导入套接字模块
import socket
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

from Form1 import Form1
from FrmInitialize import FrmInitialize

g_connection_pool = []

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
        self.login_form = FrmInitialize()
        self.form1 = Form1()
        # self.pbar = ProgressBar(self.signal_connect_client)
        # 信号量初始化
        self.login_form.signal_login.connect(self.initializeServer)     # 服务器初始化验证通过，尝试初始化服务器
        # 窗口显示
        self.login_form.show()
        self.form1.hide()

    def add_client(self, client_ip, client_port):
        self.form1.addClient(client_ip, client_port)

    def remove_client(self, client_ip, client_port):
        self.form1.removeClient(client_ip, client_port)

    # 消息处理线程
    def dispose_client_request(self, tcp_client_1, tcp_client_address):
        # 5 循环接收和发送数据
        while True:
            try:
                recv_data = tcp_client_1.recv(1048576)
            except ConnectionResetError:
                print("client:{} has closed, it has been remove from the connection pool. ".format(tcp_client_address))
                tcp_client_1.close()
                g_connection_pool.remove(tcp_client_1)
                return
            except ConnectionAbortedError:
                print("client:{} has closed, it has been remove from the connection pool. ".format(tcp_client_address))
                tcp_client_1.close()
                g_connection_pool.remove(tcp_client_1)
                return
            # 6 有消息就回复数据，消息长度为 0 就是说明客户端下线了
            if recv_data:
                # print("receive data from: {}, data are: {}".format(tcp_client_address, recv_data.decode()))
                image = np.frombuffer(recv_data, dtype=np.uint8)
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                '''
                请在此处编写处理并显示图片的代码
                '''
                # cv2.imshow("hello", image)
                # cv2.waitKey(0)
                mainForm.form1.setPicture(img=image)
                send_data = "pong"
                tcp_client_1.send(send_data.encode("utf-8"))
                print("send data to: {}, data are: {}".format(tcp_client_address, send_data))
            else:
                print("client:{} has closed, it has been remove from the connection pool. ".format(tcp_client_address))
                tcp_client_1.close()
                g_connection_pool.remove(tcp_client_1)
                break

    # 服务器开启线程
    def thd_initializeServer(self, ip, port):
        # 1 创建服务端套接字对象
        # signal_update.emit(0, 1, 1, 'initializing...')
        socket.socket()
        tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # signal_update.emit(0.2, 1, 1, 'socket object created...')
        # 设置端口复用，使程序退出后端口马上释放
        tcp_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
        # 2 绑定端口
        tcp_server.bind((host, port))
        # signal_update.emit(0.7, 1, 1, "socket bind successfully...")
        print('server port bind successfully, server host: {}, server port: {}...'.format(host, port))
        # 3 设置监听
        tcp_server.listen(128)
        print('start to listen connections from client...')
        # signal_update.emit(1, 1, 1, "socket listen successfully...")
        # 4 循环等待客户端连接请求（也就是最多可以同时有128个用户连接到服务器进行通信）
        while True:
            tcp_client_1, tcp_client_address = tcp_server.accept()
            self.add_client(tcp_client_address[0], tcp_client_address[1])
            # 创建多线程对象
            thd = threading.Thread(target=self.dispose_client_request,
                                   args=(tcp_client_1, tcp_client_address))
            g_connection_pool.append(tcp_client_1)
            # 设置守护主线程  即如果主线程结束了 那子线程中也都销毁了  防止主线程无法退出
            thd.setDaemon(True)
            # 启动子线程对象
            thd.start()
            print("new client connected, client address: {}, total client count: {}".format(tcp_client_address,
                                                                                            len(g_connection_pool)))

    # 初始化服务器函数
    def initializeServer(self, ip, port):
        # 首先显示进度条的窗口，使得程序更加的智能看起来
        # 先启动服务器
        self.thd = threading.Thread(target=self.thd_initializeServer,
                                    args=(ip, port))
        self.thd.setDaemon(True)  # 设置为守护线程
        self.thd.start()
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
