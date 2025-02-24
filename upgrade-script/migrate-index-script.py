


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



# Index_Prefix = "test_reindex_script_"
Index_Prefix = ""


def work(es_source_client, es_target_client):
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
    

    def try_create_index(es_client, index, mapping):
        try:
            # logging.info(mapping)
            if es_client.indices.exists(index):
                raise Exception("Index has already exist")
            
            # now create a new index
            es_client.indices.create(index=index, body=mapping)
            # es_client.indices.put_alias(index, "omnisearch_search")
            es_client.indices.refresh(index=index)
            logging.info("Successfully created: {} to {}".format(index, es_t_client))
            
        except Exception as e:
            logging.error(e)
            pass
            
    
    def recursive_lookup(k, d):
        if k in d:
            return d[k]
        for v in d.values():
            if isinstance(v, dict):
                return recursive_lookup(k, v)
        return None
    

    def get_mapping_from_es_v5_to_es_8(es_t_client, each_index):

        def replace_mapping_type_for_field(each_mapping):
            ''' replace mapping if it needs'''
            # if 'CONSOLIDATIONID' in json.dumps(each_mapping):
            #     logging.info(f"each_index - {each_index}, each_mapping : {each_mapping}")
                
            return json.loads(json.dumps(each_mapping).replace('"CONSOLIDATIONID": {"type": "integer"}','"CONSOLIDATIONID": {"type": "double"}')
                            #   .replace('"PRINTBATCHID": {"type": "integer"}','"PRINTBATCHID": {"type": "double"}')
                              )

        def get_recursive_nested_all(d):
            if isinstance(d, list):
                for i in d:
                    get_recursive_nested_all(i)
            elif isinstance(d, dict):
                for k, v in d.items():
                    if not isinstance(v, (list, dict)):
                        # print("%%%%", k, v)
                        if k == "format" and v == "MM/dd/yyyy hh:mm:ss.SSSSSS a Z":
                            d[k] = "MM/dd/yyyy hh:mm:ss.SSSSSS a z||MM/dd/yyyy hh:mm:ss.SSSSSS a Z"
                    else:
                        get_recursive_nested_all(v)

            ''' unnecessary field should removed by this function like "query"'''
            if 'query' in d:
                del d['query']
            return d

        # logging.info(f"index : {each_index}, mapping = {json.dumps(es_client.indices.get_mapping(index=each_index), indent=2)}")
        each_mapping = es_client.indices.get_mapping(index=each_index)
        ''' replace mapping type for specific field'''
        each_mapping = replace_mapping_type_for_field(each_mapping)
        
        get_only_properties = recursive_lookup("properties", each_mapping)
        # logging.info(f"mappings_get : {json.dumps(get_only_properties, indent=2)}")

        idx_json.update({
                        "mappings" : {
                            "properties" : get_recursive_nested_all(get_only_properties)
                        }
                 }
            )
        
        # print('\n----')
        # print(f"idx_json : {json.dumps(idx_json, indent=2)}")
        # print('\n----')
                            
        ''' Get the mappings with a specific index from source cluster and create index into new cluster as ts'''
        try_create_index(es_t_client, "{}{}".format(Index_Prefix, each_index), idx_json)

    
    logging.info(f"{es_source_client, es_target_client}")

    es_obj_s = Search(host=es_source_client)
    es_client = es_obj_s.get_es_instance()

    es_obj_t = Search(host=es_target_client)
    es_t_client = es_obj_t.get_es_instance()
    

    ''' extact a list of indices from the source cluster'''
    source_idx_lists = es_client.indices.get("*")
    # logging.info(f"{source_idx_lists}")

    # is_dev_mode = True
    is_dev_mode = False

    is_update_aliase = True
    # is_update_aliase = False

    specific_index = "wx_order_02072022_22_2_1"

    ''' get/set alias from old cluser'''
    if is_update_aliase:
        get_alias_dict = get_es_api_alias(es_client)

    # print(json.dumps(get_alias_dict, indent=2))
    # exit()

    idx_json = {}
    migrated_total_indices_cnt = 0
    ''' create index with mappping from ES v.5 after transforming'''
    for each_index in source_idx_lists:
        ''' exclude system indices in the source cluster such as .monitoring-es-7-2024.07.12'''
        if '.' not in each_index:
            if is_dev_mode:
                if each_index == specific_index:
                   get_mapping_from_es_v5_to_es_8(es_t_client, each_index)
            else:
                if str(each_index).startswith("om_") or str(each_index).startswith("wx_") or str(each_index).startswith("es_") or str(each_index).startswith("archive_"):
                    get_mapping_from_es_v5_to_es_8(es_t_client, each_index)
                    migrated_total_indices_cnt +=1

    ''' update aliase to ES v.8'''
    if is_update_aliase:
        for each_index in source_idx_lists:
            if '.' not in each_index and (each_index.startswith("wx_") or each_index.startswith("om_") or each_index.startswith("es_") or each_index.startswith("archive_es_")):
                print(f"each_index : {each_index}")
                if es_t_client.indices.exists("{}{}".format(Index_Prefix, each_index)):
                    if each_index in get_alias_dict.keys():
                        logging.info(f"Alias Printout : {each_index}, {get_alias_dict.get(each_index)}")
                        response = es_t_client.indices.put_alias("{}{}".format(Index_Prefix, each_index), ''.join(get_alias_dict.get(each_index)))
                        logging.info(f"response : {response}")
                        logging.info(f"Success with indics : {each_index}, alias : {''.join(get_alias_dict.get(each_index))}")
                        
    logging.info(f"Migrated Indices : {migrated_total_indices_cnt}")                    
    


if __name__ == "__main__":
    
    '''
    create index with mappings from source cluster to target cluster. It can be put the alias from source to target during reindexing via reindexing script
    (.venv) ➜  python ./upgrade-script/migrate-index-script.py --es http://localhost:9200 --ts https://localhost:9201
    

    '''
    parser = argparse.ArgumentParser(description="Index into Elasticsearch using this script")
    parser.add_argument('-e', '--es', dest='es', default="http://localhost:9200", help='host source')
    parser.add_argument('-t', '--ts', dest='ts', default="http://localhost:9201", help='host target')
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
    