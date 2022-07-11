from google.cloud import logging

class GCPLogger :

    def __init__ (self, gcp_project) :
        self.__logging_client = logging.Client(project=gcp_project)

    def write_entry(self, logger_name, log_struct, severity):
        """Writes log entries to the given logger."""

        # This log can be found in the Cloud Logging console under 'Custom Logs'.
        logger = self.__logging_client.logger(logger_name)

        logger.log_struct(
            log_struct,
            severity = severity
        )

        # print("Wrote logs to {}.".format(logger.name))