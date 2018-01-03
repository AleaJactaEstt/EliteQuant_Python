#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import yaml
from PyQt5 import QtCore, QtWidgets, QtGui
from source.gui.ui_main_window import MainWindow
import atexit
from signal import signal, SIGINT, SIG_DFL
from os import kill
from multiprocessing import Process
try:
    from server.EliteQuant import tradingengine_    # windows
except ImportError:
    from server.libelitequant import tradingengine_   # linux

# https://stackoverflow.com/questions/4938723/what-is-the-correct-way-to-make-my-pyqt-application-quit-when-killed-from-the-co
signal(SIGINT, SIG_DFL)

def main():
    config = None
    try:
        path = os.path.abspath(os.path.dirname(__file__))
        config_file = os.path.join(path, 'config.yaml')
        with open(os.path.expanduser(config_file), encoding='utf8') as fd:
            config = yaml.load(fd)
    except IOError:
        print("config.yaml is missing")

    lang_dict = None
    font = None
    try:
        path = os.path.abspath(os.path.dirname(__file__))
        config_file = os.path.join(path, 'language/en/live_text.yaml')
        font = QtGui.QFont('Microsoft Sans Serif', 10)
        if config['language'] == 'cn':
            config_file = os.path.join(path, 'language/cn/live_text.yaml')
            font = QtGui.QFont(u'微软雅黑', 10)
        with open(os.path.expanduser(config_file), encoding='utf8') as fd:
            lang_dict = yaml.load(fd)
        lang_dict['font'] = font
    except IOError:
        print("live_text.yaml is missing")

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow(config, lang_dict)

    if config['theme'] == 'dark':
        import qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    mainWindow.showMaximized()

    sys.exit(app.exec_())

def start_server():
    print('Running python server.')
    server = tradingengine_()
    server.run()

def stop_server():
    global server_process
    kill(server_process.pid, SIGINT)

server_process = None

if __name__ == "__main__":
    server_process = Process(target=start_server)
    server_process.start()
    atexit.register(stop_server)

    main()