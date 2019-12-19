# Felix Blanco
# 12/16/19

import argparse
import binwalk
import pprint
import hashlib
import os
import sys
import glob
import itertools
import shutil

pp  = pprint.PrettyPrinter(indent=2, width=130)

def check_directory_files(img_name, module):
	md5sums = []
	paths = []
	results = module.results
	

	for result in results:

		# Looking for files that pertain to this image...
		if img_name in result.file.path:
			
			# Moving through results...
			if result.file.path in module.extractor.output:

				# Finding results that have been extracted...
				if result.offset in module.extractor.output[result.file.path].extracted:
					
					# Iterating through all found files
					for i in range(0, len(module.extractor.output[result.file.path].extracted[result.offset].files)):

						# Checking if file is a directory...
						root_to_file_system = str(module.extractor.output[result.file.path].extracted[result.offset].files[0])
						if os.path.isdir(root_to_file_system):
							
							directory = root_to_file_system[root_to_file_system.rfind('/'):]						

							# Generating all md5sums for files in directory!
							for root, dirs, filenames in os.walk(root_to_file_system, topdown=True):
								for name in filenames:

									full_path = os.path.join(root, name)

									# Need to fix issue when files are actually symbolic links. Just check if file exists.
									# Also skipping files that symlink to busybox!
									if os.path.isfile(full_path):

										if os.path.islink(full_path):

											if 'busybox' not in os.readlink(full_path): 
												md5_sum = hashlib.md5( open(full_path, 'rb').read() ).hexdigest()

												stripped_path = full_path[full_path.rfind(directory):]

												md5sums.append(md5_sum)
												paths.append(stripped_path)
										else:
											md5_sum = hashlib.md5( open(full_path, 'rb').read() ).hexdigest()

											stripped_path = full_path[full_path.rfind(directory):]

											md5sums.append(md5_sum)
											paths.append(stripped_path)
	return md5sums, paths

def carv2set_md5(img_name, module):
	md5s = []
	carvs = []
	results = module.results

	for result in results:

		if img_name in result.file.path:

			if result.file.path in module.extractor.output:

				# The current extractor output is mine, lets process the extracted file!
				# If the current result is the same offset as a carved file lets add that to the list!
				if result.offset in module.extractor.output[result.file.path].carved:

					filee = str(module.extractor.output[result.file.path].carved[result.offset])

					# Open file and read it to calculate md5sum!
					md5_sum = hashlib.md5( open(filee, 'rb').read() ).hexdigest()
					md5s.append(md5_sum)
					
					parsed_carv = filee[filee.rfind('/'):]					

					carvs.append(parsed_carv)

	return md5s, carvs

def diff_carvs(img1, img2, module):

	results = module.results
	sum1, carv1 = carv2set_md5(img1, module)

	dic1 = {carv1[x]: sum1[x] for x in range(len(sum1))}

	common_carvs_diff_md5 = []

	print("[+] ------ Comparing binwalk carv's. ------")

	print("[+] ------ Shared carvs with different md5sums. ------")

	sum_t, carv_t = carv2set_md5(img2, module)

	dic_t = {carv_t[x]: sum_t[x] for x in range(len(sum_t))}

	common_carvs_diff_md5 = []

	# Now we will get only the intersection of common files that have different hashes...
	for com_carv in list( set(dic1).intersection(set(dic_t)) ):

		if dic1[com_carv] != dic_t[com_carv]:

			common_carvs_diff_md5.append([dic1[com_carv], dic_t[com_carv], com_carv])

	pp.pprint(common_carvs_diff_md5)

	if args.spec:

		print("[+] ------ Carvs that are only in img1 or img2 ------")
		img1_carvs = list(set(carv1).difference(set(carv_t)))
		img2_carvs = list(set(carv_t).difference(set(carv1)))
		diff_carvs = []
		for carv in img1_carvs:
			diff_carvs.append(['1', carv])

		for carv in img2_carvs:
			diff_carvs.append(['2', carv])

		pp.pprint(diff_carvs)
		
		
def diff_root_fs(img1, img2, module):

	results = module.results
	file_sum1, file_path1 = check_directory_files(img1, module)

	common_path_diff_md5 = []
	print("[+] ------ Comparing root-file systems. ------")
	print("[+] ------ Shared files with different md5sums. ------")

	file_sum_t, file_path_t = check_directory_files(img2, module)

	# Now we will get only the intersection of common files that have different hashes...
	common_paths = set(file_path1).intersection(set(file_path_t))

	for path in list(common_paths):

		sum_index1 = file_path1.index(path)
		sum_index2 = file_path_t.index(path)

		# Checking if common files have the same md5 sum, if they don't append them to final list...
		# Also filter out 'lib' files, they usually change due to updates!
		if (file_sum1[sum_index1] not in file_sum_t[sum_index2]) and ('/lib/' not in path):

			common_path_diff_md5.append([file_sum1[sum_index1], file_sum_t[sum_index2], path])

	pp.pprint(common_path_diff_md5)


parser = argparse.ArgumentParser(description='Place all the images you want to compare in the imgs folder! Then run the script!')
parser.add_argument('--img', type=str, help="Specify image you would like to analyze against.")
parser.add_argument('--verbose-carvs', dest='spec', action='store_true', help='Show uncommon carvs.')
parser.add_argument('--clean-up', dest='wipe', action='store_true', help='Clean up extracted directories.')
parser.set_defaults(wipe=False)
parser.set_defaults(spec=False)

args = parser.parse_args()

# Grabbing images from imgs directory...
images = glob.glob(os.getcwd() + '/imgs/*')
images = [f for f in images if os.path.isfile(f)]

combs = []

if args.img is None:

	# Get all combinations of analysis of the images in the directory.
	for comb in itertools.combinations(images, 2):
		combs.append(comb)

# Checking if file passed even exists...
elif os.path.isfile(args.img):

	# We will just compare all the images with the given one.
	for image in images:
		combs.append((args.img, image))

	# Adding user supplied image to the list of images to be extracted.
	images.append(args.img)

else:
	print("[+] - Image passed does not exist! Try again...")
	sys.exit()


print("[+] ------------ Analyzing these images ------------")
pp.pprint(images)
print("")

module = binwalk.scan(*images, signature=True, quiet=True, extract=True)

for img1, img2 in combs:

	print("[+] - Comparing the folowing images...")
	print("[+] -> img1 = " + img1)
	print("[+] -> img2 = " + img2)
	
	diff_carvs(img1, img2, module[0])
	print("")

	diff_root_fs(img1, img2, module[0])
	print("____________________________________________________________________________________________")

if args.wipe:
	for dir in glob.glob(os.getcwd() + '/imgs/_*'):
  		shutil.rmtree(dir)
