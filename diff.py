# Felix Blanco
# 12/16/19

import argparse
import binwalk
import pprint
import hashlib
import os
pp  = pprint.PrettyPrinter(indent=2, width=130)

def check_directory_files(imgs, index, module):
	md5sums = []
	paths = []
	results = module.results
	

	for result in results:

		# Looking for files that pertain to this image...
		if imgs[index] in result.file.path:
			
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

def carv2set_md5(imgs, index, module):
	md5s = []
	carvs = []
	results = module.results

	for result in results:

		if imgs[index] in result.file.path:

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

def diff_carvs(imgs, module):

	results = module.results
	sum1, carv1 = carv2set_md5(imgs, 0, module)

	dic1 = {carv1[x]: sum1[x] for x in range(len(sum1))}

	print("[+]                                      ------------ Checking md5sums of carved files! ------------")
	for index in range(1, len(imgs)):
		common_carvs_diff_md5 = []

		print("[+] ------ Common Carvs with different md5sums img1 -> img" + str(index+1) +" ------")

		sum_t, carv_t = carv2set_md5(imgs, index, module)

		dic_t = {carv_t[x]: sum_t[x] for x in range(len(sum_t))}
	
		common_carvs_diff_md5 = []

		# Now we will get only the intersection of common files that have different hashes...
		for com_carv in list( set(dic1).intersection(set(dic_t)) ):

			if dic1[com_carv] != dic_t[com_carv]:

				common_carvs_diff_md5.append([dic1[com_carv], dic_t[com_carv], com_carv])

		pp.pprint(common_carvs_diff_md5)

		if args.spec:

			print("[+] ------ Carvs that are only in img1 or img" + str(index+1) +" ------")
			img1_carvs = list(set(carv1).difference(set(carv_t)))
			img2_carvs = list(set(carv_t).difference(set(carv1)))
			diff_carvs = []
			for carv in img1_carvs:
				diff_carvs.append(['1', carv])

			for carv in img2_carvs:
				diff_carvs.append(['2', carv])

			pp.pprint(diff_carvs)
		
		
def diff_root_fs(imgs, module):

	results = module.results
	file_sum1, file_path1 = check_directory_files(imgs, 0, module)

	print("[+]                                      ------------ Checking md5sum of rfs files! ------------")
	for index in range(1, len(imgs)):

		common_path_diff_md5 = []

		print("[+] ------ Common Files with different md5sums img1 -> img" + str(index+1) +" ------")

		file_sum_t, file_path_t = check_directory_files(imgs, index, module)

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


parser = argparse.ArgumentParser(description='Pass an image and list of images to compare your image with.')
parser.add_argument('--img', required=True, type=str, help="Image you are analyzing.")
parser.add_argument('--img_lst', required=True, type=str, help="List of images you would like to analyze against")
parser.add_argument('--spec', dest='spec', action='store_true', help='Show carvs specific to each image.')
parser.set_defaults(spec=False)

args = parser.parse_args()

img_lst = [args.img]

# Append all images into a huge list!
# Always make sure the image you are analyzing is the first in the list.
for line in open(args.img_lst):
	line = line.rstrip('\n') 
	img_lst.append(line)

for module in binwalk.scan(*img_lst, signature=True, quiet=True, extract=True):
	results = module.results

	print("[+]                                      ------------ Analyzing the following images ------------")
	pp.pprint(img_lst)
	print("")

	diff_carvs(img_lst, module)
	print("")

	diff_root_fs(img_lst, module)
	print("")
