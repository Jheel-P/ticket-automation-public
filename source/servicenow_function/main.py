from logger import GCPLogger
import traceback
import init
import servicenow

logging_client = GCPLogger(gcp_project=init.gcp_project)

def ENTRY (request) :
    request_json = request.get_json()
    ticket_type = request_json["ticket_type"]

    temp_dict = {
        "message": "servicenow-client | " + request_json["ticket_type"] + " | " + request_json["method"] + " | " + request_json["api_path"],
        "function": "servicenow-client",
        "incident_details": request_json
    }
    logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="INFO")

    if ticket_type == "INCIDENT" or ticket_type == "REQUEST":
        
        request = {
            "url" : f"{init.instance_uri}/{request_json.get('api_path')}",
            "request_headers" : request_json.get("request_headers"),
            "query_parameters" : request_json.get("query_parameters"),
            "request_body" : request_json.get("request_body")
        }

        method_response = {"message": "METHOD_NOT_FOUND"}

        if request_json["method"] == "POST" :
            method_response = servicenow.postTicket(request).json()
        
        if request_json["method"] == "PUT" :
            method_response = servicenow.updateTicket(request).json()

        if request_json["method"] == "QUERY" :
            method_response = servicenow.queryTable(request).json()

        if request_json["method"] == "GET" :
            method_response = servicenow.getTicket(request).json()
         
        if method_response == 1 :
            return "INTERNAL_SERVER_ERROR"

        if method_response.get("message") == "METHOD_NOT_FOUND" :
            return method_response, 404, {'Content-Type': 'application/json'}

        response = method_response
        response["message"] = "SUCCESS"
        return response, 200, {'Content-Type': 'application/json'}
        
    response = {"message": "INVALID_REQUEST_TYPE"}
    return response, 404, {'Content-Type': 'application/json'}


def MAIN (request) :
    
    try :
        response = ENTRY(request)
    except Exception as e :
        temp_dict = {
            "message": "SERVICENOW CLIENT | PROGRAM CRASHED",
            "request": request.get_json(),
            "traceback": traceback.format_exc()
        }
        logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
        return "PROGRAM CRASHED"
    
    return response