import init
from logger import GCPLogger
import google.oauth2.id_token
import google.auth.transport.requests
import requests

logging_client = GCPLogger(gcp_project=init.gcp_project)

local = {
    "ticket_details" : None,
    "incident_state" : None,
    "sys_id" : None,
    "servicenow_ticket" : None
}

priority_map = {
    'TROUBLE': "3",
    'DOWN': "1",
    'UP': "4",
    'CRITICAL': "2"
}

site24x7_camel_case_map = {
    "availability": "Availability",
    "pagereads": "PageReads",
    "cpuutilization": "CPUUtilization",
    "cpuusedpercent": "CPUUsedPercent",
    "memusedpercent": "MemUsedPercent",
    "memoryutilization": "MemoryUtilization",
    "usedmemory": "UsedMemory",
    "dusedpercent": "DUsedPercent",
    "pagewrites": "PageWrites",
    "pageexpectency": "PageExpectency"
}

def getIncidentDetails () :
    raw_request = init.webhook_payload
    attributeName = "NA"
    incidentReason = raw_request['INCIDENT_REASON']
    if('STATUS_CHANGE_ATTRIBUTES' in raw_request):
        if('reason' in raw_request['STATUS_CHANGE_ATTRIBUTES'][0]):
            incidentReason = raw_request['STATUS_CHANGE_ATTRIBUTES'][0]['reason']
        if('attributeName' in raw_request['STATUS_CHANGE_ATTRIBUTES'][0]):
            attributeName = raw_request['STATUS_CHANGE_ATTRIBUTES'][0]['attributeName']
    
    if attributeName.lower() in site24x7_camel_case_map :
        attributeName = site24x7_camel_case_map[attributeName.lower()]

    failedAttributes = "NA"
    if(raw_request['STATUS'] == "DOWN"):
        if('FAILED_ATTRIBUTES' in raw_request):
            failedAttributes = str(raw_request['FAILED_ATTRIBUTES'][0])

    ticket_content = f'''Customer Name - {raw_request.get('MSP_CUSTOMER_NAME','NA')}
CI Name - {raw_request.get('MONITORNAME','NA')}
CI Type - {raw_request.get('MONITORTYPE','NA')}
Status - {raw_request.get('STATUS','NA')}
Failed Attribute - {failedAttributes}
Incident Reason - {incidentReason}
Incident Time - {raw_request.get('INCIDENT_TIME','NA')}
Tool - Site24x7
'''

    # <Customer> | <Project> | <ComponentType> | <Component> | <Metric> 
    # <Customer> | <Project> | <ComponentType> | <Component> | <Metric> 
    # <Customer> | <ComponentType> | <Component> | <Metric>
    ticket_subject = raw_request.get('MSP_CUSTOMER_NAME','NA') + " | " + raw_request.get('MONITORTYPE','NA') + " | " + raw_request.get('MONITORNAME','NA') + " | " + attributeName
    
    local["ticket_details"] = {
        "ticket_subject": ticket_subject,
        "ticket_content": ticket_content,
        "servicenow_attribs": {
            "short_description": ticket_subject,
            "priority": priority_map[raw_request.get('STATUS','TROUBLE')],
            "caller_id": "Site24x7",
            "cmdb_ci": raw_request.get('MONITORNAME','NA'),
            "description": ticket_content,
            "assignment_group": 'Cloud Support',
            "contact_type": 'alert',
            "u_monitoring_tool": 'Site24x7'
            # "u_account_name": self.raw_request['MSP_CUSTOMER_NAME'],
        },
        "ticket_type": "INCIDENT"
    }

    temp_dict = {
        "tool": "site24x7",
        "source": "cloud function | incident-processing-function",
        "message": f"incident received | {ticket_subject}",
        "ticket_details": raw_request
    }
    logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="INFO")
    return 0

