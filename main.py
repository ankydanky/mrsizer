# coding: utf-8

from __future__ import unicode_literals

import os
import sys
import subprocess
import re

import PySide.QtCore as core
import PySide.QtGui as gui

version = 1.3

class MRSizer(object):
	
	def __init__(self):
		self.lastCustomWidth = None
		self.lastCustomHeight = None
		self.activeWindow = None
		self.createWindow()
		self.createContextMenu()
		self.createSysTray()
	
	def createWindow(self):
		self.mainwindow = gui.QMainWindow()
		self.mainwindow.setFixedSize(0, 0)
	
	def createContextMenu(self):
		self.cmenu = gui.QMenu()
		
		self.act_quit = gui.QAction("Quit MRSizer", self.cmenu)
		self.act_quit.triggered.connect(lambda: sys.exit(0))
		
		self.act_about = gui.QAction("About MRSizer", self.cmenu)
		self.act_about.triggered.connect(self.showAbout)
		
		self.act_atboot = gui.QAction("Start at login", self.cmenu)
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
			self.act_sizes[size] = gui.QAction(size, self.cmenu)
			self.act_sizes[size].triggered.connect(lambda w=width, h=height: self.resize(w, h))
			self.cmenu.addAction(self.act_sizes[size])
		
		self.cmenu.addSeparator()
		
		self.act_custom = gui.QAction("Custom size", self.cmenu)
		self.act_custom.triggered.connect(self.dlgCustom)
		self.cmenu.addAction(self.act_custom)
		
		self.cmenu.addSeparator()
		self.cmenu.addAction(self.act_atboot)
		self.cmenu.addSeparator()
		self.cmenu.addAction(self.act_about)
		self.cmenu.addAction(self.act_quit)
	
	def dlgCustom(self):
		self.getActiveWindow()
		dlg = gui.QDialog()
		dlg.setWindowTitle("Custom resize dimensions")
		dlg.setWindowFlags(core.Qt.WindowStaysOnTopHint)
		dlg.setFixedWidth(350)
		dlg.setFixedHeight(120)
		layout = gui.QVBoxLayout()
		layout2 = gui.QHBoxLayout()
		layout3 = gui.QHBoxLayout()
		ipt_width = gui.QLineEdit()
		ipt_height = gui.QLineEdit()
		lbl = gui.QLabel(" X ")
		lbl_width = gui.QLabel("Width: ")
		lbl_height = gui.QLabel("Height: ")
		btn_resize = gui.QPushButton("Apply")
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
		self.systray = gui.QSystemTrayIcon()
		self.systray.setIcon(gui.QIcon("systray.png"))
		self.systray.setContextMenu(self.cmenu)
	
	def asrun(self, ascript):
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
		app = app.rstrip(":").split(":")
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
		mbox = gui.QMessageBox()
		mbox.setText("MRSizer {0} was written by Andy Kayl.\nAll rights reserved.".format(version))
		mbox.exec_()
	
	def verifyStartup(self):
		items = self.asrun('tell application "System Events" to get the name of every login item')
		if "MRSizer" in items.strip().split(", "):
			self.act_atboot.setChecked(True)
	
	def run(self):
		self.mainwindow.show()
		self.systray.show()
		self.verifyStartup()
