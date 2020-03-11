# backupstat agent prototype for Veritias Backup Exec Function: sends 
# data from Veritas log files to backupstat server in JSON format Log 
# directory, backup server ID and URL for backupstat server are 
# retrieved from config file
from bs4 import BeautifulSoup import os.path, time from os import walk 
import datetime, json, requests import re import configparser config = 
configparser.ConfigParser() config.read('veritas_agent.ini') 
LOG_DIRECTORY = config["CONFIGURATION"]["log_directory"] BACKUPSERVER_ID 
= int(config["CONFIGURATION"]["backupserver"]) BACKUPSTAT_URL = 
config["CONFIGURATION"]["server_url"] START_DATE = 
datetime.datetime.now() - 
datetime.timedelta(days=int(config["CONFIGURATION"]["capture_period"])) 
END_DATE = datetime.datetime.now()
#retrieves the modified time from the file, which acts as the creation 
#time
def getModifiedTime(filename): timestamp = os.path.getmtime(filename) 
    return datetime.datetime.fromtimestamp(timestamp)
#returns an array with the list of files in the directory passed
def getFiles(directory): files = [] for (dirpath, dirnames, filenames) 
    in walk(directory):
        for f in filenames: files.append(directory+"\\"+f) break return 
    files
#takes a list of files and filters them based on the extension passed
def filterFiles(fileList, extension): filterList = [] for f in fileList: 
        ext = os.path.splitext(f)[1] if ext == extension:
            filterList.append(f) return filterList class Job: def 
    __init__ (self, filename):
        self.filename = filename
    
    #uses bs4 to read XML
    def readXML(self): file = open (self.filename, "r").read() try: soup 
            = BeautifulSoup(file.encode().decode('utf-16'), "lxml") 
            return soup
        except UnicodeDecodeError: return False
            
    def getName(self, soup):
        # use regex to get job name and job type
        job_name = soup.find("name") if job_name: job_name = 
            re.search(r"\b(?<=Job name: ).*\b", job_name.text).group(0) 
            return job_name
        return False
    
    def getType(self, job_name): job_type = re.search(r"\b(\w+$)\b", 
        job_name).group(0) return job_type
    def getServer(self, job_name): job_server = 
        re.search(r"\b(^([^\s]+))\b", job_name).group(0) return 
        job_server
    
    def getResult(self, soup):
        #use regex to get job status/result
        job_result = soup.find("engine_completion_status") if 
        job_result:
            job_result = re.search(r"\b(\w+$)\b", 
            job_result.text.strip()).group(0) return job_result
        return False
    
    def getTime(self, soup):
        #use regex and datetime to get start time
        job_time = soup.find("header") if job_time:
        #time is in the format Month Day, Year hh:mm:ss AM/PM first the 
        #date is captured from the XML
            job_time = job_time.find("start_time").text
        #then we filter it out so we can capture the important data
            date = re.search(r"\b(\w+\s\d+\W\s\d+)\b", 
            job_time).group(0) time = 
            re.search(r"\b(\d+:\d+:\d+\s\w+)\b", job_time).group(0) 
            date_string = date + " " + time
        #now it is formatted to create a datetime object
            dt = datetime.datetime.strptime(date_string, "%B %d, %Y 
            %I:%M:%S %p")
        #and finally we make a timestamp in the format month/day/year 
        #H:M:S and I'll use this as the start_time
            timestamp = dt.strftime("%m/%d/%Y %H:%M:%S") return 
            timestamp
        return False
    
    #get the failure reason
    def getReason(self, soup, job_result): if "FAIL" in 
        job_result.upper():
            try: reason_code = soup.find("errordescription").text except 
            AttributeError:
                return ""
            #the error description is usually after a hyphen
            reason_code = re.search(r"\b(?<=- ).*\b", 
            reason_code).group(0) return reason_code
        return ""
            
        
    #concatenates data and returns a dict
    def jobData(self): soup = self.readXML() if soup: job_name = 
            self.getName(soup) if job_name:
                job_type = self.getType(job_name) job_server = 
                self.getServer(job_name)
            job_result = self.getResult(soup) if job_result: 
                job_failureCode = self.getReason(soup, job_result)
            job_time = self.getTime(soup)
            #return a dict with all these values
            if job_name and job_result and job_time: return {"name": 
                job_name, "type": job_type, "status": job_result 
                ,"start_time": job_time, "comment": job_failureCode, 
                "server": job_server}
            else: return False return False
    
#fetches backup job data from log files in directory within period 
#specified
def backupJobs(startDate, endDate, directory): files = 
    filterFiles(getFiles(directory), ".xml") log_files = [] jobs = [] 
    for f in files:
        if endDate >= getModifiedTime(f) >= startDate: 
            log_files.append(f)
    for log in log_files: job = Job(log) job_info = job.jobData() if 
        job_info:
            jobs.append(job_info) return json.dumps(jobs)
#create JSON string and POST to backupstat server
def backupstatPOST(): data = """ { "backupID": %s, "jobs": %s
}
""" % (BACKUPSERVER_ID, backupJobs(START_DATE, END_DATE, LOG_DIRECTORY)) 
    r = requests.post(BACKUPSTAT_URL, json=json.loads(data)) print 
    (data)
    
backupstatPOST()
