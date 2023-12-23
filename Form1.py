from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QListWidgetItem

from UI_form1 import Ui_form1


class Form1(QMainWindow, Ui_form1):
    def __init__(self):
        super(Form1, self).__init__()
        self.setupUi(self)
        self.signal_ok = pyqtSignal()
        self.signal_cancel = pyqtSignal()
        self.cmdOK.setVisible(False)
        self.cmdCancel.setVisible(False)

        self.cmdOK.clicked.connect(self.cmdOK_click)

    # 增加客户端
    def addClient(self, client_ip, client_port):
        self.lst_client.addItem(QListWidgetItem("{}:{}".format(client_ip, client_port)))

    # 删除客户端
    def removeClient(self, client_ip, client_port):
        for i in range(self.lst_client.count()):
            if self.lst_client.item(i).text() == "{}:{}".format(client_ip, client_port):
                self.lst_client.takeItem(i)
                break

    def cmdOK_click(self):
        print('clicked')
        QMessageBox.information(self, 'title', 'main text', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

    def setPicture(self, img):
        label_image = QImage(img, img.shape[1], img.shape[0], QImage.Format_RGB888)
        self.lblShow.setPixmap(QPixmap(label_image))#设置显示图片



