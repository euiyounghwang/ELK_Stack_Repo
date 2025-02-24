


# -*- coding: utf-8 -*-
import sys
import json

from elasticsearch import Elasticsearch, helpers
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


path = os.path.dirname(os.path.abspath(__file__)) + '/output'
file_output = path + "/Scan_Ids"


def work(es_source_client, idx):
    '''
    Extract all ids via scan API for a mount of records
    '''

    def output_clear():
        if not os.path.exists(path):
             os.makedirs(path)

        if os.path.exists(file_output):
            os.remove(file_output)

    
    def export_file(query_ids_from_es):
        ''' export to file '''
        with open(f"{file_output}", "a") as f:
            for k in query_ids_from_es:
                f.write(f"{k}" + '\n')
              

    logging.info(f"{es_source_client}")

    es_obj_s = Search(host=es_source_client)
    es_client = es_obj_s.get_es_instance()

    query = {
        "_source": False,
	    'query': {
    	    'match_all': {}
        }
    }

    output_clear()

    batch_size = 10000

    response = helpers.scan(client=es_client, 
                              query=query, 
                              index=idx,
                              size=batch_size,
                              scroll='60m',
                              request_timeout=1800000)
    
    query_ids_from_es = list(set(r['_id'] for r in response))

    ''' clear file'''
    output_clear()

    ''' add results to file'''
    export_file(query_ids_from_es)

    print('-'*50)
    print(f"docs : {len(query_ids_from_es)}")
    print('Created..')
    print('-'*50)
    


if __name__ == "__main__":
    
    """
    get all ids
    (.venv) ➜  python ./devops/scan-es.py --es http://source_es_cluster:9200
    """
    parser = argparse.ArgumentParser(description="Index into Elasticsearch using this script")
    parser.add_argument('-e', '--es', dest='es', default="http://localhost:9200", help='host source')
    parser.add_argument('-i', '--idx', dest='idx', default="test", help='idx')
    args = parser.parse_args()
    
    if args.es:
        es_source_host = args.es

    if args.idx:
        idx = args.idx
        
    """ Only One process we can use due to 'Global Interpreter Lock'. 'Multiprocessing' is that we can use for running with multiple process """
    try:
        th1 = Thread(target=work, args=(es_source_host, idx))
        th1.start()
        th1.join()
        
    except Exception as e:
        logging.error(e)
        pass
    