import os
import json
from google.cloud import datastore

os.environ["CONFIG_KEY"] = os.environ.get("CONFIG_KEY")

config_key = os.environ.get("CONFIG_KEY")
config_kind = f"{config_key.split('/')[0]}"
config_name = f"{config_key.split('/')[1]}"

datastore_client = datastore.Client()
task_key = datastore_client.key(config_kind, config_name)
entity = datastore_client.get(key=task_key)

# gcp common variables
gcp_project = entity.get("gcp_project")
log_name = entity.get("log_name", "ticket-automation-application")

# servicenow function variables
servicenow_client_url = entity.get("servicenow_client_url")

# runtime variables
webhook_payload = {}