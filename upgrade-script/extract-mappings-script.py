


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


class MD5_Cls:
    ''' The MD5, defined in RFC 1321, is a hash algorithm to turn inputs into a fixed 128-bit (16 bytes) length of the hash value. '''
    def __init__(self):
        pass
    def add(self, data):
        self.data = data
    def encrypt(self):
        self.data = md5(self.data.encode()).hexdigest()
        return "Crypted mapping: "+self.data
    def decrypt(self, data):
        if md5(data.encode()).hexdigest() == self.data:
            return "Decrypted: "+data
            del self.data
        else:
            return "Error"



def work():
    ''' 
    The best way to reindex is to use Elasticsearch's builtin Reindex API as it is well supported and resilient to known issues.
    The Elasticsaerch Reindex API uses scroll and bulk indexing in batches , and allows for scripted transformation of data. 
    In Python, a similar routine could be developed:
    '''

    def import_file(file):
        ''' transform to json format for the host'''
        hosts_dicts = {}
        path = os.path.dirname(os.path.abspath(__file__)) + '/input'
        with open(path + "/{}".format(file)) as data_file:
            for line in data_file:
                if '#' in line:
                    continue
                line = line.strip().split("|")
                hosts_dicts.update({line[0] : line[2].lower()})
            
        return hosts_dicts
    

    def export_file(env, raw_json):
        ''' export to file '''
        path = os.path.dirname(os.path.abspath(__file__)) + '/output'
        if not os.path.exists(path):
             os.makedirs(path)

        with open(f"{path}/mapping", "a") as f:
            ''' call to making_script'''
            f.write('\n')
            f.write(f"# {env}" + '\n')
            f.write(json.dumps(raw_json, indent=2) + '\n')


    def get_mappings(each_index):
        ''' get mappings '''  
        
        def recursive_lookup(k, d):
            if k in d:
                return d[k]
            for v in d.values():
                if isinstance(v, dict):
                    return recursive_lookup(k, v)
            return None
        
        def get_recursive_nested_all(d):
            if isinstance(d, list):
                for i in d:
                    get_recursive_nested_all(i)
            elif isinstance(d, dict):
                for k, v in d.items():
                    if not isinstance(v, (list, dict)):
                        print("%%%%", k, v)
                    else:
                        if "properties" in v:
                            get_recursive_nested_all(v)
                        else:
                            if 'type' not in v:
                                get_recursive_nested_all(v)
                            else:
                                # print("####", k, v)
                                crypt.add(json.dumps(v, sort_keys = True))
                                encryted = crypt.encrypt()
                                if encryted not in idx_json.keys():
                                    # idx_json.update({encryted + "_" + each_index : v})
                                    idx_json.update({encryted : v})

                                
                
        # print(each_index)
        each_mapping = es_client.indices.get_mapping(index=each_index)
        get_only_properties = recursive_lookup("properties", each_mapping)
        crypt = MD5_Cls()
        get_recursive_nested_all(get_only_properties)

        """
        # print(idx_json)
        test_json =  {
            "type": "date",
            "format": "MM/dd/yyyy"
        }
        crypt.add(json.dumps(test_json, sort_keys = True))
        print(crypt.encrypt()) # Encrypt
        print(crypt.decrypt(json.dumps(test_json, sort_keys = True)))
        """
        
    idx_json = {}
  
    # is_dev_mode = True
    is_dev_mode = False

    env_list_dict = import_file("es_list")
    logging.info(json.dumps(env_list_dict, indent=2))

    for k, v in env_list_dict.items():
        es_obj_s = Search(host="{}:9200".format(v))
        es_client = es_obj_s.get_es_instance()

        ''' extact a list of indices from the source cluster'''
        source_idx_lists = es_client.indices.get("*")
        # logging.info(f"{source_idx_lists}")


        # specific_index = "wx_receipt_10052020_20_5_1"
        specific_index = "om_whorder_02072022_22_2_1"

        ''' create index with mappping from ES v.5 after transforming'''
        for each_index in source_idx_lists:
            ''' exclude system indices in the source cluster such as .monitoring-es-7-2024.07.12'''
            if '.' not in each_index:
                if is_dev_mode:
                    if each_index == specific_index:
                        get_mappings(each_index)
                else:
                    if str(each_index).startswith("om") or str(each_index).startswith("wx"):
                        get_mappings(each_index)
                        
        # logging.info(f"idx_json : {json.dumps(idx_json, indent=2)}")
        export_file(k, idx_json)
        idx_json.clear()


if __name__ == "__main__":
    
    '''
    create index with mappings from source cluster to target cluster. It can be put the alias from source to target during reindexing via reindexing script
    (.venv) ➜  python ./upgrade-script/extract-mappings-script.py

    '''
    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        th1 = Thread(target=work, args=())
        th1.start()
        th1.join()
        
    except Exception as e:
        logging.error(e)
        pass
    