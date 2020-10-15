
import struct
import codecs

# Msbt file
class Msbt(object):

	def __init__(self):
		self.labels = dict()
		self.attributes = list()
		self.strings = list()

		self.is_valid = False
	
	@staticmethod
	def create_from_file(file_path):
		msbt = Msbt()
		msbt.load_from_file(file_path)
		return msbt

	def load_from_file(self, file_path):
		self.load(open(file_path, 'rb').read())
	
	def load(self, data):
		magic, = struct.unpack_from('8s', data, 0)
		if not magic == b'MsgStdBn':
			print('Invalid magic', magic)
			return
		
		endian, version, section_count, file_size = struct.unpack_from('<HxxHII', data, 8)
		pointer = 0x20

		for section in range(section_count):
			#section_start = pointer
			section_name, section_length = struct.unpack_from('<4sI', data, pointer)
			pointer += 0x10 
			section_data = data[pointer:pointer+section_length]
			if section_name == b'LBL1':
				self.labels = self._load_lbl1(section_data)
			elif section_name == b'ATR1':
				self.attributes = self._load_atr1(section_data)
			elif section_name == b'TXT2':
				self.strings = self._load_txt1(section_data)
			else:
				print(f'Unknown section:', section_name)
			
			# jump to next section
			pointer += (section_length + 0xF) & ~0xF 
	
	# define sections
	def _load_lbl1(self, section_data):
		labels = dict()
		entry_count, = struct.unpack_from('<I', section_data, 0)
		for entry in range(entry_count):
			label_count, offset = struct.unpack_from('<II', section_data, 4 + entry * 8)
			for _ in range(label_count):
				label_length, = struct.unpack_from('b', section_data, offset)
				label_name = codecs.decode(struct.unpack_from(f'{label_length}s', section_data, offset+1)[0], encoding='ascii')
				offset += 1 + label_length
				index, = struct.unpack_from('<I', section_data, offset)
				offset += 4
				labels[label_name] = index

		return labels

	def _load_atr1(self, section_data):
		count, size = struct.unpack_from('<II', section_data, 0)
		return [section_data[8+i*size:8+i*size+size] for i in range(count)]

	def _load_txt1(self, section_data):
		count = struct.unpack_from('<I', section_data, 0)[0]
		offsets = list(struct.unpack_from(f'<{count}I', section_data, 4))
		offsets.append(len(section_data)) # dummy end offset
		data = list()
		for i in range(count):
			txt = section_data[offsets[i]:offsets[i+1]-2]

			while True:
				idx = txt.find(b'\x0e\x002\x00\x16\x00')
				if idx == -1: break
				length, default_case = struct.unpack_from('<HH', txt, idx+6)
				#if default_case > 0:
				#	print(default_case, txt[(idx+10):(idx+10+default_case)].decode('utf-16le'))
				txt = txt[:idx] + txt[(idx+10):(idx+10+default_case)] + txt[(idx+length+8):]
			data.append(txt)
		
		#print(len(data))
		return [codecs.decode(d, 'utf-16le') for d in data]
		#return [codecs.decode(section_data[offsets[i]:offsets[i+1]-2], 'utf-16le') for i in range(count)]

# Testing
if __name__ == "__main__":
	test_file = 'Message_unpack\\114\\String_EUen\\Item\\STR_ItemName_41_Turnip.msbt'
	msbt = Msbt.create_from_file(test_file)
	for label, index in sorted(msbt.labels.items()):
		print(f'{label}: {msbt.strings[index]}')