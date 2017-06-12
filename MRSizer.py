# coding: utf-8

from __future__ import unicode_literals

import os
import sys
import main

import PySide.QtCore as core
import PySide.QtGui as gui

if __name__ == '__main__':
	app = gui.QApplication(sys.argv)
	main = main.MRSizer()
	main.run()
	sys.exit(app.exec_())
