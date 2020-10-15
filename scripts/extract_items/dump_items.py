
from Msbt import Msbt
import json
import sys
import os
import re

def fixup(name: str): # stolen from github.com/treeki
	if name.startswith('\x0e2'):
		name = name[6:]
	name = name.replace('\x0en\x1e\0', '<name>')
	return name


#print(sys.argv)
if __name__ == "__main__":
	output_file = sys.argv[1]
	base_path = f'Message_unpack'
	language = sys.argv[2]
	base_path = os.path.join(base_path, f'String_{language}')
	
	output = dict()
	"""
	Output structure:
	{
		"file1": [
			{'name':<String>, 'dec_id':<Integer>, 'hex_id':<String>, 'internal_name':<String>}
		],
		"file2": ...
	}
	"""
	load_msbt = lambda path: [(f, Msbt.create_from_file(os.path.join(path, f))) for f in os.listdir(path) if f.endswith('.msbt')]

	item_msbts = load_msbt(os.path.join(base_path, 'Item'))
	for path, msbt in item_msbts:
		name = path.split('\\')[-1][:-5]
		output[name] = list()
		for label, index in msbt.labels.items():
			if label.endswith('_pl'): continue # skip
			item_id = int(label.split('_')[-1], 10)
			item_name = fixup(msbt.strings[index])
			output[name].append({
				'name': item_name,
				'id': [item_id, f'{item_id:04X}'],
				'internal_name': label
			})
		output[name].sort(key=lambda x: x['id'][0])
	
	# load clothing
	# what do we name the section? clothing_<type>?
	# otherwise same format except we add color?
	clothing_names = load_msbt(os.path.join(base_path, 'Outfit', 'GroupName'))
	clothing_colors = load_msbt(os.path.join(base_path, 'Outfit', 'GroupColor'))

	outfitNameMapping = dict()

	for path, msbt in clothing_names:
		outfitType = path.split('_')[-1].split('.')[0]
		for label, index in msbt.labels.items():
			item_name = fixup(msbt.strings[index])
			outfitNameMapping[(outfitType, label)] = item_name
			#print(outfitType, label, item_name)
			# example: Tops 516 open-collar shirt
	#print(sorted([key[1] for key in outfitNameMapping.keys() if key[0] == 'Tops']))

	for path, msbt in clothing_colors:
		outfitType = path.split('_')[-1].split('.')[0]
		dict_name = f'clothing_{outfitType}'
		output[dict_name] = list()
		for label, index in msbt.labels.items():
			item_name = fixup(msbt.strings[index])
			#print(label, index, item_name)
			group_id, _, item_id = label.split('_')
			group_id = group_id
			item_id = int(item_id, 10)
			

			item_id = int(label.split('_')[-1], 10)
			if (outfitType, group_id) not in outfitNameMapping.keys(): 
				print('Unknown outfitType, groupId: ', outfitType, group_id)
				continue
			clothing_name = outfitNameMapping[(outfitType, group_id)]
			output[dict_name].append({
				'name': clothing_name,
				'color': item_name,
				'id': [item_id, f'{item_id:04X}'],
				#'internal_name': label
			})
		# sort by name
		output[dict_name].sort(key=lambda x: x['name'].lower())
	

	# Add BCSV Data!
	item_param = json.loads(open('bcsv_out\\json\\ItemParam.json', 'r', encoding='utf-16le').read())
	item_param = {i['UniqueID']:i for i in item_param}

	for item_group in output.keys():
		for i, item in enumerate(output[item_group]):
			# try to find 
			bcsv_data = item_param.get(item['id'][0], dict())
			output[item_group][i]['price'] = bcsv_data.get('Price', -1)
			if bcsv_data.get('_bcf5d17a', 65535) != 65535:
				diy_id = bcsv_data.get('_bcf5d17a', 65535)
				output[item_group][i]['DiyRecipe'] = [diy_id, f'{diy_id:04X}']

	# dump json
	with open(output_file, 'w', encoding='utf-8') as file:
		j = json.dumps(output, indent=4, ensure_ascii=False)
		j = re.sub(r',\n\s{12,}', r', ', j) # replace 12+spaces to a single space and remove newline
		j = re.sub(r'\n\s{12,}', r'', j) # replace 12+spaces to a single space and remove newline
		j = re.sub(r'\n        }', r'}', j) # replace end of item dicts to be on the same line
		j = re.sub(r'    ', r'\t', j)


		#j = j.replace('\n' + ' ' * 12, ' ')
		#j = j.replace('\n' + ' ' * 8 + '}', '}')
		#j = j.replace(' ' * 4, '\t')
		

		file.write(j)
