import requests, os, json, time
from akamai.edgegrid import EdgeGridAuth, EdgeRc
from urllib.parse import urlparse, urljoin
from generate_report import *


# setup proxy
proxy = {
    'http' : '',
    'https' : '',
}
# root is absolute path to project folder
root = os.path.dirname(os.path.abspath(__file__))
# .edgerc is usually in user home, set homedir
homedir = os.path.expanduser("~")
# edgerc = EdgeRc(homedir + '/.edgerc')
# if edgerc:
#     print('Client token found at: '+ str(edgerc))
# else:
#     print('Missing API client token.')
#     exit()
# section = 'default'
#baseurl = 'https://%s' % edgerc.get(section, 'host')

# Check env for values
# If its running of pipeline than unset proxies
isPipeline = False
if os.getenv('AGENT_NAME'):
    isPipeline = True
    print(os.environ['AGENT_NAME'])

if isPipeline == True:
    # Set proxies to None
    proxy = {
        'http' : None,
        'https' : None,
    }

if os.getenv('BASE_URL') and os.getenv('CLIENT_TOKEN') and os.getenv('CLIENT_SECRET') and os.getenv('ACCESS_TOKEN'):
    baseurl = 'https://' + os.environ['BASE_URL']
    print('URL and access tokens found.')
else:
    print('Missing BASE_URL and/or CLIENT_TOKEN, and/or CLIENT_SECRET, and/or ACCESS_TOKEN. Set them in the env and try again.')
    exit()

# Path to CA certs chain
certspath = os.path.join(root, 'certs')
if isPipeline == True:
    CA_CERTS = certspath+'/CA_CHAIN.pem'
else:
    CA_CERTS = certspath+'\CA_CHAIN.pem'
print(CA_CERTS)
# Akamai API Base Endpoints (bep)
properties_ep = '/papi/v1/properties'
groups_ep = 'papi/v1/groups'
configs_ep = '/appsec/v1/configs'
# Create a session
s = requests.Session()
#s.auth = EdgeGridAuth.from_edgerc(edgerc, section)
s.auth = EdgeGridAuth(
    client_token = os.environ['CLIENT_TOKEN'],
    client_secret = os.environ['CLIENT_SECRET'],
    access_token = os.environ['ACCESS_TOKEN']
)

def GetGroups():
    json_result = ''
    try:
        response = s.get(urljoin(baseurl, groups_ep), proxies=proxy, verify=CA_CERTS)
        if response:
            json_result = response.json()
        else:
           response.raise_for_status() 
    except (ConnectionError, TimeoutError, Exception) as e:
        print(str(e))
    return json_result['groups']

def GetProperties(groupId, contractId):
    json_result = ''
    try:
        response = s.get(urljoin(baseurl, properties_ep+'?contractId='+ contractId +'&groupId='+ groupId), proxies=proxy, verify=CA_CERTS)
        if response:
            json_result = response.json()
        else:
           response.raise_for_status() 
    except (ConnectionError, TimeoutError, Exception) as e:
        print(str(e))
    return json_result['properties']

# Get property version active on PRODUCTION/STAGING
def GetLatestPropertyVersion(propertyId):
    json_result = ''
    try:
        #response = s.get(urljoin(baseurl, properties_ep+'/'+propertyId+'/versions/latest?activatedOn='+activatedOn+'&contractId='+contractId+'&groupId='+groupId), proxies=proxy,verify=CERTS_BUNDLE)
        response = s.get(urljoin(baseurl, properties_ep+'/'+propertyId+'/versions/latest'), proxies=proxy, verify=CA_CERTS) #?activatedOn='+activatedOn+'&contractId='+contractId+'&groupId='+groupId), proxies=proxy,verify=CERTS_BUNDLE)
        if response:
            json_result = response.json()
        else:
            response.raise_for_status() 
    except (ConnectionError, TimeoutError, Exception) as e:
        print(str(e))
    return json_result['versions']['items']

