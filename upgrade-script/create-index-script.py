


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




def work(es_source_client, es_target_client, src_idx, dest_idx, index_type):
    ''' 
    The best way to reindex is to use Elasticsearch's builtin Reindex API as it is well supported and resilient to known issues.
    The Elasticsaerch Reindex API uses scroll and bulk indexing in batches , and allows for scripted transformation of data. 
    In Python, a similar routine could be developed:
    '''

    def get_es_api_alias(es_client):
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
    

    def try_delete_create_index(es_t_client, index, mapping):
        try:
            # logging.info(mapping)
            if es_t_client.indices.exists(index):
                raise Exception("Index has already exist")
                # logging.info('Alreday exists : {}'.format(index))
                # es_t_client.indices.delete(index)
                
            # now create a new index
            es_t_client.indices.create(index=index, body=mapping)
            # es_client.indices.put_alias(index, "omnisearch_search")
            es_t_client.indices.refresh(index=index)
            logging.info("Successfully created: {}".format(index))
            
        except Exception as e:
            logging.error(e)
            pass
            
    
    es_source_client = es_source_client.replace('\r','')
    es_target_client = es_target_client.replace('\r','')
    src_idx = src_idx.replace('\r','')
    dest_idx = dest_idx.replace('\r','')

    logging.info(f"{es_source_client, es_target_client, src_idx, dest_idx}")

    es_obj_s = Search(host=es_source_client)
    es_client = es_obj_s.get_es_instance()

    es_obj_t = Search(host=es_target_client)
    es_t_client = es_obj_t.get_es_instance()

    source_idx_lists = []
    if src_idx == 'all':
        ''' extact a list of indices from the source cluster'''
        source_idx_lists = es_client.indices.get("*")
        # logging.info(f"{source_idx_lists}")
    else:
         source_idx_lists = [src_idx]

   
    ''' get Alias'''
    get_alias_dict = get_es_api_alias(es_client)
    # print(get_alias_dict)
    
    idx_cnt = 0
    ''' create index with mappping from ES v.5 after transforming'''
    for each_index in source_idx_lists:
        ''' exclude system indices in the source cluster such as .monitoring-es-7-2024.07.12'''
        if '.' not in each_index:
           if str(each_index).startswith("om_") or str(each_index).startswith("wx_") or str(each_index).startswith("es_") or str(each_index).startswith("archive_es_"):
                print(f'each_index - {each_index}')
                src_idx_mapping = es_client.indices.get_mapping(index=each_index)

                idx_json = {
                    "settings": {
                        "index": {
                            "number_of_shards": "5",
                            "number_of_replicas": "1"
                        }
                    },
                    "mappings" : {}
                }
                idx_json.update({"mappings" : src_idx_mapping.get(each_index).get("mappings")})
                # logging.info(json.dumps(idx_json, indent=2))

                ''' Get the mappings with a specific index from source cluster and create index into new cluster as ts'''
                try_delete_create_index(es_t_client, each_index, idx_json)

                ''' update aliase'''
                print(each_index, get_alias_dict.get(each_index))
                ''' if aliase exists in source es client'''
                if get_alias_dict.get(each_index):
                    response = es_t_client.indices.put_alias(each_index, ''.join(get_alias_dict.get(each_index)))
                    if response:
                        logging.info(f"Success with indics : {each_index}, alias : {''.join(get_alias_dict.get(each_index))}")
                idx_cnt += 1

    print('\n\n****')
    print('Create index : {}'.format(idx_cnt))
    print('\n\n****')
    


if __name__ == "__main__":
    
    '''
    create index with alias from source cluster to target cluster. we only use a specific index for this script (For ES v.5)
    (.venv, migrate all indexes) ➜  python ./upgrade-script/create-index-script.py --es http://dev:9200 --ts http://dev:9200
    (.venv) ➜  python ./upgrade-script/create-index-script.py --es http://dev:9200 --source_index wx_order_02072022_22_2_1 --ts http://dev:9200

    '''
    parser = argparse.ArgumentParser(description="Index into Elasticsearch using this script")
    parser.add_argument('-e', '--es', dest='es', default="http://localhost:9200", help='host source')
    parser.add_argument('-s', '--source_index', dest='source_index', default="all", help='source_index')
    parser.add_argument('-y', '--type', dest='type', default="_doc", help='_type')
    parser.add_argument('-t', '--ts', dest='ts', default="http://localhost:9201", help='host target')
    args = parser.parse_args()
    
    if args.es:
        es_source_host = args.es
        
    if args.ts:
        es_target_host = args.ts
        
    if args.source_index:
        es_source_index = args.source_index

    if args.type:
        index_type = args.type

    '''
    if args.target_index:
        es_target_index = args.target_index
    else:
        es_target_index = args.source_index
    '''
    es_target_index = es_source_index
    # es_target_index = 'test_reindex_script_{}'.format(es_source_index)
        
    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        th1 = Thread(target=work, args=(es_source_host, es_target_host, es_source_index, es_target_index, index_type))
        th1.start()
        th1.join()
        
    except Exception as e:
        logging.error(e)
        pass
    