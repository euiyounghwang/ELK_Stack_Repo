

# -*- coding: utf-8 -*-
import sys
import json

from elasticsearch import Elasticsearch
import argparse
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd
from threading import Thread
from Search_Engine import Search
import logging
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def work(es_source_client, es_target_client):
    '''  Migrate from old cluster to new cluster for the name of indices and aliases '''

    def get_es_api_alias(source_es_client):
        ''' get all alias and set to dict'''
        ''' https://localhost:9201/_cat/aliases?format=json '''
        get_alias_old_cluster = es_client.indices.get_alias()
        # print(f"Get alias from old cluster : {json.dumps(get_alias_old_cluster, indent=2)}")

        reset_alias_dict = {}
        for k in get_alias_old_cluster.keys():
            if get_alias_old_cluster.get(k).get('aliases'):
                each_alias = list(get_alias_old_cluster.get(k).get('aliases').keys())
                # print(each_alias)
                reset_alias_dict.update({k : each_alias})
        # print(json.dumps(reset_alias_dict, indent=2))
        # print(f"get_es_api_alias : {reset_alias_dict}")

        return reset_alias_dict

    es_obj_s = Search(host=es_source_client)
    es_client = es_obj_s.get_es_instance()

    es_obj_t = Search(host=es_target_client)
    es_t_client = es_obj_t.get_es_instance()

    ''' get/set alias from old cluser'''
    get_alias_dict = get_es_api_alias(es_client)

    ''' k : real index, v : alias'''
    success_index_lists = []
    for k, v in get_alias_dict.items():
        try:
            # logging.info(f"k : {k}, v : {''.join(v)}")
            response = es_t_client.indices.put_alias(k, ''.join(v))
            if response:
                logging.info(f"Success with indics : {k}, alias : {''.join(v)}")
                success_index_lists.append({k : ''.join(v)})
        except Exception as e:
            logging.error(e)
            # pass
        
    print("\n")
    print("-"*50)
    print(json.dumps(success_index_lists, indent=2))
    print("-"*50)
    print("\n")
    logging.info(f"finished..")
    

if __name__ == "__main__":
    
    '''
    (.venv) ➜  ELK-upgrade git:(master) ✗ python ./upgrade-script/migrate-alias-script.py --es http://localhost:9200 --ts https://localhost:9201
    '''
    parser = argparse.ArgumentParser(description="Index into Elasticsearch using this script")
    parser.add_argument('-e', '--es', dest='es', default="http://localhost:9209", help='host source')
    parser.add_argument('-t', '--ts', dest='ts', default="http://localhost:9292", help='host target')
    args = parser.parse_args()
    
    if args.es:
        es_source_host = args.es
        
    if args.ts:
        es_target_host = args.ts
        
    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        th1 = Thread(target=work, args=(es_source_host, es_target_host))
        th1.start()
        th1.join()
        
    except Exception as e:
        logging.error(e)
        pass
    
  