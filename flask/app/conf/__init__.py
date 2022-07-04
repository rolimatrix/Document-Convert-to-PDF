# coding=utf-8
import datetime, logging
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        if not log_record.get('timestamp'):
            # this doesn't use record.created, so it is slightly off
            now = datetime.datetime.now(datetime.timezone.utc)
            #now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            log_record['timestamp'] = now
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

#init logging
def _init_logging(moduleName):

    logger = logging.getLogger(moduleName)
    logger.setLevel(logging.INFO)
    logHandler = logging.StreamHandler()
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(message)s %(fehlerbildnummer)s %(incomming_message)s %(communication_pattern)s '
                                    '%(service_domain)s %(service_call)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    return logger
