from config.log_config import create_log
from config import config
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
# import yaml
import json
import os

# def read_config_yaml():
#     with open('./config.yaml', 'r') as f:
#         doc = yaml.load(f, Loader=yaml.FullLoader)
        
#     logger.info(json.dumps(doc, indent=2))
    
#     return doc

#--
# read host file to make an enum
def read_hosts(server_file):
    server_list_dict = {}
    with open(server_file) as data_file:
        for line in data_file:
            line = line.strip().split(",")
            # print(f"{line}")
            server_list_dict.update({line[0] : str(line[1]).lower()})
    return server_list_dict


load_dotenv()
    
# Initialize & Inject with only one instance
logger = create_log()


hosts = read_hosts("./repository/hosts")
''' hosts = ['localhost', 'dev',...] '''
# logger.info(list(hosts.keys()))
es_hosts_enum_list =list(hosts.keys())
