import shutil, random, time

def randomCopy():
    src_file = "C:\\Documents and Settings\\Administrator\\Desktop\\ANDRIA_MAXWELL_MAY_28_2015.pdf"
    dest = ("T:\\reception 1\\%d.pdf" % (random.randint(1,25)))
    shutil.copy(src_file, dest)
    time.sleep(10)

while True:
    randomCopy()
