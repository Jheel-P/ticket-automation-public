import init
import traceback
from logger import GCPLogger


logging_client = GCPLogger(gcp_project=init.gcp_project)


def ENTRY (request):
    execution_status = "INVALID REQUEST SOURCE"

    if "request_source" in request.args :
        request_source = request.args["request_source"]
    else :
        request_source = "clickup"
    
    if request_source == "clickup" :
        
        execution_status = "SUCCESS"
        from clickupconnector import ClickUp
        clickup_client = ClickUp()
        clickup_client.addAccessToken(access_token=init.clickup_api_key)
        
        # fetch json body in request
        try :
            request_json = request.get_json()
        except Exception as e :
            temp_dict = {
                "function": "TICKET_PROCESSING",
                "type": "REQUEST",
                "method": "MAIN",
                "tool": "ClickUp",
                "message": "TICKET_PROCESSING | REQUEST | MAIN | ClickUp | FAILED TO GET JSON BODY IN REQUEST",
                "traceback": traceback.format_exc()
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            execution_status = temp_dict["message"]
            return execution_status

        try :
            clickup_client.addRequest(request=request_json['payload'])
        except Exception as e :
            temp_dict = {
                "function": "TICKET_PROCESSING",
                "type": "REQUEST",
                "method": "MAIN",
                "tool": "ClickUp",
                "message": "TICKET_PROCESSING | REQUEST | MAIN | ClickUp | FAILED TO REGISTER REQUEST",
                "traceback": traceback.format_exc()
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            execution_status = temp_dict["message"]
            return execution_status

        try :
            clickup_client.getRequestDetails()
        except Exception as e :
            temp_dict = {
                "function": "TICKET_PROCESSING",
                "type": "REQUEST",
                "method": "MAIN",
                "tool": "ClickUp",
                "message": "TICKET_PROCESSING | REQUEST | MAIN | ClickUp | FAILED TO GET REQUEST DETAILS",
                "traceback": traceback.format_exc()
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            execution_status = temp_dict["message"]
            return execution_status

        try :
            clickup_client.getRequestState()
        except Exception as e :
            temp_dict = {
                "function": "TICKET_PROCESSING",
                "type": "REQUEST",
                "method": "MAIN",
                "tool": "ClickUp",
                "message": "TICKET_PROCESSING | REQUEST | MAIN | ClickUp | FAILED TO GET REQUEST STATE",
                "traceback": traceback.format_exc()
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            execution_status = temp_dict["message"]
            return execution_status

        try :
            clickup_client.actOnRequest()
        except Exception as e :
            temp_dict = {
                "function": "TICKET_PROCESSING",
                "type": "REQUEST",
                "method": "MAIN",
                "tool": "ClickUp",
                "message": "TICKET_PROCESSING | REQUEST | MAIN | ClickUp | FAILED TO ACT ON REQUEST",
                "traceback": traceback.format_exc()
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            execution_status = temp_dict["message"]
            return execution_status
    
    return execution_status

def MAIN (request) :
    try :
        response = ENTRY(request)
    except Exception as e :
        temp_dict = {
            "message": "REQUEST PROCESSING | PROGRAM CRASHED",
            "request": request.get_json(),
            "traceback": traceback.format_exc()
        }
        logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
        return "PROGRAM CRASHED"
    
    return response