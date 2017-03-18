#!/usr/bin/python

import sys
from PyQt4 import QtGui,QtCore
import UI
import RPi.GPIO as GPIO
from time import sleep

class Photometer(QtGui.QMainWindow,UI.Ui_MainWindow):
	def __init__(self,parent=None):
		super(Photometer,self).__init__(parent)
		self.setupUi(self)
		self.selectionState = 0
                self.startSetting = 0
                self.endSetting = 0
              
		self.leftKey = switchInterruptThread(17,1)
		self.rightKey = switchInterruptThread(26,2)

		self.setupSignals()
		self.nowStartSelect.setChecked(True)
		self.nowStartSelect.setFocus()
		self.show()

#Defines a keyboard based navigation schema of the GUI
	def keyPressEvent(self,e):
		if e.key() == QtCore.Qt.Key_Enter or e.key()==QtCore.Qt.Key_Return:

			if self.selectionState == 0:
				if self.nowStartSelect.isChecked()== True:
					self.startSetting = 0
					self.nowStartSelect.setEnabled(False)
                                	self.laterStartSelect.setEnabled(False)
                                	self.buttonStartSelect.setEnabled(False)
                                	self.startTimeEdit.setEnabled(False)
                                	self.buttonEndSelect.setFocus(True)
                                	self.selectionState = 2 

				elif self.laterStartSelect.isChecked()==True:
					self.startSetting = 1
					self.startTimeEdit.setDate(QtCore.QDate.currentDate())
					self.startTimeEdit.setEnabled(True)
					self.selectionState = 1 #Later Start
					self.startTimeEdit.setFocus()

				elif self.buttonStartSelect.isChecked()==True:
					self.startSetting = 2	#Button Start
					self.nowStartSelect.setEnabled(False)
                                	self.laterStartSelect.setEnabled(False)
                                	self.buttonStartSelect.setEnabled(False)
                                	self.startTimeEdit.setEnabled(False)
                                	self.buttonEndSelect.setFocus(True)
                                	self.selectionState = 2 

			elif self.selectionState == 1:
				self.starttime = self.startTimeEdit.dateTime()
				self.nowStartSelect.setEnabled(False)
                                self.laterStartSelect.setEnabled(False)
                                self.buttonStartSelect.setEnabled(False)
                                self.startTimeEdit.setEnabled(False)
                                self.buttonEndSelect.setFocus(True)
                                self.selectionState = 2 

			elif self.selectionState == 2:
				if self.buttonEndSelect.isChecked()== True:
                                        self.endSetting = 0	#Button End
        				self.buttonEndSelect.setEnabled(False)
        	                        self.timeEndSelect.setEnabled(False)
	                                self.sampleEndSelect.setEnabled(False)
                	                self.endTimeEdit.setEnabled(False)
                        	        self.sampleSelect.setEnabled(False)
                                	self.rateSelect.setFocus(True)
                               		self.selectionState = 5 

                                elif self.timeEndSelect.isChecked()==True:
                                        self.endSetting = 1	#Time End
                                        self.endTimeEdit.setDate(QtCore.QDate.currentDate())
                                        self.endTimeEdit.setEnabled(True)
                                        self.selectionState = 3 #Set End Time
                                        self.endTimeEdit.setFocus()
                                
				elif self.sampleEndSelect.isChecked()==True:
                                        self.endSetting = 2   #Sample End
                                        self.endTimeEdit.setEnabled(False)
                                        self.sampleSelect.setEnabled(True)
					self.sampleSelect.setFocus()
					self.selectionState = 4 #Sampled

			elif self.selectionState == 3:
                                self.endtime = self.endTimeEdit.dateTime()
                                self.buttonEndSelect.setEnabled(False)
                                self.timeEndSelect.setEnabled(False)
                                self.sampleEndSelect.setEnabled(False)
                                self.endTimeEdit.setEnabled(False)
                                self.sampleSelect.setEnabled(False)
                                self.rateSelect.setFocus(True)
                                self.selectionState = 5 

			elif self.selectionState == 4:
				self.endSamples = self.sampleSelect.value()
				self.buttonEndSelect.setEnabled(False)
                                self.timeEndSelect.setEnabled(False)
                                self.sampleEndSelect.setEnabled(False)
                                self.endTimeEdit.setEnabled(False)
                                self.sampleSelect.setEnabled(False)
                                self.rateSelect.setFocus(True)
                                self.selectionState = 5

			elif self.selectionState == 5:
                                self.sampleRate = self.rateSelect.value()
                                self.rateSelect.setEnabled(False)
                                self.goButton.setEnabled(True)
                                self.goButton.setFocus(True)
                                self.selectionState = 6

			elif self.selectionState == 6:
				self.selectionState = 7
				self.operationReady = 1
				self.initiateSampling()
				self.goButton.clicked.emit()

			elif self.selectionState == 7:
				self.operationReady = 0
				self.goButton.clicked.emit()
				self.terminateSampling()
				self.resetGUI()


