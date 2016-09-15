import shutil, random, time

def randomCopy():
    src_file = ""
    dest = ("T:\\reception 1\\%d.pdf" % (random.randint(1,25)))
    shutil.copy(src_file, dest)
    time.sleep(10)

while True:
    randomCopy()
