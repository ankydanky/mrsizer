# coding: utf-8

import os
import sys
import subprocess

from PySide2 import QtWidgets, QtGui

version = 2.0


def getappdir():
	return os.path.dirname(__file__)

class MRSizer(object):
	
	def __init__(self):
		self.lastCustomWidth = None
		self.lastCustomHeight = None
		self.activeWindow = None
		self.createWindow()
		self.createContextMenu()
		self.createSysTray()
	
	def createWindow(self):
		self.mainwindow = QtWidgets.QMainWindow()
		self.mainwindow.setFixedSize(0, 0)
	
	def createContextMenu(self):
		self.cmenu = QtWidgets.QMenu()
		
		self.act_quit = QtWidgets.QAction("Quit MRSizer", self.cmenu)
		self.act_quit.triggered.connect(lambda: sys.exit(0))
		
		self.act_about = QtWidgets.QAction("About MRSizer", self.cmenu)
		self.act_about.triggered.connect(self.showAbout)
		
		self.act_atboot = QtWidgets.QAction("Start at login", self.cmenu)
		self.act_atboot.setCheckable(True)
		self.act_atboot.triggered.connect(self.enableAtBoot)
		
		self.sizes = [
			"640x400", "640x480",
			"720x480", "720x576",
			"800x600",
			"1024x600", "1024x768",
			"1280x720", "1280x800", "1280x1024",
			"1366x768",
			"1600x1200",
			"1920x1080"
		]
		self.act_sizes = {}
		
		for size in self.sizes:
			width, height = size.split("x")
			self.act_sizes[size] = QtWidgets.QAction(size, self.cmenu)
			self.act_sizes[size].triggered.connect(lambda w=width, h=height: self.resize(w, h))
			self.cmenu.addAction(self.act_sizes[size])
		
		self.cmenu.addSeparator()
		
		self.act_custom = QtWidgets.QAction("Custom size", self.cmenu)
		self.act_custom.triggered.connect(self.dlgCustom)
		self.cmenu.addAction(self.act_custom)
		
		self.cmenu.addSeparator()
		self.cmenu.addAction(self.act_atboot)
		self.cmenu.addSeparator()
		self.cmenu.addAction(self.act_about)
		self.cmenu.addAction(self.act_quit)
	
	def dlgCustom(self):
		self.getActiveWindow()
		dlg = QtWidgets.QDialog()
		dlg.setWindowTitle("Custom resize dimensions")
		dlg.setWindowFlags(core.Qt.WindowStaysOnTopHint)
		dlg.setFixedWidth(350)
		dlg.setFixedHeight(120)
		layout = QtWidgets.QVBoxLayout()
		layout2 = QtWidgets.QHBoxLayout()
		layout3 = QtWidgets.QHBoxLayout()
		ipt_width = QtWidgets.QLineEdit()
		ipt_height = QtWidgets.QLineEdit()
		lbl = QtWidgets.QLabel(" X ")
		lbl_width = QtWidgets.QLabel("Width: ")
		lbl_height = QtWidgets.QLabel("Height: ")
		btn_resize = QtWidgets.QPushButton("Apply")
		btn_resize.clicked.connect(lambda d=dlg,w=ipt_width,h=ipt_height: self.resizeCustom(d, w, h))
		layout2.addWidget(lbl_width)
		layout2.addWidget(ipt_width)
		layout2.addWidget(lbl)
		layout2.addWidget(lbl_height)
		layout2.addWidget(ipt_height)
		layout3.addStretch(True)
		layout3.addWidget(btn_resize)
		layout.addLayout(layout2)
		layout.addLayout(layout3)
		dlg.setLayout(layout)
		dlg.exec_()
	
	def createSysTray(self):
		img_path = "."
		if hasattr(sys, "frozen"):
			img_path = os.path.join(getappdir(), "..", "Resources")
		self.systray = QtWidgets.QSystemTrayIcon()
		self.systray.setIcon(QtGui.QIcon(os.path.join(img_path, "systray.png")))
		self.systray.setContextMenu(self.cmenu)
	
	def asrun(self, ascript):
		ascript = ascript.encode()
		osa = subprocess.Popen(['osascript', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		return osa.communicate(ascript)[0]

	def asquote(self, astr):
		astr = astr.replace('"', '" & quote & "')
		return '"{}"'.format(astr)
	
	def getActiveWindow(self):
		app = self.asrun('''
			set the_application to (path to frontmost application as Unicode text)
			do shell script "echo " & quoted form of the_application
		''')
		app = app.decode().rstrip(":").split(":")
		app = os.path.join(os.sep, os.sep.join(app[1:])).rstrip()
		self.activeWindow = app
	
	def resizeCustom(self, dlg, w, h):
		width = w.text()
		height = h.text()
		dlg.close()
		if width == "" or width < 100 or height == "" or height < 100:
			return
		self.asrun('''
			set the_application to "{0}"
			tell application the_application
				set currentbounds to bounds of window 1
			end tell
			set bound_x to item 1 of currentbounds
			set bound_y to item 2 of currentbounds
			tell application the_application
				activate
				set bounds of window 1 to {{bound_x, bound_y, {1}+bound_x, {2}+bound_y}}
			end tell
		'''.format(self.activeWindow, width, height))
	
	def resize(self, width, height):
		self.getActiveWindow()
		self.asrun('''
			set the_application to "{0}"
			tell application the_application
				set currentbounds to bounds of window 1
			end tell
			set bound_x to item 1 of currentbounds
			set bound_y to item 2 of currentbounds
			tell application the_application
				activate
				set bounds of window 1 to {{bound_x, bound_y, {1}+bound_x, {2}+bound_y}}
			end tell
		'''.format(self.activeWindow, width, height))
	
	def enableAtBoot(self):
		items = self.asrun('tell application "System Events" to get the name of every login item')
		if "MRSizer" in items.strip().split(", "):
			self.asrun('tell application "System Events" to delete login item "MRSizer"')
		else:
			self.asrun('tell application "System Events" to make new login item at end with properties { path: "/Applications/MRSizer.app", name: "MRSizer", hidden: false }')
	
	def showAbout(self):
		mbox = QtWidgets.QMessageBox()
		mbox.setText("MRSizer {0} was written by Andy Kayl.\nAll rights reserved.".format(version))
		mbox.exec_()
	
	def verifyStartup(self):
		items = self.asrun('tell application "System Events" to get the name of every login item')
		if "MRSizer" in items.decode().strip().split(", "):
			self.act_atboot.setChecked(True)
	
	def run(self):
		self.mainwindow.show()
		self.systray.show()
		self.verifyStartup()
