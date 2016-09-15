################################
### AUTOMATIC PDF COMPRESSOR ###
################################

from __future__ import print_function          ### Safe Thread Print ###
print = lambda x: sys.stdout.write("%s\n" % x) ### ''''''''''''''''' ###
import os
import sys
import subprocess
import time
import Queue
import threading
import time
import pickle


### Generally the scanned folder locations  ###
### to compress incoming pdfs               ###
FOLDER_LOCS = ["T:\\reception 2","T:\\reception 3","T:\\boris"]

### Output directories, generally going to  ###
### the same for processed pdfs             ###
OUTPUT_FOLDER_LOCS = ["T:\\reception 2","T:\\reception 3","T:\\boris"]

### To Enable Debug Prompts (Recommended: False) ###
DEBUG = False

### Enable PDF Compression Prompts (Recommended: True) ###
COMPLETION_PROMPTS = True

### PDF Reducer 2 Pro EXE Location ###
PDFC_LOC = "C:\Program Files\ORPALIS\PDF Reducer 2 Professional Edition\pdfReducer.exe"

### Log File Name and Location ###
LOG_FILE = "T:\\boris\\pdflog.txt"

### Status Monitoring Functions ###
def info(message):
    print ("[INFO] " + str(message))

def warning(message):
    print ("[WARNING] " + str(message))

def critical(message):
    print ("[CRITICAL] " + str(message))

def error(message):
    print ("[ERROR] " + str(message))

def fileio(message):
    print ("[FILE I/O] " + str(message))

def debug(message):
    if DEBUG:
        print ("[DEBUG] " + str(message))

def success(message):
    if COMPLETION_PROMPTS:
        print ("[SUCCESS] " + str(message))

### File Change Monitoring Functions - Taken From ScannedDocumentSorter ###
def getFileSize(path):
    try:
        f = open(path, "rb")
    except IOError:
        debug("In Process Copy File Permission Error: Access Denied Accessing Path: " + str(path))
        return 0
    old_file_position = f.tell()
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(old_file_position, os.SEEK_SET)
    f.close()
    return size

def isFileChange(path):
    size_0 = getFileSize(path)
    time.sleep(0.5) # Wait 0.5 seconds before checking file size again #
    size_1 = getFileSize(path)
    debug("File: %s, Size 1: %d, Size 2: %d, Diff: %d" % (path, size_0, size_1, size_1 - size_0))
    if size_0 == size_1:
        return False
    return True

def isFileChange2(path):
    modTime1 = os.path.getmtime(path)
    time.sleep(0.5) # Wait 0.5 seconds before checking if modified #
    modTime2 = os.path.getmtime(path)
    if modTime1 == modTime2:
        return False
    return True

def filehash(filepath, blocksize=4096):
    """ Return the hash hexdigest for the file `filepath', processing the file
    by chunk of `blocksize'.

    :type filepath: str
    :param filepath: Path to file

    :type blocksize: int
    :param blocksize: Size of the chunk when processing the file

    """
    sha = hashlib.sha256()
    with open(filepath, 'rb') as fp:
        while 1:
            data = fp.read(blocksize)
            if data:
                sha.update(data)
            else:
                break
    return sha.hexdigest()

def isFileChange3(path):
    file_hash_1 = filehash(path)
    time.sleep(0.1)
    file_hash_2 = filehash(path)
    if file_hash_1 == file_hash_2:
        return False
    return True

def checkAllFilesForChanges(directory): # Check if Able to Proceed to Copy Phase # False = NOT able to proceed, changes still occuring # True = All Okay
    files_to_check = []
    
    for fi in getFiles(directory):
        if fi not in COMPLETED_FILES: ### Added to prevent redundancy if file already has been compressed ###
            fileio("New Document Detected: '" + fi + "', adding to compression queue!")
            files_to_check.append(fi)
    
    for fi in files_to_check:
        for x in range(0, 9):
            if isFileChange2(directory + '\\' + fi):
                debug("File Change on MTime Pass %d Failed!" % x)
                return False
            elif isFileChange(directory + '\\' + fi):
                debug("File Change on Size Pass %d Failed!" % x)
                return False

    return True

def checkFileForChanges(fi): ## Fi: File and Directory Located
    for x in range(0, 9):
        if isFileChange2(fi):
            debug("File Change on MTime Pass %d Failed!" % x)
            return False
        elif isFileChange(fi):
            debug("File Change on Size Pass %d Failed!" % x)
            return False
    return True

def waitForChangeCompletion(directory):
    info("File Changes Confirmed! Waiting for completion...")
    while True:
        if checkAllFilesForChanges(directory):
            success("File Changes Completed!")
            break
def waitForFileChangeCompletion(fi): ## Fi: File and Directory
    info("File Change Confirmed! Waiting for completion...")
    while True:
        if checkFileForChanges(fi):
            success("File Change Completed!")
            break
        
### System File Directory Functions ###
def checkPath(path):
    return os.path.exists(path)

