# -*- coding: utf-8 -*-

import random
# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
import sys
import threading
import time

from PyQt5 import QtCore, QtGui, QtWidgets

from main import auth_vk, vk, ok
from main_parser import start_vk
from misc import ads_list, proxy_list, create_csv, LOGIN, PASSWORD, current_build, threads


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(758, 562)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.thread_field = QtWidgets.QSpinBox(self.centralwidget)
        self.thread_field.setGeometry(QtCore.QRect(630, 270, 51, 21))
        self.thread_field.setObjectName("thread_field")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(40, 20, 241, 31))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI Light")
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(40, 260, 241, 31))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI Light")
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(410, 260, 191, 31))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI Light")
        font.setPointSize(14)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_button.setGeometry(QtCore.QRect(420, 330, 151, 31))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(11)
        self.start_button.setFont(font)
        self.start_button.setObjectName("start_button")
        self.start_button.clicked.connect(self.on_start)

        # self.stop_button = QtWidgets.QPushButton(self.centralwidget)
        # self.stop_button.setGeometry(QtCore.QRect(420, 370, 151, 31))
        # self.stop_button.clicked.connect(self.on_stop)
        #
        # font = QtGui.QFont()
        # font.setFamily("Microsoft YaHei UI")
        # font.setPointSize(11)
        # self.stop_button.setFont(font)
        # self.stop_button.setObjectName("stop_button")
        self.ad_links = QtWidgets.QTextEdit(self.centralwidget)
        self.ad_links.setGeometry(QtCore.QRect(40, 60, 681, 191))
        self.ad_links.setObjectName("ad_links")
        self.proxy_list = QtWidgets.QTextEdit(self.centralwidget)
        self.proxy_list.setGeometry(QtCore.QRect(40, 320, 351, 191))
        self.proxy_list.setObjectName("proxy_list")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def on_start(self):
        try:
            if logged:
                thread_count = self.threads_count()
                ads = self.ads_text().split('\n')
                proxy = self.proxy_text().split('\n')
                threads_was_opened = len(threading.enumerate())
                [ads_list.append(url) for url in ads if url != '']
                [proxy_list.append(data) for data in proxy if data != '']
                or_not = True if len(proxy_list) > 0 else False
                while len(vk) or len(ok):
                    if not len(ads_list):
                        break
                    for i in range((thread_count - len(threading.enumerate())) + threads_was_opened):
                        # if len(ok):
                        #     threading.Thread(target=start_vk,
                        #                      args=(ok.pop().split(':'), random.choice(proxy_list))).start()
                        if len(vk):
                            threads.append(threading.Thread(target=start_vk, args=([vk.pop().split(':'), or_not])).start())
                        else:
                            break
                    time.sleep(2)
                while len(threading.enumerate()) != threads_was_opened:
                    time.sleep(2)
                create_csv()
        except Exception as e:
            print(f'ERROR_DEF_ON_START:\n{e}')
            exit()



    def ads_text(self):
        return self.ad_links.toPlainText()

    def proxy_text(self):
        return self.proxy_list.toPlainText()

    def threads_count(self):
        return int(self.thread_field.text())

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Ссылки на объявления"))
        self.label_3.setText(_translate("MainWindow", "Список прокси"))
        self.label_4.setText(_translate("MainWindow", "Количество потоков"))
        self.start_button.setText(_translate("MainWindow", "START"))
        # self.stop_button.setText(_translate("MainWindow", "STOP"))


def test():
    print('da')


class main_window(QtWidgets.QMainWindow):
    def __init__(self):
        super(main_window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


class Ui_MainWindow_auth(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(550, 250)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.login = QtWidgets.QLineEdit(self.centralwidget)
        self.login.setGeometry(QtCore.QRect(160, 60, 261, 31))
        self.login.setObjectName("login")

        self.password = QtWidgets.QLineEdit(self.centralwidget)
        self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password.setGeometry(QtCore.QRect(160, 110, 261, 31))
        self.password.setObjectName("password")

        self.auth_label = QtWidgets.QLabel(self.centralwidget)
        self.auth_label.setGeometry(QtCore.QRect(160, 10, 261, 41))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei Light")
        font.setPointSize(17)

        self.auth_label.setFont(font)
        self.auth_label.setAutoFillBackground(False)
        self.auth_label.setAlignment(QtCore.Qt.AlignCenter)
        self.auth_label.setObjectName("auth_label")

        self.login_label = QtWidgets.QLabel(self.centralwidget)
        self.login_label.setGeometry(QtCore.QRect(70, 60, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Microsoft JhengHei UI Light")
        font.setPointSize(14)
        self.login_label.setFont(font)
        self.login_label.setObjectName("login_label")

        self.password_label = QtWidgets.QLabel(self.centralwidget)
        self.password_label.setGeometry(QtCore.QRect(70, 120, 71, 21))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI Light")
        font.setPointSize(14)
        self.password_label.setFont(font)
        self.password_label.setObjectName("password_label")

        self.auth_button = QtWidgets.QPushButton(self.centralwidget)
        self.auth_button.setGeometry(QtCore.QRect(160, 160, 261, 31))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(13)
        self.auth_button.setFont(font)
        self.auth_button.setFlat(False)
        self.auth_button.setObjectName("auth_button")
        self.auth_button.clicked.connect(self.on_auth)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 573, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def on_auth(self):
        global logged
        logged = False
        login = self.login.text()
        password = self.password.text()
        # if login == LOGIN and password == PASSWORD:
        #     logged = True
        with open('accounts', 'r+') as file_accs:
            accs = file_accs.read().splitlines()
            for account in accs:
                if logged:
                    break
                if f'{login}:{password}' == account:
                    with open('machines', 'r+') as file_machine:
                        codes = file_machine.read().splitlines()
                        build = current_build()
                        for code in codes:
                            if build == code:
                                if len(codes) != len(accs):
                                    file_machine.write(build + '\n')
                                logged = True
                                break
        if logged:
            show_main()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Авторизация"))

        self.login_label.setText(_translate("MainWindow", "Логин"))
        self.password_label.setText(_translate("MainWindow", "Пароль"))
        self.auth_button.setText(_translate("MainWindow", "Войти"))


class auth_window(QtWidgets.QMainWindow):
    def __init__(self):
        super(auth_window, self).__init__()
        self.ui = Ui_MainWindow_auth()
        self.ui.setupUi(self)

    def closeEvent(self, event):
        exit()


def show_main():
    if logged:
        auth_app.hide()
    else:
        print('nework')


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    auth_app = auth_window()
    main_app = main_window()
    main_app.show()
    auth_app.show()

    sys.exit(app.exec())
