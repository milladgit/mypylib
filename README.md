# mypylib

Some useful Python libs

These are some usefule Python libraries that I wrote for myself.

---

## DeepSize

Useful tool to learn about size of files and subfolders of a folder. 


```
$ python deepsize.py --help

deepsize.py [options] path


Options:
	     -files, --files:	Show results only for files in the folder
	       --help, -help:	Show this help message
	               -1024:	Show in 1024 bytes (KiB, MiB, GiB, ...)
	         -1000 (def):	Show in 1000 bytes (KB, MB, GB, ...)

Sort the results:
	                 -ss:	By file size
```


### Examples:

```
python deepsize.py -1024 /usr/lib
python deepsize.py -1000 ./
python deepsize.py --files -1000
```

---
