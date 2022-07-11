import requests
import traceback
from logger import GCPLogger
import init

logging_client = GCPLogger(gcp_project=init.gcp_project)

def refreshOAuthToken () :
    url = init.instance_uri + '/oauth_token.do'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    request_body = {
        'grant_type': 'refresh_token',
        'redirect_uri': init.instance_uri + '/login.do',
        'client_id': init.client_id,
        'client_secret': init.client_secret,
        'refresh_token': init.refresh_token
    }
    response = requests.post(url, headers=headers, data=request_body)
    if response.status_code == 200 :
        try :
            if "access_token" in response.json() :
                return response.json()["access_token"]
            else :
                temp_dict = {
                    "class": "ServiceNowCore",
                    "method": "refreshOAuthToken",
                    "message": "ACCESS_TOKEN_NOT_PRESENT_IN_RESPONSE",
                    "reponse": response.json(),
                    "headers": dict(response.headers),
                    "response_code": response.status_code
                }
                logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
                return None
        except Exception as e :
            temp_dict = {
                "class": "ServiceNowCore",
                "method": "refreshOAuthToken",
                "message": "PROGRAM_ERROR",
                "message": traceback.format_exc()
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            return None
    else :
        temp_dict = {
            "class": "ServiceNowCore",
            "method": "refreshOAuthToken",
            "message": "RECIEVED_NON_200_RESPONSE",
            "response": response.json(),
            "headers": dict(response.headers),
            "response_code": response.status_code
        }
        logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
        return None 

def postTicket (request) :
    temp_headers = request.get("request_headers")
    temp_headers.update({
        "Authorization": "Bearer " + refreshOAuthToken()
    })
    response = requests.post(request.get("url"), headers=temp_headers, json=request.get("request_body"), params=request.get("query_parameters"))
    if response.status_code == 201 :
        return response
    else :
        temp_dict = {
            "class": "ServiceNow",
            "method": "postTicket",
            "message": "RECIEVED_NON_201_RESPONSE",
            "response": response.json(),
            "headers": dict(response.headers),
            "response_code": response.status_code
        }
        logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
        return 1

def updateTicket (request) :
    temp_headers = request.get("request_headers")
    temp_headers.update({
        "Authorization": "Bearer " + refreshOAuthToken()
    })
    response = requests.put(request.get("url"), headers=temp_headers, json=request.get("request_body"), params=request.get("query_parameters"))
    if response.status_code == 200 :
        return response
    else :
        temp_dict = {
            "class": "ServiceNow",
            "method": "updateTicket",
            "message": "RECIEVED_NON_200_RESPONSE",
            "response": response.json(),
            "headers": dict(response.headers),
            "response_code": response.status_code
        }
        logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
        return 1

def getTicket (request) :
    temp_headers = request.get("request_headers")
    temp_headers.update({
        "Authorization": "Bearer " + refreshOAuthToken()
    })
    response = requests.get(request.get("url"), headers=temp_headers, params=request.get("query_parameters"))
    if response.status_code == 200 :
        return response
    else :
        temp_dict = {
            "class": "ServiceNow",
            "method": "getTicket",
            "message": "RECIEVED_NON_200_RESPONSE",
            "response": response.json(),
            "headers": dict(response.headers),
            "response_code": response.status_code
        }
        logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
        return 1

def queryTable (request) :
    temp_headers = request.get("request_headers")
    temp_headers.update({
        "Authorization": "Bearer " + refreshOAuthToken()
    })
    response = requests.get(request.get("url"), headers=temp_headers, params=request.get("query_parameters"))
    if response.status_code == 200 :
        return response
    else :
        temp_dict = {
            "class": "ServiceNow",
            "method": "queryTable",
            "message": "RECIEVED_NON_200_RESPONSE",
            "response": response.json(),
            "headers": dict(response.headers),
            "response_code": response.status_code
        }
        logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
        return 1