def checkPaths(paths):
    for path in paths:
        if not checkPath(path):
            return False
    return True

def isFolderFilled(path):
    return len(getFiles(path)) > 0

def getFiles(mypath):
    try:
        onlyfiles = [ f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath,f)) ]
    except WindowsError:
        time.sleep(2)
        getFiles(mypath)
    return onlyfiles

def folderContainsNonprocessedFiles(directory): ### If the folder contains a file that has not been compressed, return True. Else, return False ###
    for fi in getFiles(directory):
        if fi not in COMPLETED_FILES:
            return True
    return False

### Run PDF Compressor Pro ###
def runPDFC(pdfReducerCompressionEXE, inputfile, outputfolder):
    debug([pdfReducerCompressionEXE, "/Min", "/F", inputfile, "/D", outputfolder, "/T", "2", "/Q", "3", "/MRC", "/DD"])
    subprocess.call([pdfReducerCompressionEXE, "/Min", "/F", inputfile, "/D", outputfolder, "/T", "2", "/Q", "3", "/MRC", "/DD"])

def runPDFCG(inputfile, directory):
    runPDFC(PDFC_LOC, inputfile, OUTPUT_FOLDER_LOCS[directory])

def log(log_file, data_to_store):
    fileLock.acquire()
    with open(log_file, 'rb') as f:
        entrySet = pickle.load(f)
    entrySet.append(data_to_store)
    with open(log_file, 'wb') as f:
        pickle.dump(entrySet, f)
    fileLock.release()

def read_from_log(log_file):
    fileLock.acquire()
    with open(log_file, 'rb') as f:
        entrySet = pickle.load(f)
        #print (entrySet)
        fileLock.release()
        return entrySet
    fileLock.release()
    
    

### Temporary Array to Store Already Compressed PDFs ###
COMPLETED_FILES = []

### Threading Class and Auxiliary Functions ###

# Class Header for File Processing Thread #
class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print("Starting " + self.name)
        process_data(self.name, self.q)
        print("Exiting " + self.name)
        
    

# The Thread Calls This Function to Run PDF Compressor and Check for Size Changes #
def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get() # Data will be formatted as [Directory + Filename, Directory ID (0, 1, 2 correponding to place of array FOLDER_LOCS) #
            COMPLETED_FILES.append(data[0]) # Prevent adding file back into queue before thread finishes (and lock releases)
            queueLock.release()
            print("%s processing %s" % (threadName, data[0]))
            if checkFileForChanges(data[0]):
                runPDFCG(data[0],data[1])
            else:
                waitForFileChangeCompletion(str(data[0]))
                runPDFCG(data[0],data[1])
            print("%s Compression Completed: '%s'" % (threadName, data[0]))
            #log(LOG_FILE, data[0])
        else:
            queueLock.release()
        time.sleep(1)

###########################################
### Main Threading Starter and Function ###
###########################################
if __name__ == "__main__":
    exitFlag = 0
    queueLock = threading.Lock()
    fileLock = threading.Lock()
    nesting = 0
    workQueue = Queue.Queue(25) ## Increase Queue size limit
    threads = []
    threadID = 1

    # Load previously compressed files from log
    #for fi in read_from_log(LOG_FILE):
    #    #print (str(fi))
    #    COMPLETED_FILES.append(fi)
        
    # Create new threads
    for tCount in xrange(0, 10): ## Increase number of Threads created
        thread = myThread(threadID, "[Thread-"+str(tCount)+"]", workQueue)
        thread.start()
        threads.append(thread)
        threadID+=1

    while True: ## Continue to fill the queue with new files - Loop just this section to keep the compression queue populated at all times ##
        try:
            time.sleep(1) ## Allow 1s for queue to refill ------ This section is all Main Thread ------
            queueLock.acquire()
            for directory in xrange(0, len(FOLDER_LOCS)):
                for fi in getFiles(FOLDER_LOCS[directory]):
                    file_and_dir = str(os.path.join(FOLDER_LOCS[directory],fi))
                    if file_and_dir not in COMPLETED_FILES and 'Box' in (file_and_dir):
                        COMPLETED_FILES.append(file_and_dir)
                        warning("Appended '%s' to completed directory!" % file_and_dir)
                    if file_and_dir not in COMPLETED_FILES:
                        fileio("New Document Detected: '" + str(FOLDER_LOCS[directory] + "\\" + fi) + "', adding to compression queue!")
                        workQueue.put([FOLDER_LOCS[directory] + "\\" + fi, directory])
            queueLock.release()
        except KeyboardInterrupt:
            # Wait for queue to empty
            while not workQueue.empty():
                pass
            # Notify threads it's time to exit
            exitFlag = 1

            # Wait for all threads to complete
            for t in threads:
                t.join()
            print ("Exiting Main Thread")
            exit(1) # Exit code 1, exited peacefully
            

        # Wait for queue to empty
        while not workQueue.empty():
            pass

    


            
