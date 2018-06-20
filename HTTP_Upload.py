# used with windows and Linux - not defined python environment - python version 2.7.11
# HTTP Upload.
#
# This module is used to download from and upload to a server
# with many different optional arguments.

import time
import sys
import pip
import threading


class PIPError(Exception):
    pass

# Check for requests module, if not present install it
try:
    import requests
except ImportError:
    try:
        pip.main(['install', 'requests'])
        import requests
    except ImportError as e:
        import requests
        sys.exit('Install pip and requests and then run,...Error: %s' % e)
    except PIPError as e:
        sys.exit('Install pip and requests and then run,...Error: %s' % e)

# Check for poster module, if not present install it
try:
    import poster
    from poster.encode import multipart_encode
except ImportError:
    try:
        pip.main(['install', 'poster'])
        import poster
        from poster.encode import multipart_encode
    except ImportError as e:
        import poster
        from poster.encode import multipart_encode
        sys.exit('Install pip and poster and then run,...Error: %s' % e)
    except PIPError as e:
        sys.exit('Install pip and poster and then run,...Error: %s' % e)

__version__ = '0.1'
__author__ = 'Shashank Devaraj'
__date__ = '02nd April 2017'

# global variables
Upload_Time = Upload_Bytes = Upload_Done = Total_Upload_Bytes_Done = Total_Upload_Time = Started_Upload = Start_Time = \
    End_Time = Upload_Bytes_List = None


class IterableToFileAdapter(object):
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.length = iterable.total

    def read(self, size=-1):
        return next(self.iterator, b'')

    def __len__(self):
        return self.length


# define multi part encode for requests
def multipart_encode_for_requests(params, boundary=None, cb=None):
    datagen, headers = multipart_encode(params, boundary, cb)
    return IterableToFileAdapter(datagen), headers


# display the progress, number of bytes uploaded
def progress(param, current, total):
    global Upload_Bytes_List, Started_Upload, Start_Time, Upload_Done, End_Time
    if Upload_Done:
        return
    if not Started_Upload:
        Started_Upload = True
        Start_Time = time.time()
    if param:
        print "{0} ({1}) - {2:d}/{3:d} - {4:.2f}%".format(param.name, param.filename, current, total,
                                                          float(current)/float(total)*100)
        Upload_Bytes_List.append(float(current))
        End_Time = time.time()
        if Upload_Time:
            if Upload_Time <= End_Time - Start_Time:
                Upload_Done = True
        if Upload_Bytes:
            if Upload_Bytes <= float(current):
                Upload_Done = True


# define requests to post to php to put
def startrequest(username, password, uploadUrl, uploadfile):
    global Upload_Done
    # define datagen and headers for requests
    datagen, headers = multipart_encode_for_requests({
        "fileToUpload": open(uploadfile, "rb"),
    }, cb=progress)
    try:
        uploadrequest = requests.post(
            uploadUrl,
            auth=(username, password),
            data=datagen,
            headers=headers
        )
        print uploadrequest, uploadrequest.text
        Upload_Done = True
    except requests.ConnectionError as e0:
        print 'Error in Connection. Error: %s' % e0
        return False, 'Error is Connection. Error: %s' % e0
    except Exception as e1:
        print 'Error in uploading request posr. Error: %s' % e1
        return False, 'Error is uploading request post. Error: %s' % e1


def startuploading(username, password, uploadUrl, uploadfile, uploadTime=None, uploadBytes=None):
    # initialize the global variables
    global Upload_Time, Upload_Bytes, Upload_Done, Started_Upload, Total_Upload_Time, Total_Upload_Bytes_Done, \
        Upload_Bytes_List
    # check for upload time or bytes threshold if defined
    if uploadTime:
        Upload_Time = int(uploadTime)
    if uploadBytes:
        Upload_Bytes = long(uploadBytes)
    Upload_Done = Started_Upload = False
    Upload_Bytes_List = []

    print 'Starting Upload....'
    Upload_Thread = threading.Thread(target=startrequest, name="startrequest", args=[username, password, uploadUrl,
                                                                                     uploadfile])
    Upload_Thread.daemon = True
    Upload_Thread.start()
    # if upload done, break and calculate the stats
    while True:
        time.sleep(1)
        if Upload_Done:
            break
    # send the result to called
    Total_Upload_Time = End_Time - Start_Time
    Total_Upload_Bytes_Done = max(Upload_Bytes_List)
    Upload_Rate = (Total_Upload_Bytes_Done * 8) / (Total_Upload_Time * 1000)
    print 'Uploading Done!!!. With Total Bytes [%s] and Total Time [%s] and with Upload Rate [%s]' \
          % (Total_Upload_Bytes_Done, Total_Upload_Time, Upload_Rate)
    if Upload_Done:
        sys.exit('Uploading is Done. Hence, Exit!!!')
    return True, 'Uploading Done!!!. With Total Bytes [%s] and Total Time [%s] and with Upload Rate [%s]' % (
        Total_Upload_Bytes_Done, Total_Upload_Time, Upload_Rate)

# main starts here, get args and call start upload
if __name__ == '__main__':
    if sys.argv[5] == '000':
        uploadtime = None
    else:
        uploadtime = str(sys.argv[5])
    if sys.argv[6] == '000':
        uploadbytes = None
    else:
        uploadbytes = str(sys.argv[6])
    startuploading(str(sys.argv[1]), str(sys.argv[2]), str(sys.argv[3]), str(sys.argv[4]), uploadtime, uploadbytes)
