import csv
class controlThread(Qtcore.QThread):
	def __init__(self,parent=None):
		self.rtcsensor=RTC()
		self.hxsensor=ADC(self.rate,self.sck)
		self.rtc_alarm=rtc_interrupt(self.selectionState)
		self.csv=CSV_WRITE()
		self.boost_hw=Boost()
		self.indicators=Indicators()
		self.rtcsensor.connect(self.rtcsensor,Qtcore.SIGNAL(self.hours,self.minutes,self.seconds,self.day,self.month,self.year))
		self.hxsensor.connect(self.hxsensor, Qtcore.SIGNAL(self.data))
		self.rtc_alarm.connect(self.rtc_alarm, Qtcore.SIGNAL(self.interrupt))
		self.active=False
		self.rtcsensor.start()
		self.hxsensor.start()
		self.rtc.start()

		
	def run(self):
		while True:
			while self.active=True:
				self.hxsensor.active=True
				self.rtcsensor.active=True
				self.rtc_alarm.active=True
				self.csv.active=True
				self.boost.active=True
				self.indicators=True






class CSV_WRITE(Qtcore.QThread):
	def __init__(self,data,timestamp,parent=None):
		Qtcore.QThread.__init__(self,parent)
		self.data=data
		self.timestamp=timestamp
		self.writer=csv.writer(open("Datafile.csv",'a'))
		self.active=False
	def run():
		while True:
			while self.active=True:
				while self.active=True:
					row=[self.timestamp,self.data]
					self.writer.writerow(row)
					sleep(0.01)
				


