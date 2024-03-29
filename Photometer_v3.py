#!/usr/bin/python

import sys
from PyQt4 import QtGui,QtCore
import UI
import RPi.GPIO as GPIO
from time import sleep
import csv
from PCF8563 import PCF8563
from hx711 import HX711


#Test
class Photometer(QtGui.QMainWindow,UI.Ui_MainWindow):
	def __init__(self,parent=None):

	#Basic Initialization

		super(Photometer,self).__init__(parent)
		self.setupUi(self)
		self.selectionState = 0		# Tracks the state of GUI
                self.startSetting = 0		# Stores the start mode
                self.endSetting = 0		# Stores the end mode
		self.buttonStart = False
		self.buttonEnd = False
	#Pin Assignments

		self.left = 16
		self.right = 21
		self.up = 12

		self.down = 26
		self.ok = 20
	
		self.rtcInt = 14
		self.hxDat = 15
		self.hxSck = 18
		
		self.led = 23
		self.buzzer = 24
		self.power = 19
		

	#Connections and Threads Setup
         
		self.setupSignals()
		self.setupControl()
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
				self.operationReady = 1
				self.goButtonClicked()

			elif self.selectionState == 7:
				self.operationReady = 0
				self.goButtonClicked()
				

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
				if self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.MinuteSection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.HourSection)
                                elif self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.HourSection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.MinuteSection)
                                
                        elif self.selectionState == 3:
                                if self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.MinuteSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.HourSection)
                                elif self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.HourSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.MinuteSection)
                                
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
                                if self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.HourSection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.MinuteSection)
                                elif self.startTimeEdit.currentSection() == QtGui.QDateTimeEdit.MinuteSection:
                                        self.startTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.HourSection)
		
                        elif self.selectionState == 3:
                                if self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.HourSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.MinuteSection)
                                elif self.endTimeEdit.currentSection() == QtGui.QDateTimeEdit.MinuteSection:
                                        self.endTimeEdit.setCurrentSection(QtGui.QDateTimeEdit.HourSection)


		elif e.key() == QtCore.Qt.Key_Up:
			if self.startTimeEdit.isEnabled()==True:
				time = self.startTimeEdit.time()
				if self.startTimeEdit.currentSection() == 0x0010:
					if time.hour()+1 == 24:
						 time.setHMS(0,time.minute(),0)					
					else:					
						time.setHMS(time.hour() + 1,time.minute(),0)
						
					self.startTimeEdit.setTime(time)
				elif self.startTimeEdit.currentSection() == 0x0008:
					if time.minute()+1 == 60:
						 time.setHMS(time.hour(),0,0)					
					else:					
						time.setHMS(time.hour(),time.minute()+1,0)
						
					self.startTimeEdit.setTime(time)
			elif self.endTimeEdit.isEnabled()==True:
				time = self.endTimeEdit.time()
				if self.endTimeEdit.currentSection() == 0x0010:
					if time.hour()+1 == 24:
						 time.setHMS(0,time.minute(),0)					
					else:					
						time.setHMS(time.hour() + 1,time.minute(),0)
						
					self.endTimeEdit.setTime(time)
				elif self.endTimeEdit.currentSection() == 0x0008:
					if time.minute()+1 == 60:
						 time.setHMS(time.hour(),0,0)					
					else:					
						time.setHMS(time.hour(),time.minute()+1,0)
						
					self.endTimeEdit.setTime(time)
			elif self.sampleSelect.isEnabled() == True:
				v = self.sampleSelect.value()
				v = v+10
				if v == 1010:
					v = 10
				self.sampleSelect.setValue(v)
			elif self.rateSelect.hasFocus() == True:
				v = self.rateSelect.value()
				v = v+1
				if v == 11:
					v = 1
				self.rateSelect.setValue(v)

		elif e.key() == QtCore.Qt.Key_Down:
			if self.startTimeEdit.isEnabled()==True:
				time = self.startTimeEdit.time()
				if self.startTimeEdit.currentSection() == 0x0010:
					if time.hour()-1 == -1:
						 time.setHMS(23,time.minute(),0)					
					else:					
						time.setHMS(time.hour() - 1,time.minute(),0)
						
					self.startTimeEdit.setTime(time)
				elif self.startTimeEdit.currentSection() == 0x0008:
					if time.minute()-1 == -1:
						 time.setHMS(time.hour(),59,0)					
					else:					
						time.setHMS(time.hour(),time.minute()-1,0)
					self.startTimeEdit.setTime(time)
			elif self.endTimeEdit.isEnabled()==True:
				time = self.endTimeEdit.time()
				if self.endTimeEdit.currentSection() == 0x0010:
					if time.hour()-1 == -1:
						 time.setHMS(23,time.minute(),0)					
					else:					
						time.setHMS(time.hour() -1,time.minute(),0)
						
					self.endTimeEdit.setTime(time)
				elif self.endTimeEdit.currentSection() == 0x0008:
					if time.minute()-1 == -1:
						 time.setHMS(time.hour(),59,0)					
					else:					
						time.setHMS(time.hour(),time.minute()-1,0)
						
					self.endTimeEdit.setTime(time)
			elif self.sampleSelect.isEnabled() == True:
				v = self.sampleSelect.value()
				v = v-10
				if v == 0:
					v = 1000
				self.sampleSelect.setValue(v)
			elif self.rateSelect.hasFocus() == True:
				v = self.rateSelect.value()
				v = v-1
				if v == 0:
					v = 10
				self.rateSelect.setValue(v)



	def setupControl(self):
                self.rtcThread = RTC()
                self.alarmThread = rtcAlarm(self.rtcInt)
                self.adcThread = ADC(self.hxDat,self.hxSck)
                self.rtcThread.start()
                self.adcThread.start()
                self.alarmThread.start()
                self.rtcThread.active = True
                self.adcThread.connect(self.adcThread,QtCore.SIGNAL("sampleReady(float)"),self.sampleReady)
		self.alarmThread.connect(self.alarmThread,QtCore.SIGNAL("alarmResponse()"),self.alarmResponse)


