########################################
### SCANNED DOCUMENT SORTER/ARRANGER ###
########################################

import os
import glob
import time
import cdb
import pickle

DEBUG = False

COMPLETION_PROMPTS = True # Recommended: True

DESIGNATED_SCAN_FOLDER = "T:\\reception 1"

LOG_FILE = "T:\\boris\\pdflog.txt"

FILE_TYPES = ['rg','n','c','x','i','rx','t','h','m','pd','tr','mlr']
FILE_NAMES = ['Registration','Progress Notes', 'Correspondence',
              'Xray','Imaging','Prescriptions', 'Tests','Hospital',
              'Miscellaneous', 'Patient Demographics','Test Results','Misc Lab Results']

### Initialize local flat-file storage ###
db = cdb
db.check_db()

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

def checkAllFilesForChanges(directory): # Check if Able to Proceed to Copy Phase # False = NOT able to proceed, changes still occuring # True = All Okay
    for fi in getFiles(directory):
        for x in range(0, 9):
            if isFileChange2(directory + '\\' + fi):
                debug("File Change on MTime Pass %d Failed!" % x)
                return False
            elif isFileChange(directory + '\\' + fi):
                debug("File Change on Size Pass %d Failed!" % x)
                return False

    return True

def waitForChangeCompletion(directory):
    while True:
        if checkAllFilesForChanges(directory):
            success("File Changes Completed!")
            break

### File System Functions ###
def getFiles(mypath):
    try:
        onlyfiles = [ f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath,f)) ]
    except WindowsError:
        time.sleep(2)
        getFiles(mypath)
    return onlyfiles

def removeFilesInDirectory(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            try:
                os.remove(os.path.join(root, name))
            except:
                retry2 = raw_input(error("Unable to delete file: %s! Retry? (y) " % str(name)))
                if ('n' or 'N') in retry2:
                    return False
                    continue
                else:
                    time.sleep(1)
                    os.remove(os.path.join(root, name))
        return True

def getFullFileType(abbrev):
    global FILE_TYPES
    for num in xrange(0, len(FILE_TYPES)):
        if FILE_TYPES[num] == abbrev:
            return FILE_NAMES[num]
    return ''
        

def rename_in_order(file_order, box_num, directory):
    files_ordered_by_ctime = sorted(glob.iglob(os.path.join(directory, '*')), key=os.path.getctime)
    for num in xrange(0, len(file_order)):
        old_filepath = os.path.join(directory, files_ordered_by_ctime[num])
        new_filepath = os.path.join(directory, "Old" + " " + getFullFileType(file_order[num])) + " " + "Box" + " " + str(box_num) + ".pdf"
        success("Successfully converted: %s to %s" % (old_filepath, new_filepath))
        os.rename(old_filepath, new_filepath)

def wait_for_complete_directory(number_required, directory):
    warning("You specified %d number of files, only %d in folder: '%s'. Waiting..." % (number_required, len(getFiles(directory)),directory))
    while True:
        time.sleep(1)
        number_current = len(getFiles(directory))
        if number_current == number_required:
            if not checkAllFilesForChanges(directory):
                info("%d file(s) reached, waiting for completion..." % number_required)
                waitForChangeCompletion(directory)
            break

def read_from_log(log_file):
    with open(log_file, 'r') as f:
        try:
            entrySet = pickle.load(f)
        except:
            entrySet = []
        return entrySet

def wait_for_compression():
    loopBreak = False
    while not loopBreak:
        time.sleep(1)
        files = getFiles(DESIGNATED_SCAN_FOLDER)
        for x in xrange(0, len(files)):
            if os.path.join(DESIGNATED_SCAN_FOLDER,files[x]) not in read_from_log(LOG_FILE):
                debug(str(os.path.join(DESIGNATED_SCAN_FOLDER,str(files[x]))) + " not found in log: " + str(read_from_log(LOG_FILE)))
                break
            elif x == (len(files)-1):
                loopBreak = True
            

if __name__ == '__main__':

    while True:
        ### User Input for Order of Files ###
        print ('''
        =========================================
        ===    | ----------------------- |    ===
        ===    | Document Arrangment Key |    ===
        ===    | ----------------------- |    ===
        ===                                   ===
        === 1.  Registration = rg             ===
        === 2.  Progress Notes = n            ===
        === 3.  Correspondence = c            ===
        === 4.  Xray = x                      ===
        === 5.  Imaging = i                   ===
        === 6.  Prescriptions = rx            ===
        === 7.  Tests = t                     ===
        === 8.  Hospital = h                  ===
        === 9.  Miscellaneous = m             ===
        === 10. Patient Demographics = pd     ===
        === 11. Test Results = tr             ===
        === 12. Misc Lab Results = mlr        ===
        === 13. Quit Program                  ===
        =========================================
        
        ''')

        
        input_error_count = 0
        while True:
            order_of_scans = raw_input("Order of Documents (i.e: rg,xray,rx,n):  ")
            order_of_scans = [x.strip() for x in order_of_scans.split(',')]

            ### Exit Program Case ###
            try:
                if '13' in order_of_scans:
                    exit(1)
            except:
                pass
            ###                   ###
            
            for ftype in order_of_scans:
                if ftype not in FILE_TYPES:
                  error("Type: '%s' is not a valid file type, please try again." % ftype)
                  input_error_count += 1
            if input_error_count == 0:
                break
            input_error_count = 0
            print "\n"
    
        ###  Order can vary, keep FILE_TYPES updated ###
        ###  for all patient chart types             ###
        
        ###  Retrieve Box ID Number from Database ###
        try:
            db_box_id = db.read_db()['box_id']
        except KeyError:
            db.update_db({'box_id':0})
            db_box_id = 0
        user_box_id = raw_input(("Box ID (Last Used - %s): " % db_box_id))
        if user_box_id is '':
            user_box_id = db_box_id
        else:
            db.update_db({'box_id':user_box_id})
        # user_box_id now contains the box number to be used

        # Final confirmation
        resp_conf = raw_input("Confirm box order: '%s' (y) " % ",".join([str(x) for x in order_of_scans]))
        if resp_conf is 'n':
            continue

        ### Check if already compressed, if not, wait until it is ###
        #for fi in getFiles(DESIGNATED_SCAN_FOLDER):
        #    if fi not in read_from_log(LOG_FILE):
        #        warning("All files have not been compressed yet! Waiting for compression to complete...")
        #        wait_for_compression()
                    

        ### Check to see if all files that were ordered are in the designated scan folder ###
        if len(order_of_scans) != len(getFiles(DESIGNATED_SCAN_FOLDER)):
            # If not, wait until there is!
            wait_for_complete_directory(len(order_of_scans), DESIGNATED_SCAN_FOLDER)
        # Otherwise, rename the files as such
        rename_in_order(order_of_scans, user_box_id, DESIGNATED_SCAN_FOLDER)
        # Offer an option to clear files from folder after completing uploading #
        resp_clear = raw_input("\nWould you like to clear files from directory: '%s'(y)? " % DESIGNATED_SCAN_FOLDER)
        if resp_clear is '' or resp_clear is 'y':
            removeFilesInDirectory(DESIGNATED_SCAN_FOLDER)
            
            
        

        
    
    
    
