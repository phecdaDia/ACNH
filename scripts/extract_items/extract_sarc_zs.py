
import sarc
import zstandard
import os

import sys

file_path = sys.argv[1]
output_path = sys.argv[2] 
file_filter = (sys.argv[3] if len(sys.argv) > 3 else '')

# get all files in Message

files = (lambda path: [os.path.join(path, x) for x in os.listdir(path) if x.endswith('sarc.zs') and x.startswith(file_filter)])(file_path)
for file in files:
	archive = sarc.SARC(zstandard.decompress(open(file, 'rb').read()))
	
	for file_name in archive.list_files():
		folders = file_name.split('/')
		folders, name = folders[:-1], folders[-1]
		path = os.path.join(file.partition('.sarc.zs')[0], *folders).replace(file_path, output_path, 1)
		
		# extract the file
		os.makedirs(path, exist_ok=True)
		with open(os.path.join(path, name), 'wb') as output_file:
			output_file.write(archive.get_file_data(file_name))
	print(f'Finished extracting {file} successfully')
		