#Sets up the interconnections between the various threads
	def setupSignals(self):
	
		self.nowStartSelect.setFocus()
		self.nowStartSelect.setEnabled(True)
		self.nowStartSelect.setChecked(True)
		self.goButton.clicked.connect(self.goButtonClicked)

                self.leftKey = switchInterruptThread(self.left,1)
                self.rightKey = switchInterruptThread(self.right,2)
                self.upKey = switchInterruptThread(self.up,3)
                self.downKey = switchInterruptThread(self.down,4)
                self.okKey = switchInterruptThread(self.ok,0)

		self.leftKey.connect(self.leftKey,QtCore.SIGNAL("keyDecode(int)"),self.keyDecode)
		self.rightKey.connect(self.rightKey,QtCore.SIGNAL("keyDecode(int)"),self.keyDecode)
                self.upKey.connect(self.upKey,QtCore.SIGNAL("keyDecode(int)"),self.keyDecode)
                self.downKey.connect(self.downKey,QtCore.SIGNAL("keyDecode(int)"),self.keyDecode)
                self.okKey.connect(self.okKey,QtCore.SIGNAL("keyDecode(int)"),self.keyDecode)

		self.leftKey.active = True
		self.rightKey.active = True
                self.upKey.active = True
                self.downKey.active = True
                self.okKey.active = True

		self.leftKey.start()
		self.rightKey.start()
                self.upKey.start()
                self.downKey.start()
                self.okKey.start()
		


	def goButtonClicked(self):
		if self.selectionState == 6 and self.buttonStart == False:
			#self.control.setParameters(self.startSetting,self.endSetting,self.rate,self.endTime,self.startTime,self.samples)
			self.nowStartSelect.setEnabled(False)
			self.laterStartSelect.setEnabled(False)
                	self.buttonStartSelect.setEnabled(False)
                	self.buttonEndSelect.setEnabled(False)
                	self.timeEndSelect.setEnabled(False)
                	self.sampleEndSelect.setEnabled(False)
                	self.rateSelect.setEnabled(False)
			self.sampleCount = 0


			if self.startSetting == 0:
				if self.endSetting == 1:
					hour = endTime.toString("h")
        	                        minute = endTime.toString("m")
					print "end time: " + hour + ":" + minute
	                                self.rtcThread.setAlarm(hour,minute)
                	                self.alarmThread.active = True
					self.rtcThread.connect(self.rtcThread,QtCore.SIGNAL("alarmResponse()"),self.alarmResponse)
				self.setFileName()
				self.adcThread.active = True
				self.selectionState = 7
			elif self.startSetting == 1:
				hour = self.startTime.toString("h")
				minute = self.startTime.toString("m")
				print "end time: " + hour + ":" + minute
				self.rtcThread.setAlarm(hour,minute)
				self.rtcThread.connect(self.rtcThread,QtCore.SIGNAL("alarmResponse()"),self.alarmResponse)
			elif self.startSetting == 2:
				self.buttonStart = True
		
		elif self.selectionState == 6 and self.buttonStart == True:
			self.setFileName()

			if startSetting == 0:
				if self.endSetting == 1:
					hour = endTime.toString("h")
        	                        minute = endTime.toString("m")
	                                self.rtcThread.setAlarm(hour,minute)
                	                self.alarmThread.active = True
					self.rtcThread.connect(self.rtcThread,QtCore.SIGNAL("alarmResponse()"),self.alarmResponse)
				self.adcThread.active = True
				self.selectionState = 7
			elif startSetting == 1:
				hour = self.startTime.toString("h")
				minute = self.startTime.toString("m")
				self.rtcThread.setAlarm(hour,minute)
				self.rtcThread.connect(self.rtcThread,QtCore.SIGNAL("alarmResponse()"),self.alarmResponse)
			elif startSetting == 2:
				self.buttonStart = True
		
		elif self.selectionState == 6 and self.buttonStart == True:

 			self.adcThread.active = True
			self.selectionState = 7

		elif self.selectionState == 7:


			if self.endSetting == 0:
				self.adcThread.active = False
				self.nowStartSelect.setEnabled(True)
	                        self.nowStartSelect.setChecked(True)
        	                self.laterStartSelect.setEnabled(True)
                	        self.buttonStartSelect.setEnabled(True)
				self.nowStartSelect.setFocus()

				#self.file.close()


				self.selectionState = 0

