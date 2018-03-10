#################################################################################################################################
# This script will create stub config files for all Eureka server (which you have specified) registered	apps                    #
#                                                                                                                               #
# Author: Chinthaka Senanayaka                                                                                                  #
# Date: 2018-Feb-09                                                                                                             #
#                                                                                                                               #
# Run command:                                                                                                                  #
# > python stub_config_creator.py <Mandatory:config file path to write> <Optional:eureka host> <Optional:eureka port>           #
# <Optional:eureka app name which you work> <Optional:app port which you work>                                                  #
# Example:                                                                                                                      #
# > python stub_config_creator.py configuration/eureka/ 11.111.111.111 8761 APP-SERVICE-1 8085                                  #
#                                                                                                                               #
# Post requisites:                                                                                                              #
# 1. ZUULSERVER port will be set to 8080 and service that you are working will be set to 8085                                   #
#################################################################################################################################

import urllib2
import sys
import xml.etree.ElementTree as ET
import socket

print "========= Starting stub config update ========="

basePath = sys.argv[1]
eurekaHost = "11.111.111.111" if len(sys.argv) < 3 else sys.argv[2]
eurekaPort = "8761" if len(sys.argv) < 4 else sys.argv[3]
localServiceName = "APP-SERVICE-1" if len(sys.argv) < 5 else sys.argv[4]
localServicePort = "8085" if len(sys.argv) < 6 else sys.argv[5]

localServiceName2 = None if len(sys.argv) < 7 else sys.argv[6]
localServicePort2 = None if len(sys.argv) < 8 else sys.argv[7]
localServiceName3 = None if len(sys.argv) < 9 else sys.argv[8]
localServicePort3 = None if len(sys.argv) < 10 else sys.argv[9]

allConfigFileName = "all-applications.xml"
deltaConfigFileName = "delta.xml"

#setupLocalServices function start
def setupLocalServices(edgeInstance):
	
	edgeInstance.find("ipAddr").text = "127.0.0.1"
	
	edgeHostName = edgeInstance.find("hostName").text
	edgeInstance.find("hostName").text = socket.gethostname()
	
	edgeHomePageUrlText = edgeInstance.find("homePageUrl").text
	edgeInstance.find("homePageUrl").text = edgeHomePageUrlText.replace(edgeHostName, socket.gethostname())
	
	edgeStatusPageUrlText = edgeInstance.find("statusPageUrl").text
	edgeInstance.find("statusPageUrl").text = edgeStatusPageUrlText.replace(edgeHostName, socket.gethostname())
	
	edgeHealthCheckUrlText = edgeInstance.find("healthCheckUrl").text
	edgeInstance.find("healthCheckUrl").text = edgeHealthCheckUrlText.replace(edgeHostName, socket.gethostname())
	
	edgeMetaData = edgeInstance.find('metadata')
	edgeMetaData.find("instanceId").text = appName.lower() + ":1234"

#setupLocalServices function end

#get all configs from Eureka by GET request
allConfigURL = "http://" + eurekaHost + ":" + eurekaPort + "/eureka/apps"
requestGETAll = urllib2.Request(allConfigURL)
try:
	getAllUrl = urllib2.urlopen(requestGETAll)
	contentsGETAll = getAllUrl.read()
except urllib2.HTTPError as e:
	print "Failure to get all config details for: " + allConfigURL + ". Code: " + str(e.code) + ", reason: " + str(e.reason)
except URLError as e:
	print "Unable to reach server to get all config details for: " + allConfigURL + ". Code: " + str(e.code) + ", reason: " + str(e.reason)
finally:
	getAllUrl.close()

#get delta config from Eureka by GET request
deltaConfigURL = allConfigURL + "/delta"
requestGETDelta = urllib2.Request(deltaConfigURL)
try:
	getDeltaUrl = urllib2.urlopen(requestGETDelta)
	contentsGETDelta = getDeltaUrl.read()
except urllib2.HTTPError as e:
	print "Failure to get delta config details for: " + deltaConfigURL + ". Code: " + str(e.code) + ", reason: " + str(e.reason)
except URLError as e:
	print "Unable to reach server to get delta config details for: " + deltaConfigURL + ". Code: " + str(e.code) + ", reason: " + str(e.reason)
finally:
	getDeltaUrl.close()

#Take individual application config
dataAll = ET.fromstring(contentsGETAll)

for app in dataAll.findall('application'):
	
	appName = app.find('name').text
	edgeInstance = app.find('instance')
	
	# Make local services configs to local: ZUULSERVER and Service that you are working on
	# ZUULSERVER port will be set to 8080 and localServiceName will be set to 8085
	if(appName == "EDGESERVER"):
		
		# Make EDGE-SERVER local
		setupLocalServices(edgeInstance)
		edgeInstance.find("port").text = "8080"
		
	elif(localServiceName != None and appName == localServiceName):
		setupLocalServices(edgeInstance)
		edgeInstance.find("port").text = localServicePort
		
	elif(localServiceName2 != None and appName == localServiceName2):
		setupLocalServices(edgeInstance)
		edgeInstance.find("port").text = localServicePort2
		
	elif(localServiceName3 != None and appName == localServiceName3):
		setupLocalServices(edgeInstance)
		edgeInstance.find("port").text = localServicePort3
	
	appData = ET.tostring(app)
	
	try:
		appConfigFile = open(basePath + appName + ".xml","w+")
		appConfigFile.write(appData)
	finally:
		appConfigFile.close()

#Write all application config and delta config
try:
	allConfigFile = open(basePath + allConfigFileName,"w+")
	allConfigFile.write(ET.tostring(dataAll))
	
	deltaConfigFile = open(basePath + deltaConfigFileName,"w+")
	deltaConfigFile.write(contentsGETDelta)
	
finally:
	allConfigFile.close()
	deltaConfigFile.close()

print "========= Finished stub config update ========="