def getIncidentState () :
    raw_request = init.webhook_payload
    auth_req = google.auth.transport.requests.Request()
    url = init.servicenow_client_url
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, url)
    headers = {
        "Authorization": f"Bearer {id_token}", 
        "Content-Type": "application/json"
    }
    request_body = {
        "api_path": "api/now/table/incident",
        "request_headers": {
            "Content-Type": "application/json", "Accept": "application/json"
        },
        "query_parameters": {
            "sysparm_query": f'active=true^stateNOT IN6,7,8^short_description={local["ticket_details"]["ticket_subject"]}',
            "sysparm_limit": "1"
        },
        "request_body": {},
        "ticket_type": "INCIDENT",
        "method": "QUERY"
    }

    response = requests.post(url=url, headers=headers, json=request_body)
    if response.status_code == 200 :
        if "result" in response.json() :
            if response.json()["result"] is not None :
                if len(response.json()["result"]) != 0 :
                    local["servicenow_ticket"] = response.json()["result"][0]
                    local["incident_state"] = 1
                    local["sys_id"] = response.json()["result"][0]["sys_id"]
                    return 0
        local["incident_state"] = 0
        return 0
    else :
        temp_dict = {
            "tool": "site24x7",
            "message": "failed to get incident state",
            "source": "cloud function | incident-processing-function",
            "response_code": response.status_code,
            "response_headers": dict(response.headers),
            "response_body": response.text,
            "ticket_details": raw_request
        }
        logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
        return 1

def actOnIncident () :
    raw_request = init.webhook_payload
    if local["incident_state"] == 0 :
        auth_req = google.auth.transport.requests.Request()
        url = init.servicenow_client_url
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, url)
        headers = {
            "Authorization": "Bearer {}".format(id_token), 
            "Content-Type": "application/json"
        }
        path_params = {
            "tableName": "incident"
        }
        api_path = "api/now/table/{tableName}".format(**path_params)
        request_body = {
            "api_path": api_path,
            "request_headers": {
                "Content-Type": "application/json", "Accept": "application/json"
            },
            "query_parameters": None,
            "request_body": local["ticket_details"]["servicenow_attribs"],
            "ticket_type": "INCIDENT",
            "method": "POST"
        }
        response = requests.post(url=url, headers=headers, json=request_body)
        if response.status_code == 200 :
            temp_dict = {
                "tool": "site24x7",
                "source": "cloud function | incident-processing-function",
                "message": f"incident posted | {local['ticket_details']['servicenow_attribs']['short_description']}",
                "ticket_details": raw_request
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="INFO")
            return 0
        else :
            temp_dict = {
                "tool": "site24x7",
                "message": "failed to post incident",
                "source": "cloud function | incident-processing-function",
                "response_code": response.status_code,
                "response_headers": dict(response.headers),
                "response_body": response.text,
                "ticket_details": raw_request
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            return 1
        
    if local['incident_state'] == 1 :
        auth_req = google.auth.transport.requests.Request()
        url = init.servicenow_client_url
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, url)
        headers = {
            "Authorization": "Bearer {}".format(id_token), 
            "Content-Type": "application/json"
        }
        path_params = {
            "tableName": "incident",
            "sys_id": local['sys_id']
        }
        api_path = "api/now/table/{tableName}/{sys_id}".format(**path_params)
        # temp_dict = self.ticket_details["servicenow_attribs"]
        temp_dict = {}
        temp_dict["work_notes"] = local['ticket_details']["ticket_content"]
        # temp_dict.pop('priority', None)
        request_body = {
            "api_path": api_path,
            "request_headers": {
                "Content-Type": "application/json", "Accept": "application/json"
            },
            "query_parameters": None,
            "request_body": temp_dict,
            "ticket_type": "INCIDENT",
            "method": "PUT"
        }
        response = requests.post(url=url, headers=headers, json=request_body)
        if response.status_code == 200 :
            temp_dict = {
                "tool": "site24x7",
                "source": "cloud function | incident-processing-function",
                "message": f"incident updated | {local['ticket_details']['servicenow_attribs']['short_description']}",
                "ticket_details": raw_request
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="INFO")
            return 0
        else :
            temp_dict = {
                "tool": "site24x7",
                "message": "failed to update incident",
                "source": "cloud function | incident-processing-function",
                "response_code": response.status_code,
                "response_headers": dict(response.headers),
                "response_body": response.text,
                "ticket_details": raw_request
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            return 1