


# -*- coding: utf-8 -*-
import sys
import json

from elasticsearch import Elasticsearch
import argparse
from dotenv import load_dotenv
import dotenv
import os
from datetime import datetime
import pandas as pd
from threading import Thread
from Search_Engine import Search
import logging
import random
from hashlib import md5
import warnings
warnings.filterwarnings("ignore")

# load_dotenv()
dotenv.load_dotenv(".env", override=True)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def get_indices_replica_zero(es_client):
    """
    params es_client: es instance
    """
    es_indices = es_client.indices.get("*")
    please_set_the_number_of_replicas = []
    for each_indice in es_indices.keys():
        # print(f"Replica : {es_indices.get(each_indice).get('settings').get('index').get('number_of_replicas')}")
        the_number_of_replicas = int(es_indices.get(each_indice).get('settings').get('index').get('number_of_replicas'))
        if the_number_of_replicas < 1:
            please_set_the_number_of_replicas.append(each_indice)

    return please_set_the_number_of_replicas


def work(es_target_host):
    """
    params es_target_host: Target es client host
    """
    try:
   
        es_obj_t = Search(host=es_target_host)
        es_client = es_obj_t.get_es_instance()

        please_set_the_number_of_replicas = get_indices_replica_zero(es_client)
        print(f"\nplease_set_the_number_of_replicas : {please_set_the_number_of_replicas}")

        if please_set_the_number_of_replicas :
            print(f"Set the number of replicas")
            for need_to_set_replica in please_set_the_number_of_replicas:
                # Restore the desired number of replicas after indexing
                es_client.indices.put_settings(
                    index=need_to_set_replica,
                    body={"settings": {"number_of_replicas": 1, "refresh_interval": None}}
                )
                print(f"Number of replicas restored to 1 for the ES indics: {need_to_set_replica}")
    
    except Exception as e:
        print(e)

    finally:
        print('\n')
        print('---')
        print(f"Script for the the number of replica has been finished..")
        print('---')
        print('\n')
       

if __name__ == "__main__":
    
    '''
    Set the number of replicas
    (.venv) ➜  python ./upgrade-script/update-replica-script.py --ts http://target_es_cluster:9201
    '''

    parser = argparse.ArgumentParser(description="Update the number of replicas into Elasticsearch using this script")
    parser.add_argument('-t', '--ts', dest='ts', default="http://localhost:9201", help='host target')
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
    