from typing import re

from PyQt5.QtCore import pyqtSignal, QPoint
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QToolTip

from UI_frmInitialize import Ui_frmInitialize

class FrmInitialize(QMainWindow, Ui_frmInitialize):
    signal_login = pyqtSignal(str, int)

    def __init__(self):
        super(FrmInitialize, self).__init__()
        self.setupUi(self)
        self.cmdStart.clicked.connect(self.cmd_start)
        self.cmdExit.clicked.connect(self.cmd_exit_click)
        self.txtPort.setText('4444')
        self.txtHost.setText('127.0.0.1')

    def cmd_exit_click(self):
        cmd = QMessageBox.question(self, 'exit confirm', 'are you sure to exit? ',
                                QMessageBox.Yes|QMessageBox.Cancel, QMessageBox.Yes)
        if cmd == QMessageBox.Yes:
            self.close()

    def cmd_start(self):
        host = self.txtHost.text()
        port = self.txtPort.text()
        if host == '':
            QToolTip.showText(self.txtHost.mapToGlobal(QPoint(0,0)),
                              'please input a valible host name! ')
            return
        if port == '':
            QToolTip.showText(self.txtPort.mapToGlobal(QPoint(0,0)),
                              'please input a valible port number! ')
            return

        # 发送登录成功的信号量
        self.signal_login.emit(host, int(port))

