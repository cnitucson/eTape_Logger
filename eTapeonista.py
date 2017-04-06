import ui
import console
import cb
import struct
import clipboard
import sound

measurements = list()

def copyToClipboard(sender):
	printList = ','.join(str(x) for x in measurements)
	clipboard.set(printList)

def clearMeasurements(sender):
	global measurements
	measurements = []
	printList = ','.join(str(x) for x in measurements)
	v['measurements'].text = printList

def button_tapped(sender):
	console.alert(sender.title)

v = ui.load_view()
v.present('fullscreen')

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
				
	def did_update_value(self, c, error):
		v['bluetoothIcon'].background_color = '#2C82C9'
		v['connectionLabel'].text = 'Connected'
		inches = struct.unpack('<H',c.value)[0]/64
		cm = round(inches*2.54,1)
		if cm >= 2600:
			cm = 0.0
		print(str(cm)+' centimeters')
		measurements.append(cm)
		printList = '\n'.join(str(x) for x in measurements)
		v['measurements'].text = printList
#		sound.play_effect('Click_1')
		
mngr = eTapeManager()
cb.set_central_delegate(mngr)
cb.scan_for_peripherals()
if cb.get_state() == 5:
	test = True
#	v['bluetoothIcon'].background_color = '#2C82C9'
#	v['connectionLabel'].text = 'Connected'
print(cb.CH_PROP_NOTIFY)
while not mngr.peripheral:
	pass
