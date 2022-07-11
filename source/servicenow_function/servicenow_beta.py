import requests
from pprint import pprint
from requests import api
from requests.models import Response
from logger import GCPLogger
import os

logging_client = GCPLogger(gcp_project=os.environ["gcp_project"])

class ServiceNowCore :
    
    def __init__ (self) :
        self.__access_token = None
        self.__oauth_header = None
        self.instance_uri = None
    
    def addInstanceURI (self, instance_uri) :
        self.instance_uri = instance_uri

    def addOAuthToken (self, access_token) :
        self.__access_token = access_token
        self.__oauth_header = {
            "Authorization": "Bearer " + self.__access_token
        }

class ServiceNowIncident (ServiceNowCore) :
    
    def __init__(self) :
        super().__init__()
        self.headers = None
        self.api_path = None
        self.url = None
        self.response = None
        self.query_parameters = None
        self.request_body = None

    def addAPIPath (self, api_path) :
        self.url = self.instance_uri + "/" + api_path
    
    def addHeaders (self, headers) :
        self.headers = headers

    def addQueryParameters (self, query_parameters) :
        self.query_parameters = query_parameters

    def addRequestBody (self, request_body) :
        self.request_body = request_body

    def postTicket (self) :
        temp_headers = dict(self.headers)
        temp_headers.update(self._ServiceNowCore__oauth_header)
        self.response = requests.post(self.url, headers=temp_headers, json=self.request_body, params=self.query_parameters)
        if self.response.status_code == 201 :
            return 0
        else :
            temp_dict = {
                "class": "ServiceNow",
                "method": "postTicket",
                "message": "RECIEVED_NON_201_RESPONSE",
                "response": self.response.json(),
                "headers": dict(self.response.headers),
                "response_code": self.response.status_code
            }
            logging_client.write_entry(logger_name=os.environ["log_name"], log_struct=temp_dict, severity="ERROR")
            return temp_dict

    def updateTicket (self) :
        temp_headers = dict(self.headers)
        temp_headers.update(self._ServiceNowCore__oauth_header)
        self.response = requests.put(self.url, headers=temp_headers, json=self.request_body, params=self.query_parameters)
        if self.response.status_code == 200 :
            return 0
        else :
            temp_dict = {
                "class": "ServiceNow",
                "method": "updateTicket",
                "message": "RECIEVED_NON_200_RESPONSE",
                "response": self.response.json(),
                "headers": dict(self.response.headers),
                "response_code": self.response.status_code
            }
            logging_client.write_entry(logger_name=os.environ["log_name"], log_struct=temp_dict, severity="ERROR")
            return temp_dict

    def deleteTicket (self) :
        temp_headers = dict(self.headers)
        temp_headers.update(self._ServiceNowCore__oauth_header)
        self.response = requests.delete(self.url, headers=temp_headers, params=self.query_parameters)
        if self.response.status_code == 204 :
            return 0
        else :
            temp_dict = {
                "class": "ServiceNow",
                "method": "deleteTicket",
                "message": "RECIEVED_NON_204_RESPONSE",
                "response": self.response.json(),
                "headers": dict(self.response.headers),
                "response_code": self.response.status_code
            }
            logging_client.write_entry(logger_name=os.environ["log_name"], log_struct=temp_dict, severity="ERROR")
            return temp_dict

    def getTicket (self) :
        temp_headers = dict(self.headers)
        temp_headers.update(self._ServiceNowCore__oauth_header)
        self.response = requests.delete(self.url, headers=temp_headers, params=self.query_parameters)
        if self.response.status_code == 200 :
            return 0
        else :
            temp_dict = {
                "class": "ServiceNow",
                "method": "getTicket",
                "message": "RECIEVED_NON_200_RESPONSE",
                "response": self.response.json(),
                "headers": dict(self.response.headers),
                "response_code": self.response.status_code
            }
            logging_client.write_entry(logger_name=os.environ["log_name"], log_struct=temp_dict, severity="ERROR")
            return temp_dict

    def queryTable (self) :
        temp_headers = dict(self.headers)
        temp_headers = self._ServiceNowCore__oauth_header
        self.response = requests.get(self.url, headers=temp_headers, params=self.query_parameters)
        if self.response.status_code == 200 :
            return 0
        else :
            temp_dict = {
                "class": "ServiceNow",
                "method": "queryTable",
                "message": "RECIEVED_NON_200_RESPONSE",
                "response": self.response.json(),
                "headers": dict(self.response.headers),
                "response_code": self.response.status_code
            }
            logging_client.write_entry(logger_name=os.environ["log_name"], log_struct=temp_dict, severity="ERROR")
            return temp_dict