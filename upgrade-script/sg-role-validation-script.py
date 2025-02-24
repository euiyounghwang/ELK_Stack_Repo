


# -*- coding: utf-8 -*-
import sys
import json

import argparse
from dotenv import load_dotenv
import os
from datetime import datetime
from threading import Thread
import requests
import coloredlogs, logging
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
# coloredlogs.install()


path = os.path.dirname(os.path.abspath(__file__)) + '/output'
file_output = path + "/sgconfig_permissions"

INDEX = "logstash-2024-08-01"

def work(es_target_client):
    '''
    Validate a list of indices from the source cluster and compare them to target cluster
    '''

    def import_file(file):
        ''' transform to json format for the host'''
        '''
        test_user|test==|_cluster/health?format=json
        test_user|test==|_cat/indices?format=json
        test_user|test==|_cat/aliases?format=json
        test_user|test==|_cat/nodes?format=json
        test_user|test==|test_10052020_20_5_1/_search
        test_user|test==|logstash-2024.08.21/_search

        2024-08-22 11:51:42,978 : INFO : sg_info_dicts - {
            "test_user": {
                "header": "test",
                "urls": [
                    "_cat/indices?v",
                    "_cat/aliases?v",
                    "_cat/aliases?v",
                    "om_test/_search",
                    "wx_test/_search",
                    "logstash-2024.08.21/_search"
                ]
            }
            ...
        }
        '''
        sg_info_dicts = {}
        path = os.path.dirname(os.path.abspath(__file__)) + '/input'
        with open(path + "/{}".format(file)) as data_file:
            for line in data_file:
                if '#' in line:
                    continue
                line = line.strip().split("|")
                user = line[0]
                if user in sg_info_dicts.keys():
                    sg_info_dicts.update({user : {
                        "header" : line[1],
                        "urls" : sg_info_dicts.get(user).get("urls") + [line[2].lower()]
                    }})
                else:
                    sg_info_dicts.update({user : {
                        "header" : line[1],
                        "urls" : []
                    }})
                
        # logging.info(f"sg_info_dicts - {json.dumps(sg_info_dicts, indent=2)}")
        return sg_info_dicts
    

    def delete_sg_permission_check(target_host, user, basic_auth):
        ''' check if user has permission to delete'''
        try:
            ''' BASIC Authentication in HTTP Header'''
            header =  {
                'Content-type': 'application/json', 
                'Authorization' : 'Basic {}'.format(basic_auth)
            }
            # logging.info(f"header : {header}")
            http_urls = "{}/{}".format(target_host, INDEX)
            # logging.info(f"http_urls : {http_urls}")

            resp = requests.delete(url=http_urls, headers=header, verify=False, timeout=600)
            ''' check first records if user has permission to write'''
            logging.info(f"DELETE [{resp.status_code}] User ['{user}'] - DELETE INDEX Request : {http_urls}, Response - {resp.json()}")
            
        except Exception as e:
            logging.error(f"Error : {e}")
            pass

    def post_sg_permission_check(target_host, user, basic_auth):
        ''' check first records if user has permission to write'''
        try:
            ''' BASIC Authentication in HTTP Header'''
            header =  {
                'Content-type': 'application/json', 
                'Authorization' : 'Basic {}'.format(basic_auth)
            }
            # logging.info(f"header : {header}")
            http_urls = "{}/_bulk".format(target_host)
            # logging.info(f"http_urls : {http_urls}")

            body = [
                {"index" : { "_index" : INDEX, "_id" : "1"}},
                {"ADDTS" : "03/09/2023 02:06:34.739993" }
            ]

            payload = '\n'.join([json.dumps(line) for line in body]) + '\n'

            resp = requests.post(url=http_urls, headers=header, data=payload, verify=False, timeout=600)
            ''' check first records if user has permission to write'''
            status = resp.json()["items"][0]["index"]["status"]
            if "errors" in resp.json() and resp.json()["errors"] == True:
                logging.error(f"POST [{status}] User ['{user}'] - CREATE INDEX request : {resp.json()}")
            else:
                logging.info(f"POST [{resp.status_code}] User ['{user}'] - CREATE INDEX request : {resp.json()}")
            
        except Exception as e:
            logging.error(f"Error : {e}")
            pass


    def get_sg_permission_check(target_host, user, urls, basic_auth):
        ''' request_sg_permission_check '''
        try:
            ''' BASIC Authentication in HTTP Header'''
            header =  {
                'Content-type': 'application/json', 
                'Authorization' : 'Basic {}'.format(basic_auth)
                # 'Authorization' : '{}'.format(os.getenv('BASIC_AUTH')),
            }
            # logging.info(f"header : {header}")
            http_urls = "{}/{}".format(target_host, urls)
            # logging.info(f"http_urls : {http_urls}")
            resp = requests.get(url=http_urls, headers=header, verify=False, timeout=600)
                
            if not (resp.status_code == 200):
                ''' if host not reachable'''
                logging.error(f"GET [{resp.status_code}] User ['{user}'], Urls [{urls}], X-pack access - {resp.json()}")
                # logging.error(f"[{resp.status_code}] User [{user}], Urls [{urls}]")
            else:
                logging.info(f"GET [{resp.status_code}] User ['{user}'], Urls [{urls}]")

        except Exception as e:
            logging.error(f"Error : {e}")
            pass
                            
    
    ''' clear output file'''
    # output_clear()

    '''
    es_admin|test==|_cluster/health?format=json
    es_admin|test==|_cat/indices?format=json
    es_admin|test==|_cat/aliases?format=json
    es_admin|test==|_cat/nodes?format=json
    es_admin|test==|logstash-2024.08.21/_search
    '''
    sg_info_dict = import_file("./sg-user")

    ''' Validate permission to ES with X-pack based on SG'''
    ''' 403 means credentials errors or that you don't have permission '''
    for k, v in sg_info_dict.items():
        logging.info("\n")
        logging.info("--")
        logging.info(f"# X-pack User : '{k}' to ES v.8.12 [{es_target_client}]")
        ''' Create sample index '''
        post_sg_permission_check(es_target_client, k, v.get("header"))
        ''' DELETE sample index '''
        delete_sg_permission_check(es_target_client, k, v.get("header"))
        ''' Create sample index '''
        post_sg_permission_check(es_target_client, k, v.get("header"))
        for each_url in v.get("urls"):
            # print(es_target_client, k, each_url, v.get("header"))
            get_sg_permission_check(es_target_client, k, each_url, v.get("header"))
        logging.info("--")
    
    logging.info("\n")
    


if __name__ == "__main__":
    
    '''
    (.venv) ➜  python ./upgrade-script/sg-role-validation-script.py --ts https://target_es_cluster:9201
    The port 9200 is for http clients and port 9300 is for tcp clients. In 5.x we use both. 
    Once we are ready for 8.x we need to move the Cliy teams to 9200 as the 9300 port is no longer supported.
    '''
    parser = argparse.ArgumentParser(description="Index into Elasticsearch using this script")
    parser.add_argument('-t', '--ts', dest='ts', default="https://localhost:9201", help='host target')
    args = parser.parse_args()
    
        
    if args.ts:
        es_target_host = args.ts
        
    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        th1 = Thread(target=work, args=(es_target_host,))
        th1.start()
        th1.join()
        
    except Exception as e:
        logging.error(e)
        pass
    