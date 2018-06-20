# used with windows and Linux - not defined python environment - python version 2.7.11
#
# Passing on and copying of this document, use and communication of its
# contents is not permitted without prior written authorization.
#
# HTTP Upload and Download.
#
# This module is used to download from and upload to a server
# with many different optional arguments.


import time
import threading
import sys
import subprocess
import os
import signal


class PIPError(Exception):
    pass


# Check for pip module, if not present install it
try:
    import pip
except ImportError:
    try:
        if 'darwin' in sys.platform or 'linux' in sys.platform:
            subprocess.call(['easy_install', 'pip'])
    except ImportError as e:
        import pip
        sys.exit('Install pip and then run,...Error: %s' % e)
    except PIPError as e:
        sys.exit('Install pip and then run,...Error: %s' % e)


# Check for urllib2 module, if not present install it
try:
    import urllib2
except ImportError:
    try:
        pip.main(['install', 'urllib2'])
        import urllib2
    except ImportError as e:
        import urllib2
        sys.exit('Install pip and urllib2 and then run,...Error: %s' % e)
    except PIPError as e:
        sys.exit('Install pip and urllib2 and then run,...Error: %s' % e)

__version__ = '0.1'
__author__ = 'Shashank Devaraj'
__copyright__ = 'Author'
__date__ = '02nd April 2017'


