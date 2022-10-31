import requests
import json
import time
import os
import sys

class Unbuffered(object):
   def __init__(self, stream):
       self.stream = stream
   def write(self, data):
       self.stream.write(data)
       self.stream.flush()
   def writelines(self, datas):
       self.stream.writelines(datas)
       self.stream.flush()
   def __getattr__(self, attr):
       return getattr(self.stream, attr)

sys.stdout = Unbuffered(sys.stdout)

session = requests.Session()
username = os.environ.get("cop_username")
token = os.environ.get("cop_token")
AUTO_FILE_LOCATION = os.environ.get("AUTO_FILE_LOCATION")
AUTO_FILE_SHA512_SUM = os.environ.get("AUTO_FILE_SHA512_SUM")
NOTIFICATION_URL = os.environ.get("NOTIFICATION_URL")
PRIORITY = os.environ.get("PRIORITY")


URL = "https://engci-private-rcdn.com/jenkins/sc-jenkins1/job/HCS-Cloud-Services/job/UcmgmtAutoFileUpload/buildWithParameters?AUTO_FILE_LOCATION="+AUTO_FILE_LOCATION+"&AUTO_FILE_SHA512_SUM="+AUTO_FILE_SHA512_SUM+"&NOTIFICATION_URL="+NOTIFICATION_URL+"&PRIORITY="+PRIORITY
print("----------------")

session.auth = (username, token)
response = session.post(URL)

# print(response)
location = response.headers["location"]
print("Remote Job Queue number and Url: ")
print(location)
print("----------------")
joburl=""
for i in range(0,100):
    print("Waiting for job to be scheduled...")
    response2 = session.get(location+"api/json/")
    # print(response2)
    response2_json = response2.json()
    # print(response2_json)
    if "executable" in response2_json:
        executable=response2_json["executable"]
        joburl=executable["url"]
        # print(joburl)
        print("----------------")
        break
    time.sleep(2)
if joburl=="":
    print("Timeout occured. Exiting...")
    exit(1)
print("Remote Job Build number and Url: ")
print(joburl)
print("----------------")
# joburl="https://engci-private-rcdn.com/jenkins/sc-jenkins1/job/HCS-Cloud-Services/job/UcmgmtAutoFileUpload/533/"   
timeout_flag=1
Result=""
for i in range(0,100):
    response3 = session.get(joburl+"api/json/")
    try:
    	response3_json = response3.json()
    except:
        print("Problem extracting json with response {}. Continuing...".format(response3))
        time.sleep(2)
        continue
    # print(response3_json)
    Job_Result=response3_json["result"]
    print("Waiting for job to complete ...")
    if Job_Result == "FAILURE":
        print("----------------")
        print(Job_Result)
        print("Remote Job failed. Exiting...")
        exit(1)
    elif Job_Result=="SUCCESS":
        timeout_flag=0
        print("----------------")
        print(Job_Result)
        print("Remote Job Successful.")
        break
    time.sleep(2)
if timeout_flag==1:
    print("Timeout occured. Exiting...")
    exit(1) 