#                       elif self.selectionState == 1:
#                               self.nowStartSelect.setEnabled(False)
#                               self.laterStartSelect.setEnabled(False)
#                               self.buttonStartSelect.setEnabled(False)
#                               self.startTimeEdit.setEnabled(False)
#                               self.buttonEndSelect.setFocus(True)
#                               self.selectionState = 3         #go to End parameter selection

#                       elif self.selectionState == 4:
#                               self.buttonEndSelect.setEnabled(False)
#                                self.timeEndSelect.setEnabled(False)
#                                self.sampleEndSelect.setEnabled(False)
#                                self.endTimeEdit.setEnabled(False)
#                               self.sampleSelect.setEnabled(False)
#                                self.rateSelect.setFocus(True)
#                                self.selectionState = 7 
		elif e.key() == QtCore.Qt.Key_Left:
			if self.selectionState == 0:
				if self.laterStartSelect.isChecked() == True:
					self.nowStartSelect.setChecked(True)
				elif self.buttonStartSelect.isChecked() == True:
					self.laterStartSelect.setChecked(True)
			elif self.selectionState == 2:
				if self.timeEndSelect.isChecked() == True:
                                        self.buttonEndSelect.setChecked(True)
                                elif self.sampleEndSelect.isChecked() == True:
                                        self.timeEndSelect.setChecked(True)
			elif self.selectionState == 1:
				if self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.AmPmSection:
					self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.MinuteSection)	
                                elif self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.MinuteSection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.HourSection)
                                elif self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.HourSection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.YearSection)
                                elif self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.YearSection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.MonthSection)
                                elif self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.MonthSection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.DaySection)

                        elif self.selectionState == 3:
                                if self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.AmPmSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.MinuteSection)
                                elif self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.MinuteSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.HourSection)
                                elif self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.HourSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.YearSection)
                                elif self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.YearSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.MonthSection)
                                elif self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.MonthSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.DaySection)


		elif e.key() == QtCore.Qt.Key_Right:
			if self.selectionState == 0:
                                if self.nowStartSelect.isChecked() == True:
                                        self.laterStartSelect.setChecked(True)
                                elif self.laterStartSelect.isChecked() == True:
                                        self.buttonStartSelect.setChecked(True)

                        elif self.selectionState == 2:
                                if self.buttonEndSelect.isChecked() == True:
                                        self.timeEndSelect.setChecked(True)
                                elif self.timeEndSelect.isChecked() == True:
                                        self.sampleEndSelect.setChecked(True)

			elif self.selectionState == 1:
                                if self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.DaySection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.MonthSection)
                                elif self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.MonthSection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.YearSection)
                                elif self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.YearSection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.HourSection)
                                elif self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.HourSection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.MinuteSection)
                                elif self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.MinuteSection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.AmPmSection)
		
                        elif self.selectionState == 3:
                                if self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.DaySection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.MonthSection)
                                elif self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.MonthSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.YearSection)
                                elif self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.YearSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.HourSection)
                                elif self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.HourSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.MinuteSection)
                                elif self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.MinuteSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.AmPmSection)


		elif e.key() == QtCore.Qt.Key_Up:
			print "Up Pressed"
		elif e.key() == QtCore.Qt.Key_Down:
			print "Down Pressed"

