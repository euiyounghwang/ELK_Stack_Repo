


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
file_import = path + "/Scan_Ids"
file_output = path + "/Scan_Ids_Duplicate"


def work():
    '''
    Extract all ids via scan API for a mount of records
    '''

    def output_clear():
        if not os.path.exists(path):
             os.makedirs(path)

        if os.path.exists(file_output):
            os.remove(file_output)

    
    def import_file():
        ''' import ids'''
        ids_dict = {}
        ids_duplicate = []
        with open(file_import) as data_file:
            for line in data_file:
                if '#' in line:
                    continue
                lines = line.strip().split("|")
                if lines[0] not in ids_dict.keys():
                    ids_dict.update({lines[0] : line})
                else:
                    ids_duplicate.append(ids_dict.get(lines[0]))
                    ids_duplicate.append(line)

            
        return ids_duplicate
    

    def export_file(query_ids_from_es):
        ''' export to file '''
        with open(f"{file_output}", "a") as f:
            for k in query_ids_from_es:
                f.write(f"{k}")

    duplicate_list = import_file()

    ''' clear file'''
    output_clear()

    ''' add to file'''
    export_file(duplicate_list)              

    

if __name__ == "__main__":
    
    """
    Lookup the duplicate ids
    (.venv) ➜  python ./devops/lookup-id.py
    """
    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        th1 = Thread(target=work)
        th1.start()
        th1.join()
        
    except Exception as e:
        logging.error(e)
        pass
    