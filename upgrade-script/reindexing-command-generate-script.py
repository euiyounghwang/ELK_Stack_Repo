


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
import random
from hashlib import md5
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


DOCS_CNT = 5000000

path = os.path.dirname(os.path.abspath(__file__)) + '/output'
file_output = path + "/reindexing_command"


def work(es_source_host, es_target_host):
    ''' 
    The best way to reindex is to use Elasticsearch's builtin Reindex API as it is well supported and resilient to known issues.
    The Elasticsaerch Reindex API uses scroll and bulk indexing in batches , and allows for scripted transformation of data. 
    In Python, a similar routine could be developed:
    '''

    def output_clear():
        if not os.path.exists(path):
             os.makedirs(path)

        if os.path.exists(file_output):
            print("The file does exist")
            os.remove(file_output)
        else:
            print("The file does not exist")

        ''' add header '''
        with open(f"{file_output}", "a") as f:
            f.write(f"# Reindexing script" + '\n')


    def export_file(source_host, target_host, ranked_index):
        ''' export to file '''
        with open(f"{file_output}", "a") as f:
            ''' call to making_script'''
            ''' python ./Search-reindexing-script.py --es http://localhost:9200 --source_index test_index --type test_index_doc --ts https://localhost:9201 '''

            # ranked_keys = sorted(ranked_index, reverse=True)
            ranked_keys = dict(sorted(ranked_index.items(), key = lambda x: (x[1]["count"]), reverse=True))
            # print(ranked_keys)

            # for k, v in ranked_index.items():
            ''' create python script with argument for reindexing'''
            for k in ranked_keys:
                f.write(f"\n# Index : {ranked_index[k].get('each_index')}, docs : {ranked_index[k].get('count'):,}" + '\n')
                if int(ranked_index[k].get('count')) > DOCS_CNT:
                    # print('wow', v)
                    f.write(f"nohup python ./Search-reindexing-script.py --es {source_host} --source_index {ranked_index[k].get('each_index')} --type {ranked_index[k].get('get_type')} --ts {target_host} > {ranked_index[k].get('get_type')}.log 2>&1 </dev/null &" + '\n')
                    # f.write('\n')
                else:
                    # print('nop, wow', v)
                    f.write(f"python ./Search-reindexing-script.py --es {source_host} --source_index {ranked_index[k].get('each_index')} --type {ranked_index[k].get('get_type')} --ts {target_host}" + '\n')
                    # f.write('\n')

            ''' create tracking counts on each ES indices before reindexing'''
            f.write(f"\n\nSource ES Cluster\tES Indices\tCount")
            for k in ranked_keys:
                f.write(f"\n{source_host}\t{ranked_index[k].get('each_index')}\t{int(ranked_index[k].get('count')):,}")

            

    es_obj_s = Search(host=es_source_host)
    es_client = es_obj_s.get_es_instance()

    ''' extact a list of indices from the source cluster'''
    source_idx_lists = es_client.indices.get("*")
    # logging.info(f"{source_idx_lists}")

    ''' delete output file'''
    output_clear()

    ranked_index = {}
    for each_index in source_idx_lists:
        # if str(each_index).startswith("om") or str(each_index).startswith("wx") or str(each_index).startswith("es") or str(each_index).startswith("archive"):
        if str(each_index).startswith("om") or str(each_index).startswith("wx"):
            each_mapping = es_client.indices.get_mapping(index=each_index)
            # print(each_mapping)
            for v in each_mapping.values():
                ''' get the name of type'''
                get_type = list(v.get("mappings").keys())[0]
            # print(get_type)
            res_count = es_client.count(index=each_index, body={'query': { 'match_all' : {}}})["count"]

            ''' extract output command for reindexing if count is grater than zero'''
            if int(res_count) > 0:
                ranked_index.update(
                                {
                                    each_index : {
                                        "each_index" : each_index,
                                        "get_type" : get_type,
                                        "count" : int(res_count)
                                }
                    }
                )
            
            
    export_file(es_source_host, es_target_host, ranked_index)
    
    print('\n')
    print('---')
    print('Created..')
    print('---')
    print('\n')


    
   

if __name__ == "__main__":
    
    '''
    Generate the command for reindexing
    (.venv) ➜  python ./upgrade-script/reindexing-command-generate-script.py --es http://source_es_cluster:9200 --ts http://target_es_cluster:9201
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
        th1 = Thread(target=work, args=(es_source_host,es_target_host,))
        th1.start()
        th1.join()
        
    except Exception as e:
        logging.error(e)
        pass
    