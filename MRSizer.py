# coding: utf-8

import sys

from PySide2 import QtWidgets
from main import MRSizer

if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	main = MRSizer()
	main.run()
	sys.exit(app.exec_())
