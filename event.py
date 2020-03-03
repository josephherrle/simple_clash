from datetime import datetime
import os
import csv

class Event:
	log_path = 'log.csv'
	log_initialized = False
	fields=[]
	fields.append('ets')
	fields.append('uid')
	fields.append('evt_src')
	fields.append('cts')
	fields.append('sts')
	fields.append('dts')
	fields.append('cat')
	fields.append('src')
	fields.append('act')
	fields.append('tgt')
	fields.append('src_cur_id')
	fields.append('src_cur_amt')
	fields.append('snk_cur_id')
	fields.append('snk_cur_amt')

	def __init__(self,payload):
		# print("Event in init()")
		
		line = dict.fromkeys(Event.fields)	
		line.update(payload)
		# add system fields
		dts = datetime.now()
		# effective timestamp is server time, else client time, else database time
		if 'sts' in payload:
			ets = payload['sts']
		elif 'cts' in payload:
			ets = payload['cts']
		else:
			ets = dts
		line.update({'dts':dts,'ets':ets})
		self.write(line.values())

	def write(self,line):
		print("Event in write()")
		with open(Event.log_path,'a',newline='') as log:					
			log_writer=csv.writer(log)
			log_writer.writerow(line)

def main():
	print("In events.py main()")
	if os.path.exists(Event.log_path):
		os.remove(Event.log_path)
	self.write(Event.fields)