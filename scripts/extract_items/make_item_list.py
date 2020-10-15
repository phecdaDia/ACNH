import subprocess
import os
import shutil
import sys

print(f'Dumping Item IDs')

# check if files exist

if not os.path.exists('Bcsv\\ItemParam.bcsv'):
	print('Unable to find ItemParam.bcsv in Bcsv directory!')
	exit(1)

languages = [x.partition('_')[2][0:4] for x in os.listdir(f'Message') if x.startswith('String_') and x.endswith('.sarc.zs')]

if not languages: # No languages found
	print('Unable to find any language files in the Message directory!')
	exit(1)
print('Found the following languages: ', languages)
print('All required files seem to be present, proceeding.')

# BCSV parsing 
if os.path.exists('Bcsv_out'):
	shutil.rmtree('Bcsv_out')

print('Building specs')
subprocess.run(['py', 'build_specs.py', 'Bcsv', f'enum.json'])
print('Dumping bcsv')
subprocess.run(['py', 'dump_all_bcsv.py', 'Bcsv', 'Bcsv_out', 'specs.py'])
os.remove('specs.py')



if os.path.exists(f'Message_unpack/'):
	shutil.rmtree(f'Message_unpack/')

print('Extracting Files from sarc.zs')
subprocess.run(['py', 'extract_sarc_zs.py', f'Message', f'Message_unpack', f'String_'])

os.makedirs('item_ids', exist_ok=True)
for language in languages:
	subprocess.run(['py', 'dump_items.py', f'item_ids\\items_{language}.json', language])
	print(f'Finished dumping items for {language}')
