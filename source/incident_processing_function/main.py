import init
import traceback
from logger import GCPLogger

logging_client = GCPLogger(gcp_project=init.gcp_project)

def ENTRY (request) :
    
    execution_status = "INVALID MONITORING TOOL"
    if "monitoring_tool" in request.args :
        monitoring_tool = request.args["monitoring_tool"]
    else :
        monitoring_tool = 'null'

    if monitoring_tool == "pmm" :
        import pmm
        execution_status = "SUCCESS"
        try :
            request_json = request.get_json()
            init.webhook_payload = request_json
            pmm.getIncidentDetails()
            pmm.getIncidentState()
            pmm.actOnIncident()
        except :
            temp_dict = {
                "tool": "pmm",
                "source": "cloud function | incident-processing-function",
                "message": "failed to process incident",
                "ticket_payload": request_json,
                "traceback": traceback.format_exc()
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            execution_status = temp_dict["message"]
            return execution_status
        
        return execution_status
        
    ###################################################################################

    if monitoring_tool == "stackdriver" :
        import google_cloud_monitoring
        execution_status = "SUCCESS"
        try :
            request_json = request.get_json()
            init.webhook_payload = request_json['incident']
            google_cloud_monitoring.getIncidentDetails()
            google_cloud_monitoring.getIncidentState()
            google_cloud_monitoring.actOnIncident()
        except :
            temp_dict = {
                "tool": "stackdriver",
                "source": "cloud function | incident-processing-function",
                "message": "failed to process incident",
                "ticket_payload": request_json,
                "traceback": traceback.format_exc()
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            execution_status = temp_dict["message"]
            return execution_status
        return execution_status
    
    #########################################################################
    
    if monitoring_tool == "site24x7" :
        import site24x7
        execution_status = "SUCCESS"
        try :
            request_json = request.get_json()
            site24x7.getIncidentDetails()
            site24x7.getIncidentState()
            site24x7.actOnIncident()
        except :
            temp_dict = {
                "tool": "site24x7",
                "message": "failed to process incident",
                "source": "cloud function | incident-processing-function",
                "ticket_payload": request_json,
                "traceback": traceback.format_exc()
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            execution_status = temp_dict["message"]
            return execution_status
        return execution_status
        
    temp_dict = {
        "message": "invalid monitoring tool",
        "source": "cloud function | incident-processing-function",
        "request_headers": dict(request.headers),
        "request_arguments": request.args,
        "request_body": request.get_json()
    }
    logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
    return execution_status


def MAIN (request) :
    try :
        response = ENTRY(request)
    except :
        temp_dict = {
            "message": "program crashed",
            "source": "cloud function | incident-processing-function",
            "request": request.get_json(),
            "traceback": traceback.format_exc()
        }
        logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
        return "INTERNAL SERVER ERROR"
    
    return response