#			elif endSetting  == 2:

	
	def sampleReady(self,data):
                timestamp = self.rtcThread.timestr
                entry = [timestamp,data]
                self.writer.writerow(entry)
		self.sampleCount = self.sampleCount + 1
		if self.endSetting == 2:
			if self.sampleCount == self.samples:
				self.adcThread.active = False
				self.selectionState = 0
                                self.nowStartSelect.setEnabled(True)
                                self.nowStartSelect.setChecked(True)
                                self.laterStartSelect.setEnabled(True)
                                self.buttonStartSelect.setEnabled(True)
                                self.nowStartSelect.setFocus()
				

        def setFileName(self):
                self.filename = self.rtcThread.getTimeStr() + ".csv"
		self.file = open(self.filename,'a')
                self.writer = csv.writer(self.file)

	def alarmResponse(self):
		if self.selectionState == 6:
			self.setFilename()
			self.adcThread.active = True
			if self.endSetting == 1:
				hour = starttime.toString("h")
                                minute = starttime.toString("m")
                                self.rtcThread.setAlarm(hour,minute)
			self.selectionState = 7
		elif self.selectionState == 7:
			self.adcThread.active = False
			self.selectionState = 0

			#self.file.close()

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

#Defines a thread class that operates on the various threads
class switchInterruptThread(QtCore.QThread):
	def __init__(self,pin,key,parent=None):
		QtCore.QThread.__init__(self,parent)
		self.setTerminationEnabled(True)
		self.pin = pin
	#	self.upPin = 16
	#	self.downPin = 26
	#	self.leftPin = 21
	#	self.rightPin = 12
	#	self.okPin = 20
		self.key = key
		self.active = False
		GPIO.setup(self.pin,GPIO.IN)
            #    GPIO.setup(26,GPIO.IN)
             #   GPIO.setup(21,GPIO.IN)
              #  GPIO.setup(12,GPIO.IN)
               # GPIO.setup(20,GPIO.IN)



	def run(self):
		while True:
			while self.active==True:
				try:
					if GPIO.input(self.pin)==GPIO.LOW:
						sleep(0.08)
						if GPIO.input(self.pin)==GPIO.LOW:
				#GPIO.wait_for_edge(self.pin,GPIO.FALLING)
				#print `self.pin` + "Pressed"
							print self.key
							self.emit(QtCore.SIGNAL("keyDecode(int)"),self.key)	

