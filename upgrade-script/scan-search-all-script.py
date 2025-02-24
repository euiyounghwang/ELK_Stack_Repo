


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
file_output = path + "/Scan-IDs"


def work(es_source_client, index_name):
    '''
    Extract all ids via scan API for a mount of records
    '''

    def output_clear():
        if not os.path.exists(path):
             os.makedirs(path)

        if os.path.exists(file_output):
            # print("The file does exist")
            os.remove(file_output)
        # else:
        #     print("The file does not exist")

    
    def export_file(query_ids_from_es):
        ''' export to file '''
        with open(f"{file_output}", "a") as f:
            for k in query_ids_from_es:
                f.write(f"{k}" + '\n')
              

    def scroll_API(index, body):
        result = []

        _KEEP_ALIVE_LIMIT='30s'

        # Initialize the scroll
        page = es_client.search(index=index
                        ,body=body
                        ,scroll=_KEEP_ALIVE_LIMIT
                        ,size=10000
                        # ,track_total_hits=True
                        )
        sid = page['_scroll_id']
        # scroll_size = page['hits']['total']['value']
        scroll_size = page['hits']['total']

        # Start scrolling
        result += page['hits']['hits']


        while (scroll_size > 0):
            print('Scrolling...')
            page = es_client.scroll(scroll_id=sid, scroll=_KEEP_ALIVE_LIMIT)

            # Update the scroll ID
            sid = page['_scroll_id']

            # Get the number of results that we returned in the last scroll
            # scroll_size = len(page['hits']['hits'])
            scroll_size = len(page['hits']['hits'])
            print("scroll size: ", str(scroll_size))
            result += page['hits']['hits']
            

        es_client.clear_scroll(body={'scroll_id': [sid]}, ignore=(404, ))
        return result
        
    logging.info(f"{es_source_client}")

    es_obj_s = Search(host=es_source_client)
    es_client = es_obj_s.get_es_instance()

    query = {
        "_source": False,
	    'query': {
    	    'match_all': {}
        }
        # "query": {
        #     "bool": {
        #         "must": [
        #             {
        #                 "range": {
        #                     "ADDTS": {
        #                     "gte": "08/10/2020",
        #                     "lte": "12/07/2024",
        #                     "format": "MM/dd/yyyy"
        #                     }
        #                 }
        #             },
        #             {
        #                 "range": {
        #                     "EDITTS": {
        #                         "gte": "01/01/2022",
        #                         "lte": "12/21/2022",
        #                         "format": "MM/dd/yyyy"
        #                 }
        #             }
        #           }
        #         ]
        #     }
        # }
    }

    output_clear()

    batch_size = 10000

    response = helpers.scan(client=es_client, 
                              query=query, 
                              index=index_name,
                              size=batch_size,
                              scroll='60m',
                              request_timeout=1800000)
    
    '''
    response = scroll_API(index='wx_loc_10052020_20_5_1', body=query)
    '''

    query_ids_from_es = list(set(r['_id'] for r in response))
    query_ids_from_es.sort()
    export_file(query_ids_from_es)

    print('-'*50)
    print(f"docs : {len(query_ids_from_es)}")
    print('Created..')
    print('-'*50)
    


if __name__ == "__main__":
    
    '''
    (.venv) ➜  python ./upgrade-script/scan-search-all-script.py --es http://source_es_cluster:9200 --index test

    '''
    parser = argparse.ArgumentParser(description="Index into Elasticsearch using this script")
    parser.add_argument('-e', '--es', dest='es', default="http://localhost:9200", help='host source')
    parser.add_argument('-i', '--index', dest='index', default="test", help='index name')
    args = parser.parse_args()
    
    if args.es:
        es_source_host = args.es

    if args.index:
        index = args.index
        
    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        th1 = Thread(target=work, args=(es_source_host, index))
        th1.start()
        th1.join()
        
    except Exception as e:
        logging.error(e)
        pass
    