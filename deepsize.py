
import os, sys
from os import listdir
from os.path import isfile, join



options = dict()


found_error = False
error_file = "log.deepsize.log"


def get_human_readable(sz):
	global options

	unit_string = ""
	unit_coeff = 1
	human_readable_divisor = options["human_readable_divisor"]

	if sz < human_readable_divisor:
		unit_string = "B"
		unit_coeff = 1
	elif sz < human_readable_divisor*human_readable_divisor:
		unit_string = "KiB"
		if human_readable_divisor == 1000: unit_string = "KB"
		unit_coeff = human_readable_divisor
	elif sz < human_readable_divisor*human_readable_divisor*human_readable_divisor:
		unit_string = "MiB"
		if human_readable_divisor == 1000: unit_string = "MB"
		unit_coeff = human_readable_divisor*human_readable_divisor
	else:
		unit_string = "GiB"
		if human_readable_divisor == 1000: unit_string = "GB"
		unit_coeff = human_readable_divisor*human_readable_divisor*human_readable_divisor

	return str(sz/unit_coeff) + " " + unit_string

def show_usage():
	print sys.argv[0] + " [options] path"
	print "\n"
	print "Options:"
	help_messages = dict()
	help_messages["--help, -help"] = "Show this help message"
	help_messages["-1024"] = "Show in 1024 bytes (KiB, MiB, GiB, ...)"
	help_messages["-1000 (def)"] = "Show in 1000 bytes (KB, MB, GB, ...)"
	help_messages["-files, --files"] = "Show results only for files in the folder"
	for h, m in help_messages.items():
		print "\t%20s:\t%s" % (h, m)
	sort_msgs = dict()
	print "\nSort the results:"
	sort_msgs["-ss"] = "By file size"
	for h, m in sort_msgs.items():
		print "\t%20s:\t%s" % (h, m)
	print "\n"
	exit(0)

def get_options():
	global options

	options["check_current_folder"] = True
	options["dest_folder"] = "."
	options["human_readable_divisor"] = 1024
	options["sort"] = ""
	options["top"] = -1
	options["onlyfiles"] = False

	i = 1
	while True:
		if i >= len(sys.argv):
			break

		arg = sys.argv[i]
		if arg in ["--help", "-help"]:
			show_usage()
		elif arg == "--current-folder" or arg == "-cf":
			options["check_current_folder"] = True
			options["dest_folder"] = "."
		elif arg == "-1024" or arg == "--1024":
			options["human_readable_divisor"] = 1024
		elif arg == "-1000" or arg == "--1000":
			options["human_readable_divisor"] = 1000
		elif arg in ["-file", "--file", "-files", "--files"]:
			options["onlyfiles"] = True
		elif arg == "--top":
			if i+1 >= len(sys.argv):
				show_usage()
			i += 1
			arg = sys.argv[i]
			try:
				options["top"] = int(arg)
			except ValueError:
				print "Invalid value after TOP flag.\n"
				exit(0)
		elif arg == "-ss": # Sort by size
			options["sort"] = "size"
		elif len(arg)>0 and arg[0] == "-":
			print "Unknown flag:", arg,"\n"
			show_usage()
		else:
			options["dest_folder"] = arg
			options["check_current_folder"] = False

		i += 1

def record_error(file_path, error_type, exp):
	global found_error
	found_error = True

	f = open(error_file, "a")
	f.write("File Path: " + file_path + "\n")
	f.write("{2}({0}): {1}".format(exp.errno, exp.strerror, error_type))
	f.write("\n\n")
	f.close()

def get_size(file_path):
	sz = 0
	try:
		sz = os.path.getsize(file_path)
	except OSError as exp:
		record_error(file_path, "OS Error", exp)
	except IOError as exp:
		record_error(file_path, "I/O Error", exp)
	except:
		record_error(file_path, "Unexpected Error", sys.exc_info()[0])
	return sz

			
def get_folder_size(start_path):
	total_size = 0
	if os.path.isfile(start_path):
		return os.path.getsize(start_path)

	for dirpath, dirnames, filenames in os.walk(start_path):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total_size += get_size(fp)

	return total_size


def get_top_folder_size():
	global options

	path = options['dest_folder']

	try:
		listdir(path)
	except OSError as exp:
		print "--- %s - No such file exists!" % (path)
		record_error(path, "OS Error", exp)
		return


	onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
	onlyfolders = [f for f in listdir(path) if not isfile(join(path, f))]

	filtered_path = onlyfolders
	if options["onlyfiles"]:
		filtered_path = onlyfiles

	total_size = 0
	for f in onlyfiles:
		total_size += get_size(path + "/" + f)

	print "--- [all orphan files]:", get_human_readable(total_size)

	all_list = list()
	count = 0
	bar_length = 10
	for folder in filtered_path:
		sz = get_folder_size(path + "/" + folder)
		all_list.append((folder, sz, get_human_readable(sz)))
		total_size += sz
		count += 1
		percent = 1.0 * count / len(filtered_path)
		bar_length = 10
		hashes = '#' * int(round(percent * bar_length))
		spaces = ' ' * (bar_length - len(hashes))
		sys.stdout.write("\rPercent: [{0}] {1}%".format(hashes + spaces, int(round(percent * 100))))
		sys.stdout.flush()
	print "\r", " "*60,"\r",

	if options["top"] > 0:
		options["sort"] = "size"

	if options["sort"] == "size":
		all_list = sorted(all_list, key=lambda A:A[1], reverse=True)

	if options["top"] > 0:
		top = options["top"]
		all_list = all_list[:top]

	for al in all_list:
		print "--- " + al[0] + ":", al[2]


	print "\nTotal Size:", get_human_readable(total_size)
	return total_size
	


if __name__ == "__main__":

	os.system("rm -f " + error_file)

	print

	get_options()
	get_top_folder_size()

	if found_error:
		print "\n\n*** Errors happened. ***\nPlease check " + error_file + "."

	print "\n\n"