#def GetPropertiesHostnames(propertyId, propertyVersion, groupId, contractId, validateHostnames):
def GetPropertiesHostnames(propertyId, propertyVersion):
    json_result = ''
    try:
        #response = s.get(urljoin(baseurl, properties_ep+'/'+propertyId+'/versions/'+str(propertyVersion)+'/hostnames?contractId='+contractId+'&groupId='+groupId+'&validateHostnames='+str(validateHostnames)), proxies=proxy,verify=CERTS_BUNDLE)
        response = s.get(urljoin(baseurl, properties_ep+'/'+propertyId+'/versions/'+str(propertyVersion)+'/hostnames'), proxies=proxy,verify=CA_CERTS)
        if response:
            json_result = response.json()
        else:
            response.raise_for_status()
    except (ConnectionError, TimeoutError, Exception) as e:
        print(str(e))
    return json_result['hostnames']

def GetConfigs():
    json_result = ''
    try:
        response = s.get(urljoin(baseurl, configs_ep), proxies=proxy, verify = CA_CERTS)
        if response:
            json_result = response.json()
        else:
            response.raise_for_status() 
    except (ConnectionError, TimeoutError, Exception) as e:
        print(str(e))
    return json_result['configurations']

def ListMatchHostnames():
    matchedHostnames_arr = []
    matchedHostDetails_dict = {}
    cdnHostnames = []
    configHostnames = []
    unmatchedHostDetails_dict = {}
    propertyHostnames_dict = []
    #configs would contain all configurations with hostnames
    print('Getting list of security configurations..')
    configs = GetConfigs()
    
    #list of all groups on akami
    print('Getting list of groups..')
    groups = GetGroups() 
    print('Getting list of properties for each group..')
    #check through each group
    for group in groups['items']:
        groupId = group['groupId']
        contractIds = group['contractIds']
        
        contractId = contractIds[0]
        #properties contains all hostnames based on group and contract (including covered ones)
        properties = GetProperties(groupId, contractId)

        #for each property, find all matches from configurations
        for property in properties['items']:
            #print(property['propertyId'])
            propertyId = property['propertyId']
            #propertyVersionList = GetLatestPropertyVersion(propertyId, groupId, contractId, 'PRODUCTION') #STAGING
            propertyVersionList = GetLatestPropertyVersion(propertyId)
            #print(propertyVersionList[0]['propertyVersion'])
            #if propertyVersionList:
            propertyVersion = propertyVersionList[0]['propertyVersion']
            #propertyHostnames = GetPropertiesHostnames(propertyId, propertyVersion, groupId, contractId, true)
            propertyHostnames = GetPropertiesHostnames(propertyId, propertyVersion)
            temp = propertyHostnames['items']
            if temp: # Not empty
                #print(temp[0])
                propertyHostnames_dict.append(temp)
    time.sleep(2)
    print('List of hostnames in CDN properties..')
    for entry in propertyHostnames_dict:
        for hostname in entry:
            cdnHostnames.append(hostname['cnameFrom'])
    print(cdnHostnames)
    time.sleep(2)      
    print('List of hostnames in security configurations..')
    for entry in configs:
        if 'productionHostnames' in entry:
            for hostname in entry['productionHostnames']:
                #print(hostname)
                configHostnames.append(hostname)
    print(configHostnames)
    time.sleep(2)
    print('Comparing for matches..')
    for i in cdnHostnames:
        if i in configHostnames:   
            matchedHostnames_arr.append(i)
    time.sleep(2)
    print('Matches found: ')
    print(matchedHostnames_arr)
    time.sleep(2)
    print('Generating html report.. ')
    GenerateHTMLReport(matchedHostnames_arr, cdnHostnames)
    print('Generating json report..')
    GenerateJSONReport(matchedHostnames_arr, cdnHostnames)
    time.sleep(1)
    print('Done.')

ListMatchHostnames()
#GetProperties()####

