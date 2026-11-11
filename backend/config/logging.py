"""Do not attach request-body or coordinate logging. Proxy/APM redaction is separate."""
LOGGING={'version':1,'disable_existing_loggers':False,'handlers':{'console':{'class':'logging.StreamHandler'}},'loggers':{'django':{'handlers':['console'],'level':'WARNING','propagate':False}}}
