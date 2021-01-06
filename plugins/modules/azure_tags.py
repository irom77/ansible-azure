#!/usr/bin/python3
DOCUMENTATION = '''
---
module: azure_tags
short_description: Pull tagged IP addresses
description: Module pulls IP addresses of tagged objects on Azure
'''

EXAMPLES = '''
- name: Pull addresses from Azure
  azure_tags:
    tgs: creator:me, applicationname:cyberark
    provider: "{{azure_provider_test}}"
    register: addr
'''
from ansible.module_utils.basic import *
import requests, json, urllib3
TIMEOUT=3
def get_token(provider):
    """ Get authorization token """
    url_token="https://login.microsoftonline.com/" + provider['tenant'] + "/oauth2/token"
    payload = { 
        'grant_type': 'client_credentials',
        'client_id': provider['client_id'],
        'client_secret': provider['secret'],
        'Content-Type': 'x-www-form-urlencoded',
        'resource': 'https://management.azure.com/',
        }  
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)     
    response = requests.post(url_token, data=payload, verify=False, timeout=TIMEOUT) 
    if response.status_code == 200:
        Token = json.loads(response.content)["access_token"]
    else:
        raise Exception(json.dumps(response.json()))
    return { "Authorization": str("Bearer "+ Token), 'Content-Type': 'application/json'}    

def tag_pull(provider, tag):
    """ Pull addresses with tag from Azure  """
    tag1=tag.split(':')[0]
    tag2=tag.split(':')[1]
    Query = """Resources
            | where type =~ 'microsoft.compute/virtualmachines'
            | where tags['{tag1}'] =~ '{tag2}'
            | extend nics=array_length(properties.networkProfile.networkInterfaces) 
            | mv-expand nic=properties.networkProfile.networkInterfaces 
            | project vmId = id, vmName = name, nicId = tostring(nic.id) 
            | join kind=leftouter (
                Resources
                | where type =~ 'microsoft.network/networkinterfaces'
                | mv-expand ipconfig=properties.ipConfigurations 
                | project  nicId = id, IP = ipconfig.properties.privateIPAddress
                )
                on nicId
            | project-away vmId, nicId, nicId1, vmName
            | union (Resources
            | where type =~ 'microsoft.network/networkinterfaces'
            | where tags['applicationname'] =~ 'subscription defaults'
            | mv-expand ipconfig=properties.ipConfigurations 
            | project  nicId = id, IP = ipconfig.properties.privateIPAddress
            | project-away nicId)
            | summarize Tagged = make_list(IP)""".format(tag1=tag1,tag2=tag2)
    url_graph = "https://management.azure.com/providers/Microsoft.ResourceGraph/resources?api-version=2019-04-01"
    
    payload,headers = {
        "subscriptions": [provider['subscription_id']],
        "query": " ".join(Query.split()) 
        },{}
    try:
        headers = get_token(provider)
    except Exception as e:        
        return [], str(e)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)   
    response = requests.post(url_graph, headers=headers, data = json.dumps(payload), verify=False, timeout=TIMEOUT)
    if response.status_code == 200:
        if 'data' in response.json():
            return response.json()['data']['rows'][0][0], ""   
    return [], json.dumps(response.json())
 
def main():
    fields = {
        "tgs": {"required": True, "type": "str"},
        "provider": {"required": True, "type": "dict"}
    }    

    module = AnsibleModule(argument_spec=fields)
    tgs = module.params['tgs']
    provider = module.params['provider']

    result = {
        "tgs": tgs,
        "provider": provider
        }
    response, debug_msg = [], "tgs:"
    if tgs:
        for tag in tgs.split(','):
                # module.log("Tag: {}".format(tag))
                debug_msg= debug_msg + "{} ".format(tag.strip())
                result, error = tag_pull(provider,tag.strip()) 
                if len(result) > 0:
                    response.extend(result)   
        response = list(set(response))
        if response:
            module.exit_json(changed=True, meta=response, debug_msg=debug_msg.strip())
        else:
            module.fail_json(msg=error, meta=response)  
    else:
        module.fail_json(msg="No tags provided", meta={})     

if __name__ == '__main__':
    main()