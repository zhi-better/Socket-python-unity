import threading
from PyQt5 import QtWidgets, QtCore
import sys
from PyQt5.QtCore import *
import time
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication


class ProgressBar(QtWidgets.QWidget):
    signal_update = pyqtSignal(float, int, int)
    def __init__(self):
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
        # 窗口初始化
        self.setGeometry(300, 300, 500, 70)
        self.setWindowTitle('正在处理中')
        self.show()

    def update(self, progress, task_run, task_total):
        self.pbar.setValue(progress*100)
        label = "正在处理：" + "第" + str(task_run) + "/" + str(task_total) + '个任务'
        self.setWindowTitle(self.tr(label))  # 顶部的标题

def initializeServer(signal, num):
    for i in range(100):
        print('fun call')
        signal.emit(i/100.0, 1, 1)
        time.sleep(1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pbar = ProgressBar()
    thd = threading.Thread(target=initializeServer, args=(pbar.signal_update, 1))
    thd.setDaemon(True)  # 设置为守护线程
    thd.start()
    app.exec_()