#Sets up the interconnections between the various threads
	def setupSignals(self):
		self.signalObj = InterruptSignals()
		self.signalObj.Key.connect(self.keyPressEvent)
		
		self.nowStartSelect.setFocus()
		self.goButton.clicked.connect(self.goButtonClicked)

		self.leftKey.connect(self.leftKey,QtCore.SIGNAL("keyDecode(int)"),self.keyDecode)
		self.rightKey.connect(self.rightKey,QtCore.SIGNAL("keyDecode(int)"),self.keyDecode)

		self.leftKey.active = True
		self.rightKey.active = True
                #self.leftKey.Key.connect(self.leftKeyPressEvent)
#               self.rightKey.Key.connect(keyPressEvent)
#               self.upKey.Key.connect(keyPressEvent)
#               self.downKey.Key.connect(keyPressEvent)
#               self.okKey.Key.connect(keyPressEvent)
		self.leftKey.start()
		self.rightKey.start()

	def goButtonClicked(self):
		print "Go Button Clicked"

	def keyDecode(self,e):
		if e == 0:
			ap = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,QtCore.Qt.Key_Enter,QtCore.Qt.NoModifier)
			self.keyPressEvent(ap)
                elif e == 1:
                        ap = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,QtCore.Qt.Key_Left,QtCore.Qt.NoModifier)
                        self.keyPressEvent(ap)
                elif e == 2:
                        ap = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,QtCore.Qt.Key_Right,QtCore.Qt.NoModifier)
                        self.keyPressEvent(ap)
                elif e == 3:
                        ap = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,QtCore.Qt.Key_Up,QtCore.Qt.NoModifier)
                        self.keyPressEvent(ap)
                elif e == 4:
                        ap = QtGui.QKeyEvent(QtCore.QEvent.KeyPress,QtCore.Qt.Key_Down,QtCore.Qt.NoModifier)
                        self.keyPressEvent(ap)




#Defines signals to be used for communications between the various threads
class InterruptSignals(QtCore.QObject):
	Key = QtCore.pyqtSignal(QtCore.Qt.Key_Enter.__class__)
	rtcInterrupt = QtCore.pyqtSignal(int)
	operationCompleted = QtCore.pyqtSignal()
	wrapUp = QtCore.pyqtSignal()

#Defines a thread class that operates on the various threads
class switchInterruptThread(QtCore.QThread,InterruptSignals):
	def __init__(self,pin,key,parent=None):
		InterruptSignals.__init__(self)
		QtCore.QThread.__init__(self,parent)
		self.setTerminationEnabled(True)
		self.pin = pin
		self.key = key
		self.active = False
		GPIO.setup(self.pin,GPIO.IN)
	def run(self):
		while self.active==True:
			try:
				if GPIO.input(self.pin)==0:
					sleep(0.08)
					if GPIO.input(self.pin)==0:
				#GPIO.wait_for_edge(self.pin,GPIO.FALLING)
				#print `self.pin` + "Pressed"
						self.emit(QtCore.SIGNAL("keyDecode(int)"),self.key)	
			except KeyboardInterrupt: 
				print "Exiting"
			sleep(0.1)
def main():
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	app = QtGui.QApplication(sys.argv)
	UI = Photometer()
#	sys.exit(app.exec_())
	app.exec_()
	print "GPIO cleaning"
#	GPIO.cleanup()

if __name__=='__main__':
	main()
