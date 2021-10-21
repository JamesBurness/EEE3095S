import os
import sys

def main():
	if sys.argv[1] == "threads":
		for y in range(5):
			a = 2**(y+1)
			os.system("make threaded CFLAGS+=\"-D Thread_Count=" + str(a) + "\"")
			for x in range(15):
				os.system("make run_threaded")

	elif sys.argv[1] == "cflags":
		print("1")
		flags = ["","-O0","-O1","-O2","-O3","-Ofast","-Os","-Og","-funroll-loops"]
		for f in flags:
			if sys.argv[2] == "16":
				os.system("make threaded CFLAGS+=\"-D Thread_Count=16 \"" + f)
			else:
				os.system("make default CFLAGS+=" + f)
			for x in range(15):
				if sys.argv[2] == "16":
					os.system("make run_threaded")
				else:
					os.system("make run")
		for f2 in range(8):
			if sys.argv[2] == "16":
				os.system("make threaded CFLAGS+=\"-funroll-loops \"" + flags[f2] + "\" -D Thread_Count=16\"")
			else:
				os.system("make default CFLAGS+=\"-funroll-loops \"" + flags[f2])
			for x in range(15):
                                if sys.argv[2] == "16":
                                        os.system("make run_threaded")
                                else:
                                        os.system("make run")

	elif sys.argv[1] == "py":
		os.system("python ../Python/PythonHeterodyning.py")

	else:
		os.system("make threaded CFLAGS+=\"-funroll-loops -O3 -D Thread_Count=16\"")
		for x in range(15):
			os.system("make run_threaded")

	os.system("make clean")

if __name__ == "__main__":
   main()