class HTTPDownloadUploadWithAuthentication:

    def __init__(self):
        self.resultDownloadHTTP = self.resultUploadHTTP = -1
        self.Download_File_No = 0
        self.downloadHTTPResult = []
        self.UploadHTTPResult = []
        self.UploadProcessPID = []
        self.startHTTPThread = ['dummy']
        self.startHTTPThreadUpload = ['dummy']
        self.HTTP_Upload_Script_Name = 'HTTP_Upload.py'
        self.abruptStopHTTPDownload = self.TriggerStopHTTPDownload = self.completeHTTPDownload = \
            self.startedHTTPDownload = self.ExceptionHTTPDownload = False
        self.abruptStopHTTPUpload = self.TriggerStopHTTPUpload = self.startedHTTPUpload = \
            self.completeHTTPUpload = self.ExceptionHTTPUpload = False
        print '############# HTTP Download and Upload Initialization Done -- Version : %s #############' % __version__
        print 'Download Command:\nPerformHTTPDownload(username,password,downloadUrl,downloadStreams,downloadTime,' \
              'downloadBufferSize,downloadBytes,downloadtopath)'
        print 'Default Values:\ndownloadStreams=1,downloadTime=till complete,downloadBufferSize=8192,' \
              'downloadBytes=all,downloadtopath=C:\\Tools\\CLA\\3rd_party\\http\\download\\'
        print 'HTTP Upload Script Name: %s' % self.HTTP_Upload_Script_Name
        print 'Upload Command:\nPerformHTTPUpload(username,password,uploadurl,uploadfrom,uploadstreams,' \
              'uploadtime,uploadbytes)'

        # In case if we need to return at initialize do with __new__(cls)

    def PerformHTTPDownload(self, username, password, downloadUrl, downloadStreams=1, downloadTime=None,
                            downloadBufferSize=8192, downloadBytes=None, downloadtopath=None):
        # Validate user input
        if downloadTime:
            downloadTime = int(downloadTime)
        if downloadBytes:
            downloadBytes = long(downloadBytes)
        if not downloadtopath:
            if 'darwin' in sys.platform:
                downloadtopath = '/Applications/Tools/CLA/CLA.app/Contents/MacOS/3rd_party/http/download/'
            elif 'win' in sys.platform:
                downloadtopath = 'C:\\Tools\\CLA\\3rd_party\\http\\download\\'
            elif'linux' in sys.platform:
                downloadtopath = '/Applications/Tools/CLA/CLA.app/Contents/MacOS/3rd_party/http/download/'

        try:
            startHTTPThreadCommandMetric = threading.Thread(target=self.PerformHTTPDownloadMetric,
                                                            name='HTTP Metric Download', args=[str(username),
                                                                                               str(password),
                                                                                               str(downloadUrl),
                                                                                               int(downloadStreams),
                                                                                               downloadTime,
                                                                                               int(downloadBufferSize),
                                                                                               downloadBytes,
                                                                                               str(downloadtopath)])
            startHTTPThreadCommandMetric.daemon = True
            startHTTPThreadCommandMetric.start()
            return True, 'HTTP Download started successfully'
        except Exception as e0:
            print 'Failed to Start HTTP Download with Exception: %s' % e0
            return False, 'Failed to Start HTTP Download with Exception: %s' % e0

    def PerformHTTPDownloadMetric(self, username, password, downloadUrl, downloadStreams=1, downloadTime=None,
                                  downloadBufferSize=8192, downloadBytes=None, downloadtopath=None):
        try:
            self.abruptStopHTTPDownload = self.TriggerStopHTTPDownload = self.startedHTTPDownload = \
                self.completeHTTPDownload = self.ExceptionHTTPDownload = False
            self.resultDownloadHTTP = -1
            self.startHTTPThread = ['dummy']
            self.downloadHTTPResult = []
            self.Download_File_No = 0
            time.sleep(1)  # Avoid race time

            for noofThread in range(1, downloadStreams + 1):
                try:
                    HTTPDownloadThreadName = 'HTTP_Download_' + str(noofThread)
                    startHTTPThreadCommand = threading.Thread(target=self.PerformHTTPDownloadThread,
                                                              name=HTTPDownloadThreadName, args=[username, password,
                                                                                                 downloadUrl,
                                                                                                 downloadTime,
                                                                                                 downloadBufferSize,
                                                                                                 downloadBytes,
                                                                                                 downloadtopath])
                    self.startHTTPThread.append(startHTTPThreadCommand)
                    self.startHTTPThread[noofThread].daemon = True
                    self.startHTTPThread[noofThread].start()
                except Exception as e1:
                    return False, 'Exception Seen in Metric HTTP to start HTTP Thread!!!\nException: %s' % e1
            self.startedHTTPDownload = True
            for noofThread in range(1, downloadStreams + 1):
                try:
                    self.startHTTPThread[noofThread].join()
                except Exception as e2:
                    return False, 'Exception Seen in Metric HTTP in completing the download!!!\nException: %s' % e2
            try:
                print self.downloadHTTPResult, downloadStreams
                self.resultDownloadHTTP = sum(self.downloadHTTPResult) / downloadStreams
                self.completeHTTPDownload = True
                return True, self.resultDownloadHTTP
            except Exception as e3:
                return False, 'Exception Seen in Metric HTTP in aggregating the download result!!!\nException: %s' % e3
        except Exception as e4:
            return False, 'Exception Seen to start Metric HTTP!!!\nException: %s' % e4

    def StopHTTPDownload(self):
        self.abruptStopHTTPDownload = False
        self.TriggerStopHTTPDownload = True
        self.Download_File_No = 0
        time.sleep(1)  # check for abrupt stop
        self.downloadHTTPResult = []
        self.startHTTPThread = ['dummy']
        try:
            if self.ExceptionHTTPDownload:
                print 'Exception in HTTP Download!!!. Please Check!!!'
                self.abruptStopHTTPDownload = self.TriggerStopHTTPDownload = self.startedHTTPDownload = \
                    self.completeHTTPDownload = self.ExceptionHTTPDownload = False
                return False, 'Exception in HTTP Download[-1]!!!. Please Check!!!'
            elif not self.startedHTTPDownload:
                print 'HTTP Download Not started!!!. Please Check!!!'
                self.abruptStopHTTPDownload = self.TriggerStopHTTPDownload = self.startedHTTPDownload = \
                    self.completeHTTPDownload = self.ExceptionHTTPDownload = False
                return False, 'HTTP Download Not started[-1]!!!. Please Check!!!'
            elif not self.completeHTTPDownload:
                print 'HTTP Download Not Completed!!!. Please Check!!!'
                self.abruptStopHTTPDownload = self.TriggerStopHTTPDownload = self.startedHTTPDownload = \
                    self.completeHTTPDownload = self.ExceptionHTTPDownload = False
                return False, 'HTTP Download Not Completed[-1]!!!. Please Check!!!'
            elif self.abruptStopHTTPDownload:
                print 'HTTP Download Stopped Abruptly!!!'
                self.abruptStopHTTPDownload = self.TriggerStopHTTPDownload = self.startedHTTPDownload = \
                    self.completeHTTPDownload = self.ExceptionHTTPDownload = False
                return False, 'HTTP Download Stopped Abruptly[-1]!!!'
        except Exception as e5:
            print 'Exception is stopping HTTP Download. Error: %s' % e5
            return False, 'Exception is stopping HTTP Download. Error: %s' % e5
        self.abruptStopHTTPDownload = self.TriggerStopHTTPDownload = self.startedHTTPDownload = \
            self.completeHTTPDownload = self.ExceptionHTTPDownload = False
        if self.resultDownloadHTTP == 0:
            self.resultDownloadHTTP = -1
        print 'HTTP Download completed successfully with Download Throughput %.3f Kbps' % self.resultDownloadHTTP
        return True, 'HTTP Download completed successfully with Download Throughput [%.3f] Kbps' \
                     '' % self.resultDownloadHTTP

    def PerformHTTPDownloadThread(self, username, password, downloadUrl, downloadTime=None, downloadBufferSize=8192,
                                  downloadBytes=None, downloadtopath=None):
        try:
            self.abruptStopHTTPDownload = False
            self.TriggerStopHTTPDownload = False

            # set up authentication info
            authinfo = urllib2.HTTPBasicAuthHandler()
            authinfo.add_password(realm='the realm',
                                  uri=downloadUrl,
                                  user=username,
                                  passwd=password)

            # used basic http handler, other handlers are available
            handler = urllib2.HTTPBasicAuthHandler(authinfo)

            # build a new opener that adds authentication and caching FTP handlers
            opener = urllib2.build_opener(handler)

            # install it
            urllib2.install_opener(opener)

            u = urllib2.urlopen(downloadUrl)

            # Get information about the file we are about to download
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])

            self.Download_File_No += 1

            # Get file name from url
            file_name = downloadUrl.split('/')[-1]
            file_exte = downloadUrl.split('.')[-1]
            file_name = '%s_%s.%s' % (file_name[: - len(file_exte) - 1], self.Download_File_No, file_exte)
            if downloadtopath.split(os.sep)[-1] == '':
                full_file_name = '%s%s' % (downloadtopath, file_name)
            else:
                full_file_name = os.path.join(downloadtopath, file_name)
                
            print "Download File Name: %s, Size: %s" % (file_name, file_size)

            # Create a file to write the data from url
            f = open(full_file_name, 'wb')
            file_size_dl = 0
            buffer_size = downloadBufferSize
            print 'Buffer Size is: %s' % buffer_size
            # start reading and writing the data
            print '#############Starting HTTP Download#############'
            start_time = time.time()
            print 'Start Time of HTTP Download is %s' % start_time
            while True:
                # read data from url
                bufferdata = u.read(buffer_size)
                if not bufferdata:
                    end_time = time.time()
                    break
                file_size_dl += len(bufferdata)
                # write data to local
                f.write(bufferdata)
                if downloadBytes is not None:
                    if file_size_dl >= int(downloadBytes):
                        print 'Downloaded Expected Number of Bytes!!!'
                        end_time = time.time()
                        break
                if downloadTime is not None:
                    if time.time() >= start_time + int(downloadTime):
                        print 'Downloaded Data Successfully For %.2f Seconds!!!' % float(time.time() - start_time)
                        end_time = time.time()
                        break
                if self.TriggerStopHTTPDownload:
                    self.abruptStopHTTPDownload = True
                    print 'HTTP Download Stopped Abruptly!!!'
                    return False, 'HTTP Download Stopped Abruptly!!!'

            # calculate the download time
            download_time = end_time - start_time

            print '************End HTTP Download************'
            print 'End Time of HTTP Download is %s' % end_time

            # download is done. close the file now
            f.close()

            # calculate the data rate
            download_rate = float(file_size_dl * 8) / (int(download_time) * 1000)
            print 'Total number of bytes downloaded is %d with time %d Seconds' \
                  % (int(file_size_dl), int(download_time))
            print 'Download Throughput is %.3f Kbps' % download_rate
        # in case of exception
        except urllib2.HTTPError as e6:
            self.ExceptionHTTPDownload = True
            error_message = 'None'
            error_code = 'None'
            if hasattr(e6, 'code'):
                print('The server could not fulfill the request.')
                print ['Error code: ', e6.code]
                error_code = e6.code
            if hasattr(e6, 'msg'):
                print ['Error Message: ', e6.msg]
                error_message = e6.msg
            print 'Error Code: %s with Error Message: %s ' % (error_code, error_message)
            self.downloadHTTPResult.append('Error Code: %s with Error Message: %s ' % (error_code, error_message))
            return False, 'Error Code: %s with Error Message: %s ' % (error_code, error_message)
        except urllib2.URLError as e7:
            self.ExceptionHTTPDownload = True
            error_reason = 'None'
            if hasattr(e7, 'reason'):
                print('We failed to reach a server.')
                print ['Reason for Failure: ', e7.reason]
                error_reason = e7.reason
            print 'Failed to Reach Server. Reason is: %s' % error_reason
            self.downloadHTTPResult.append('Failed to Reach Server. Reason is: %s' % error_reason)
            return False, 'Failed to Reach Server. Reason is: %s' % error_reason
        except ValueError as e8:
            self.ExceptionHTTPDownload = True
            print 'Value Error: %s' % e8
            self.downloadHTTPResult.append('Value Error: %s' % e8)
            return False, 'Value Error: %s' % e8
        except Exception as e9:
            self.ExceptionHTTPDownload = True
            print 'Exception seen in HTTP Download. Exception: %s' % e9
            self.downloadHTTPResult.append('Exception seen in HTTP Download. Exception: %s' % e9)
            return False, 'Exception seen in HTTP Download. Exception: %s' % e9
        else:
            self.downloadHTTPResult.append(float(download_rate))
            print 'Process finished without any Exception!!!'
            return True, 'Process finished without any Exception!!!'

    def PerformHTTPUpload(self, username, password, uploadurl, uploadfrom, uploadstreams=1,
                          uploadtime=None, uploadbytes=None):
        # Validate user input
        if uploadtime:
            uploadtime = int(uploadtime)
        if uploadbytes:
            uploadbytes = long(uploadbytes)

        try:
            Upload_Thread = threading.Thread(target=self.PerformHTTPUploadMetric, name='Base_Http_Upload_Thread',
                                             args=[username, password, uploadurl, uploadfrom, uploadstreams,
                                                   uploadtime, uploadbytes])
            Upload_Thread.daemon = True
            Upload_Thread.start()
            return True, 'HTTP Upload started successfully'
        except Exception as e10:
            print 'Failed to Start HTTP Upload with Exception: %s' % e10
            return False, 'Failed to Start HTTP Upload with Exception: %s' % e10

    def PerformHTTPUploadMetric(self, username, password, uploadurl, uploadfrom, uploadstreams=1,
                                uploadtime=None, uploadbytes=None):
        self.abruptStopHTTPUpload = self.TriggerStopHTTPUpload = self.startedHTTPUpload = \
            self.completeHTTPUpload = self.ExceptionHTTPUpload = False
        self.startHTTPThreadUpload = ['dummy']
        self.UploadHTTPResult = []
        self.UploadProcessPID = []
        self.resultUploadHTTP = -1
        if not uploadtime:
            uploadtime = '000'
        if not uploadbytes:
            uploadbytes = '000'
        for noofThread in range(1, uploadstreams + 1):
            try:
                HTTPUploadThreadName = 'HTTP_Upload_' + str(noofThread)
                startHTTPUploadThreadCommand = threading.Thread(target=self.PerformHTTPUploadThread,
                                                                name=HTTPUploadThreadName,
                                                                args=[username, password, uploadurl,
                                                                      uploadfrom, uploadtime, uploadbytes])

                self.startHTTPThreadUpload.append(startHTTPUploadThreadCommand)
                self.startHTTPThreadUpload[noofThread].daemon = True
                self.startHTTPThreadUpload[noofThread].start()
            except Exception as e11:
                return False, 'Exception Seen in Metric HTTP Upload to start HTTP Thread!!!\nException: %s' % e11
        self.startedHTTPUpload = True
        for noofThread in range(1, uploadstreams + 1):
            try:
                self.startHTTPThreadUpload[noofThread].join()
            except Exception as e12:
                print 'Exception Seen in Metric HTTP Upload in completing the download!!!\nException: %s' % e12
                return False, 'Exception Seen in Metric HTTP Upload in completing the download!!!\nException: %s' % e12
        try:
            print self.UploadHTTPResult, uploadstreams
            self.resultUploadHTTP = sum(self.UploadHTTPResult) / uploadstreams
            self.completeHTTPUpload = True
            print 'Average Upload Data Rate is %s' % self.resultUploadHTTP
            return True, 'Average Upload Data Rate is %s' % self.resultUploadHTTP
        except Exception as e13:
            return False, 'Exception Seen in Metric HTTP in aggregating the Upload result!!!\nException: %s' % e13

    def PerformHTTPUploadThread(self, username, password, uploadurl, uploadfrom, uploadtime, uploadbytes):
        self.HTTP_Upload_Script_Name = 'HTTP_Upload.py'
        # get the current path
        try:
            Current_Path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.HTTP_Upload_Script_Name)
        except NameError:
            Current_Path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])) + self.HTTP_Upload_Script_Name)
        print 'HTPP Upload Script is:%s' % Current_Path

        try:
            self.abruptStopHTTPUpload = True
            # create the sub process to call http upload
            Upload_Process = subprocess.Popen(['python', str(Current_Path), str(username), str(password),
                                               str(uploadurl), str(uploadfrom), str(uploadtime), str(uploadbytes)],
                                              stdout=subprocess.PIPE)
            print 'Upload PID is %s' % Upload_Process.pid
            self.UploadProcessPID.append(Upload_Process.pid)
            (Upload_Result, Upload_Error) = Upload_Process.communicate()
            print 'Upload Result is: %s' % Upload_Result
            Upload_Result = Upload_Result.split('Uploading Done!!!')[-1]
            if not len(Upload_Result) > 1:
                print 'Upload Result is not valid'
                return False, 'Exception in Upload Sub Process'
            Upload_Result = Upload_Result.split('[')[-1].split(']')[0]
            print 'Upload Data Rate is : %s' % Upload_Result
            self.UploadHTTPResult.append(float(Upload_Result))
            try:
                Upload_Process.terminate()
            except Exception as e14:
                print 'PASS on Process Terminate as it has been taken care in base upload file %s' % e14
            self.abruptStopHTTPUpload = False
        except Exception as e15:
            self.ExceptionHTTPUpload = True
            print 'Exception in Upload Sub Process: %s' % e15
            return False, 'Exception in Upload Sub Process: %s' % e15

    def StopHTTPUpload(self):
        self.abruptStopHTTPUpload = False
        self.TriggerStopHTTPUpload = True
        for PID_Count, PID_NO in enumerate(self.UploadProcessPID):
            try:
                os.kill(self.UploadProcessPID[PID_Count], signal.SIGINT)
                print 'Killed PID %s' % self.UploadProcessPID[PID_Count]
            except Exception as e16:
                print 'Pass on OS KILL as it has been taken care in base upload file %s : %s ' % (
                    self.UploadProcessPID[PID_Count], e16)
        try:
            if self.ExceptionHTTPUpload:
                print 'Exception in HTTP Download!!!. Please Check!!!'
                self.abruptStopHTTPUpload = self.TriggerStopHTTPUpload = self.startedHTTPUpload = \
                    self.completeHTTPUpload = self.ExceptionHTTPUpload = False
                return False, 'Exception in HTTP Download[-1]!!!. Please Check!!!'
            elif not self.startedHTTPUpload:
                print 'HTTP Download Not started!!!. Please Check!!!'
                self.abruptStopHTTPUpload = self.TriggerStopHTTPUpload = self.startedHTTPUpload = \
                    self.completeHTTPUpload = self.ExceptionHTTPUpload = False
                return False, 'HTTP Download Not started[-1]!!!. Please Check!!!'
            elif not self.completeHTTPUpload:
                print 'HTTP Download Not Completed!!!. Please Check!!!'
                self.abruptStopHTTPUpload = self.TriggerStopHTTPUpload = self.startedHTTPUpload = \
                    self.completeHTTPUpload = self.ExceptionHTTPUpload = False
                return False, 'HTTP Download Not Completed[-1]!!!. Please Check!!!'
            elif self.abruptStopHTTPUpload:
                print 'HTTP Download Stopped Abruptly!!!'
                self.abruptStopHTTPUpload = self.TriggerStopHTTPUpload = self.startedHTTPUpload = \
                    self.completeHTTPUpload = self.ExceptionHTTPUpload = False
                return False, 'HTTP Download Stopped Abruptly[-1]!!!'
        except Exception as e17:
            print 'Exception is stopping HTTP Download. Error: %s' % e17
            return False, 'Exception is stopping HTTP Download. Error: %s' % e17
        self.abruptStopHTTPUpload = self.TriggerStopHTTPUpload = self.startedHTTPUpload = \
            self.completeHTTPUpload = self.ExceptionHTTPUpload = False
        if self.resultUploadHTTP == 0:
            self.resultUploadHTTP = -1
        print 'HTTP Upload completed successfully with Upload Throughput %.3f Kbps' % self.resultUploadHTTP
        return True, 'HTTP Upload completed successfully with Upload Throughput [%.3f] Kbps' \
                     '' % self.resultUploadHTTP
