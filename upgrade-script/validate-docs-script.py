


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


path = os.path.dirname(os.path.abspath(__file__)) + '/output'
file_output = path + "/validation_docs"

def work(es_source_client, es_target_client):
    '''
    Validate a list of indices from the source cluster and compare them to target cluster
    '''
    def output_clear():
        if not os.path.exists(path):
             os.makedirs(path)

        if os.path.exists(file_output):
            # print("The file does exist")
            os.remove(file_output)
        # else:
        #     print("The file does not exist")


    def export_file(source_host, target_host, results):
        ''' export to file '''
        with open(f"{file_output}", "a") as f:
            ''' call to making_script'''
            for each_dict in results:
                for k, v in each_dict.items():
                    f.write(f"{k}\t{source_host}\t{v.get('source_docs')}\t{target_host}\t{v.get('target_docs')}\t{v.get('count')}" + '\n')
            

    def try_exists_index(es_client, index):
        try:
            # logging.info(mapping)
            if es_client.indices.exists(index):
               return True
            return False
            
        except Exception as e:
            logging.error(e)
            pass
            
    
    es_source_client = es_source_client.replace('\r','')
    es_target_client = es_target_client.replace('\r','')
    
    logging.info(f"{es_source_client, es_target_client}")

    es_obj_s = Search(host=es_source_client)
    es_client = es_obj_s.get_es_instance()

    es_obj_t = Search(host=es_target_client)
    es_t_client = es_obj_t.get_es_instance()

    ''' compare all records with match_all '''
    query = {
        # "_source": False,
	    'query': {
    	    'match_all': {}
        }
    }

    ''' compare all records with this condition '''
    '''
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "range": {
                            "ADDTS": {
                            "gte": "08/10/2020",
                            "lte": "12/07/2024",
                            "format": "MM/dd/yyyy"
                            }
                        }
                    },
                    {
                        "range": {
                            "EDITTS": {
                            "gte": "01/01/2022",
                            "lte": "12/21/2022",
                            "format": "MM/dd/yyyy"
                            }
                        }
                    }
                ]
            }
        }
    }
    '''
    

    ''' extact a list of indices from the source cluster'''
    source_idx_lists = es_client.indices.get("*")
    # logging.info(source_idx_lists)
    is_not_exist_lists, different_doc = [], []
    all_docs_df = {}
    source_cluter, target_cluter, index_column, index_value, source_cnt, target_cnt = [], [], [], [], [], []
    for each_index in source_idx_lists:
        ''' exclude system indices in the source cluster such as .monitoring-es-7-2024.07.12'''
        if '.' not in each_index:
            res_count_source, res_count_target = 0, 0
            ''' compare each index between source cluster and target cluster'''
            is_exist = try_exists_index(es_t_client, each_index)
            logging.info(f"validate index [{each_index}] exsits : results is {is_exist}")
            ''' check the number of count'''
            res_count_source = es_client.count(index=each_index, body=query)["count"]
            if is_exist:
                res_count_target = es_t_client.count(index=each_index, body=query)["count"]
            
            index_column.append(each_index)

            if res_count_source > res_count_target:
                different_doc.append({
                                        each_index : {
                                            "source_docs" : "%s" % res_count_source,
                                            "target_docs" : "%s" % res_count_target,
                                             "count" : "Differ"
                                            }
                                    }
                                )
                index_value.append(False)
            else:
                different_doc.append({
                                        each_index : {
                                            "source_docs" : "%s" % res_count_source,
                                            "target_docs" : "%s" % res_count_target,
                                             "count" : "Same"
                                            }
                                    }
                            )
                index_value.append(True)

            ''' es cluster '''
            source_cluter.append(es_client)
            target_cluter.append(es_t_client)
            ''' index cnt '''
            source_cnt.append(res_count_source)
            target_cnt.append(res_count_target)

            # print(res)
            if not is_exist:
                is_not_exist_lists.append(each_index)

    print('\n')
    print('-'*50)
    if len(is_not_exist_lists) > 0:
        print(f"Not exist lists : {json.dumps(is_not_exist_lists, indent=2)}")
    print(f"Validate the number of docs : {json.dumps(different_doc, indent=2)}")

    ''' *** df ***'''
    all_docs_df.update({"Index_Name" : index_column})
    all_docs_df.update({"source_cluster" : str(source_cluter)})
    all_docs_df.update({"Source Count" : source_cnt})
    all_docs_df.update({"target_cluster" : str(target_cluter)})
    all_docs_df.update({"Target Count" : target_cnt})
    all_docs_df.update({"Reindex Completed" : index_value})

    df = pd.DataFrame.from_dict(all_docs_df)
    print(df.head(10))
    ''' *** df ***'''

    
    ''' clear output file'''
    output_clear()

    ''' export file for different total counts betweenn two clusters'''
    print('\n')
    print(f"Created file for the Index..")
    export_file(es_source_client, es_target_client, different_doc)
    print('-'*50)
    print('\n')
    


if __name__ == "__main__":
    
    '''
    (.venv) ➜  python ./upgrade-script/validate-docs-script.py --es http://source_es_cluster:9200 ---ts http://target_es_cluster:9201
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
    