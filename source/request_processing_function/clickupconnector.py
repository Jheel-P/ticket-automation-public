import init
from logger import GCPLogger
import google.oauth2.id_token
import google.auth.transport.requests
import requests

logging_client = GCPLogger(gcp_project=init.gcp_project)

class ClickUp :
    
    def __init__ (self) :
        self.raw_request = None
        self.ticket_details = None
        self.request_state = None
        self.sys_id = None
        self.servicenow_ticket = None
        self.tool = "clickup"
        self.access_token = None
        self.ticket_state = 0

    def addAccessToken (self, access_token) :
        self.access_token = access_token

    def addRequest (self, request) :
        self.raw_request = request

    def __getParentInfo (self, parent_id) :
        url = f"https://api.clickup.com/api/v2/task/{parent_id}/"
        headers = {
            "Authorization": self.access_token
        }
        response = requests.get(url, headers=headers)
        return response

    def getRequestDetails (self) :
        if "source" in self.raw_request :
            if self.raw_request["source"] == "servicenow" :
                temp_dict = {
                    "direction": "reverse",
                    "task_id": self.raw_request["task_id"]
                }
                self.ticket_details = temp_dict
                return self.ticket_details
        else :
            task_info_reponse = self.__getParentInfo (parent_id=self.raw_request["parent"])
            if task_info_reponse.status_code == 200 :
                temp_dict = {
                    "subtask": {
                        "id": self.raw_request['id'],
                        "name": self.raw_request['name']
                    },
                    "parent_task": {
                        "id": self.raw_request["parent"],
                        "name": task_info_reponse.json()["name"] 
                    },
                    "project": {
                        "name": self.raw_request['project']['name'],
                        "id": self.raw_request['project']['id']
                    },
                    "list": {
                        "name": self.raw_request["list"]["name"],
                        "id": self.raw_request["list"]["id"]
                    }
                }

                # Account Name | Task Name
                ticket_subject = temp_dict['parent_task']['name'] + " | " + temp_dict['subtask']['name']
                
                self.ticket_details = {
                    "ticket_subject": ticket_subject,
                    "servicenow_attribs": {
                        "short_description": ticket_subject,
                        "u_clickup_task": temp_dict['subtask']['id'],
                        # "account": "Reddoorz",
                        "priority": "4",
                        # "catagory": "GCP",
                        "assignment_group": "Cloud Support",
                        "description": ticket_subject
                    },
                    "ticket_type": "REQUEST"
                }
            else :
                temp_dict = {
                    "function": "TICKET_PROCESSING",
                    "type": "REQUEST",
                    "method": "ClickUp.getRequestDetails",
                    "tool": "ClickUp",
                    "message": "TICKET_PROCESSING | REQUEST | FAILED TO GET TASK ID",
                    "response_code": task_info_reponse.status_code,
                    "response_headers": task_info_reponse.headers,
                    "response_body": task_info_reponse.text,
                    "ticket_details": self.raw_request
                }
                logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
                return 1

            return self.ticket_details
        
    def getRequestState (self) :

        # path_params = {
        #     "tableName": "incident"
        # }
        # request_body = {
        #     "api_path": "api/now/table/{tableName}".format(*path_params),
        #     "request_headers": {
        #         "Content-Type": "application/json", "Accept": "application/json"
        #     },
        #     "query_params": {
        #         "sysparm_query": f'active=true^stateNOT IN6,7,8^short_description={self.ticket_details["ticket_subject"]}',
        #         "sysparm_limit": "1"
        #     }
        # }
        if "source" in self.raw_request :
            if self.raw_request["source"] == "servicenow" :
                return 0

        auth_req = google.auth.transport.requests.Request()
        url = init.servicenow_client_url
        id_token = google.oauth2.id_token.fetch_id_token(auth_req, url)
        headers = {
            "Authorization": f"Bearer {id_token}", 
            "Content-Type": "application/json"
        }
        
        request_body = {
            "api_path": "api/now/table/sn_customerservice_case",
            "request_headers": {
                "Content-Type": "application/json", "Accept": "application/json"
            },
            "query_parameters": {
                "sysparm_query": f'active=true^stateNOT IN6,3,7^short_description={self.ticket_details["ticket_subject"]}',
                "sysparm_limit": "1"
            },
            "request_body": {},
            "ticket_type": "REQUEST",
            "method": "QUERY"
        }
    
        response = requests.post(url=url, headers=headers, json=request_body)
        if response.status_code == 200 :
            if "result" in response.json() :
                if response.json()["result"] is not None :
                    if len(response.json()["result"]) != 0 :
                        self.servicenow_ticket = response.json()["result"][0]
                        self.ticket_state = 1
                        self.sys_id = response.json()["result"][0]["sys_id"]
                        return 0
            self.ticket_state = 0
            return 0
        else :
            temp_dict = {
                "function": "TICKET_PROCESSING",
                "type": "INCIDENT",
                "method": "Stackdriver.getIncidentState",
                "tool": "Stackdriver",
                "message": "TICKET_PROCESSING | INCIDENT | FAILED TO GET INCIDENT STATE",
                "response_code": response.status_code,
                "response_headers": dict(response.headers),
                "response_body": response.text,
                "ticket_details": self.raw_request
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            return 1

    def actOnRequest (self) :

        if "direction" in self.ticket_details :
            url = f"https://api.clickup.com/api/v2/task/{self.ticket_details['task_id']}/"
            headers = {
                "Authorization": self.access_token
            }
            request_body = {
                "status": "complete"
            }
            response = requests.put(url, headers=headers, json=request_body)
            temp_dict = {
                "function": "TICKET_PROCESSING",
                "type": "REQUEST",
                "method": "Clickup.actOnRequest",
                "tool": "Clickup",
                "message": f"TICKET_PROCESSING | REQUEST | REQUEST POSTED | REVERSE | {self.raw_request['task_id']}",
                "ticket_details": self.raw_request
            }
            logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="INFO")
            return response.json()

        if self.ticket_state == 0 :
            auth_req = google.auth.transport.requests.Request()
            url = init.servicenow_client_url
            id_token = google.oauth2.id_token.fetch_id_token(auth_req, url)
            headers = {
                "Authorization": "Bearer {}".format(id_token), 
                "Content-Type": "application/json"
            }
            path_params = {
                "tableName": "sn_customerservice_case"
            }
            api_path = "api/now/table/{tableName}".format(**path_params)
            request_body = {
                "api_path": api_path,
                "request_headers": {
                    "Content-Type": "application/json", "Accept": "application/json"
                },
                "query_parameters": None,
                "request_body": self.ticket_details["servicenow_attribs"],
                "ticket_type": "REQUEST",
                "method": "POST"
            }
            response = requests.post(url=url, headers=headers, json=request_body)
            if response.status_code == 200 :
                temp_dict = {
                    "function": "TICKET_PROCESSING",
                    "type": "REQUEST",
                    "method": "Clickup.actOnRequest",
                    "tool": "Clickup",
                    "message": f"TICKET_PROCESSING | REQUEST | REQUEST POSTED | {self.ticket_details['servicenow_attribs']['short_description']}",
                    "ticket_details": self.raw_request
                }
                logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="INFO")
                return 0
            else :
                temp_dict = {
                    "function": "TICKET_PROCESSING",
                    "type": "REQUEST",
                    "method": "ClickUp.actOnRequest",
                    "tool": "ClickUp",
                    "message": "TICKET_PROCESSING | REQUEST | FAILED TO POST REQUEST",
                    "response_code": response.status_code,
                    "response_headers": response.headers,
                    "response_body": response.text,
                    "ticket_details": self.raw_request
                }
                logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
                return 1
        
        if self.ticket_state == 1 :
            return "TICKET ALREADY EXISTS"
            # auth_req = google.auth.transport.requests.Request()
            # url = init.servicenow_client_url
            # id_token = google.oauth2.id_token.fetch_id_token(auth_req, url)
            # headers = {
            #     "Authorization": "Bearer {}".format(id_token), 
            #     "Content-Type": "application/json"
            # }
            # path_params = {
            #     "tableName": "sn_customerservice_case"
            # }
            # api_path = "api/now/table/{tableName}".format(**path_params)
            # request_body = {
            #     "api_path": api_path,
            #     "request_headers": {
            #         "Content-Type": "application/json", "Accept": "application/json"
            #     },
            #     "query_parameters": None,
            #     "request_body": self.ticket_details["servicenow_attribs"],
            #     "ticket_type": "REQUEST",
            #     "method": "POST"
            # }
            # response = requests.post(url=url, headers=headers, json=request_body)
            # if response.status_code == 200 :
            #     temp_dict = {
            #         "function": "TICKET_PROCESSING",
            #         "type": "REQUEST",
            #         "method": "Site24x7.actOnRequest",
            #         "tool": "Site24x7",
            #         "message": f"TICKET_PROCESSING | REQUEST | REQUEST POSTED | {self.ticket_details['servicenow_attribs']['short_description']}",
            #         "ticket_details": self.raw_request
            #     }
            #     logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="INFO")
            #     return 0
            # else :
            #     temp_dict = {
            #         "function": "TICKET_PROCESSING",
            #         "type": "REQUEST",
            #         "method": "ClickUp.actOnRequest",
            #         "tool": "ClickUp",
            #         "message": "TICKET_PROCESSING | REQUEST | FAILED TO POST REQUEST",
            #         "response_code": response.status_code,
            #         "response_headers": response.headers,
            #         "response_body": response.text,
            #         "ticket_details": self.raw_request
            #     }
            #     logging_client.write_entry(logger_name=init.log_name, log_struct=temp_dict, severity="ERROR")
            #     return 1