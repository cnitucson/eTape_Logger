import ui
import console
import cb
import struct
import clipboard
import sound
import json

settings = 'eTapeonista_settings.json'

measurements = list()
measurementUnits = list()

def copyToClipboard(sender):
	if v['measurementUnits'].selected_index == 0:
		printList = ','.join(str(round(x/64*2.54,1)) for x in measurements)
	else:
		printList = ','.join(str(round(x/64/12,2)) for x in measurements)
	clipboard.set(printList)

def clearMeasurements(sender):
	global measurements
	measurements = []
	global measurementUnits
	measurementUnits = []
	printList = ','.join(str(x) for x in measurements)
	v['measurements'].text = printList

v = ui.load_view()
v.present('fullscreen')

def unitChanger(sender):
	formattedList = list()
	if v['measurementUnits'].selected_index == 0:
		#centimeters
		for value in measurements:
			convertedValue = round(value/64*2.54,1)
			unit = 'cm'
			print(convertedValue)
			formattedList.append(str(convertedValue)+' '+unit)
	else:
		#feet
		for value in measurements:
			convertedValue = round(value/64/12,2)
			unit = 'ft'
			formattedList.append(str(convertedValue)+' '+unit)
	printList = '\n'.join(str(x) for x in formattedList)
	v['measurements'].text = printList

unitChangerAction = v['measurementUnits']
unitChangerAction.action = unitChanger

class eTapeManager (object):
	def __init__(self):
		self.peripheral = None

	def did_discover_peripheral(self, p):
		if p.name and 'eTape' in p.name and not self.peripheral:
			self.peripheral = p
			print('Connecting to eTape...')
			cb.connect_peripheral(p)
	
	def did_connect_peripheral(self, p):
		print('Connected:', p.name)
		print('Discovering services...')
		p.discover_services()
	
	def did_fail_to_connect_peripheral(self, p, error):
		print('Failed to connect: %s' % (error,))
		
	def did_disconnect_peripheral(self, p, error):
		print('Disconnected, error: %s' % (error,))
		v['bluetoothIcon'].background_color = '#E25041'
		v['connectionLabel'].text = 'Not Connected'
		
	def did_discover_services(self, p, error):
		for s in p.services:
			if s.uuid == '23455100-8322-1805-A3DA-78E4000C659C':
				print('Discovered Linear Measure Service, discovering characteristics...')
				p.discover_characteristics(s)
				
	def did_discover_characteristics(self, s, error):
		print('Did discover characteristics...')
		for c in s.characteristics:
			if c.uuid == '23455102-8322-1805-A3DA-78E4000C659C':
				self.peripheral.set_notify_value(c, True)
				v['bluetoothIcon'].background_color = '#2C82C9'
				v['connectionLabel'].text = 'Connected'
				
	def did_update_value(self, c, error):
		v['bluetoothIcon'].background_color = '#2C82C9'
		v['connectionLabel'].text = 'Connected'
		#values are recoreded in 1/64 inch
		value = struct.unpack('<H',c.value)[0]
		if value >= 65000:
			value = 0
		measurements.append(value)
		formattedList = list()
		if v['measurementUnits'].selected_index == 0:
			#centimeters
			for value in measurements:
				convertedValue = round(value/64*2.54,1)
				unit = 'cm'
				formattedList.append(str(convertedValue)+' '+unit)
		else:
			#feet
			for value in measurements:
				convertedValue = round(value/64/12,2)
				unit = 'ft'
				formattedList.append(str(convertedValue)+' '+unit)
		printList = '\n'.join(str(x) for x in formattedList)
		v['measurements'].text = printList
		sound.play_effect('Click_1')
		
mngr = eTapeManager()
cb.set_central_delegate(mngr)
cb.scan_for_peripherals()
while not mngr.peripheral:
	pass