#                                        if GPIO.input(self.upPin)==GPIO.LOW:
 #                                              sleep(0.3)
  #                                             if GPIO.input(self.upPin)==GPIO.LOW:
   #                                                    self.emit(QtCore.SIGNAL("keyDecode(int)"),3)
    #                                    if GPIO.input(self.leftPin)==GPIO.LOW:
     #                                          sleep(0.3)
      #                                         if GPIO.input(self.leftPin)==GPIO.LOW:
       #                                                self.emit(QtCore.SIGNAL("keyDecode(int)"),1)
        #                                if GPIO.input(self.rightPin)==GPIO.LOW:
         #                                      sleep(0.3)
          #                                     if GPIO.input(self.rightPin)==GPIO.LOW:
           #                                            self.emit(QtCore.SIGNAL("keyDecode(int)"),2)
            #                            if GPIO.input(self.okPin)==GPIO.LOW:
             #                                  sleep(0.3)
              #                                 if GPIO.input(self.okPin)==GPIO.LOW:
               #                                        self.emit(QtCore.SIGNAL("keyDecode(int)"),0)
                #                        if GPIO.input(self.downPin)==GPIO.LOW:
                 #                              sleep(0.3)
                  #                             if GPIO.input(self.downPin)==GPIO.LOW:
                   #                                    self.emit(QtCore.SIGNAL("keyDecode(int)"),4)
					sleep(0.1)
				except KeyboardInterrupt: 
					print "Exiting"
#				self.sleep(100)

class RTC(QtCore.QThread):
	def __init__(self,parent=None):
		QtCore.QThread.__init__(self,parent)
		self.setTerminationEnabled(True)
		self.active = False
		self.rtc = PCF8563(1,0x51)
		#self.time = self.rtc.read_datetime()
	def run(self):
		while True:
			while self.active:
				#self.time = self.rtc.read_datetime()
				self.timestr = self.rtc.read_str()
	def setAlarm(self,hour,min):
		if self.rtc.check_if_alarm_on():
			self.rtc.turn_alarm_off()
		if self.rtc.check_for_alarm_interrupt():
			self.rtc.disable_alarm_interrupt()
		self.rtc.clear_alarm()
		self.rtc.set_daily_alarm(hour,min)
		self.rtc.enable_alarm_interrupt()
		
	def getTimeStr(self):
		return self.timestr

class rtcAlarm(QtCore.QThread):
        def __init__(self,pin,parent=None):
                QtCore.QThread.__init__(self,parent)
                self.setTerminationEnabled(True)
                self.pin = pin
#                self.key = key
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
                                                self.emit(QtCore.SIGNAL("alarmResponse()"))
                        except KeyboardInterrupt:
                                print "Exiting"
                        sleep(0.1)

	

class ADC(QtCore.QThread):
	def __init__(self,data,sck,rate=10,parent=None):
		QtCore.QThread.__init__(self,parent)
		self.setTerminationEnabled(True)
		self.active = False
		self.data = data
		self.sck = sck
		self.rate = rate
		self.adc = HX711(self.data,self.sck)
		self.value = 0
		self.adc.set_reading_format("LSB","MSB")
		self.adc.set_reference_unit(92)
		self.adc.reset()	
		self.adc.tare()
		self.delayval = 1/self.rate

	def run(self):
		while True:
			while self.active == True:
				self.delayval = (1/self.rate)
				print self.delayval
				self.value = self.adc.get_weight(8)
				print self.value
				print self.delayval
				self.emit(QtCore.SIGNAL("sampleReady(float)"),self.value)
				sleep(self.delayval)							
			sleep(0.01)

	def setRate(self,rate):
		self.rate = rate


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
