# -*- coding: utf-8 -*-

import argparse
import sys

import requests, time
import warnings
import os

from elasticsearch import Elasticsearch
import elasticsearch.helpers as es_helpers
from concurrent.futures import ThreadPoolExecutor
import logging
from dotenv import load_dotenv
import json

warnings.filterwarnings('ignore')
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

''' pip install python-dotenv'''
# load_dotenv(dotenv_path="../.env") # will search for .env file in local folder and load variables 
load_dotenv() # will search for .env file in local folder and load variables 

path = os.path.dirname(os.path.abspath(__file__)) + '/performance'
file_output = path + "/chart_data"


def get_headers():
    ''' BASIC Authentication in HTTP Header'''
    # logging.info(f"BASIC AUTH : {os.getenv('BASIC_AUTH')}")
    return {'Content-type': 'application/json', 'Authorization' : '{}'.format(os.getenv('BASIC_AUTH')), 'Connection': 'close'}


def get_es_instance(_host):
    # create a new instance of the Elasticsearch client class
    es_client = Elasticsearch(hosts=_host, headers=get_headers(), verify_certs=False, timeout=60)
    return es_client


def post_url(args):
    # logging.info(f"url : {args[0]}, json : {args[1]}")
    # logging.info(f"args - {args}")
    return requests.post(args[0], json=args[1], headers=get_headers(), verify=False, timeout=600)


def get_dataset_from_omnisearch(env):
    ''' get Dataset with only id lists from ES Cluster'''
    if env == 'local':
        _es_host = "http://localhost:9201"
        query_filter = {"_source": ["_id"], "query": {"match_all": {}}}
    
    omni_es = get_es_instance(_es_host)
    omni_index = "test_idx"
    batch_size = 1000

    results = es_helpers.scan(
        omni_es,
        query=query_filter,
        index=omni_index,
        size=batch_size,
        request_timeout=1800000
    )
    _id_lists = [r['_id'] for r in results]

    return _id_lists


def make_requests(url, search_index, data, number_of_users):
    ''' Give the stress to api'''
    # ?request_cache=false
    list_of_urls = [("{}/{}/_search?request_cache=false".format(url, search_index), data, get_headers())] * int(number_of_users)

    return list_of_urls


def test_request_to_api(url, data):
    ''' request to omnisearch api as test'''
    response = requests.post(url, json=data)

    if response.status_code == 200 or response.status_code == 201:
        # print "JSON Response : {}".format(response.json())
        print("The number of docs : {}".format(response.json()['hits']['total']["value"]))
        print("Time : {}".format(response.elapsed.total_seconds()))
    else:
        print(response.json())


def export_files(labels, metrics):
    ''' export files for metrics'''
    if not os.path.exists(path):
        os.makedirs(path)

    if os.path.exists(file_output):
        print("The file does exist")
        os.remove(file_output)
    else:
        print("The file does not exist")

    ''' add header/datas '''
    with open(f"{file_output}", "a") as f:
        f.write(f"# Labels for search performance" + '\n')
        f.write(f"{','.join(labels)}" + '\n')
        f.write(f"# Metrics for search performance" + '\n')
        f.write(f"{','.join(metrics)}" + '\n')


if __name__ == "__main__":
    """
    * Peformance script 
    python ./upgrade-script/http-es-performance-script.py --ts https://target_es_cluster:9201 --idx test_index
    """
    parser = argparse.ArgumentParser(description="Script that might allow us to use it as an application of Performance comparison with ES Cluster")
    parser.add_argument('-t', '--ts', dest='ts', default="https://localhost:9201", help='host target')
    parser.add_argument('-i', '--idx', dest='idx', default="test_index", help='index')
    args = parser.parse_args()
    
    if args.ts:
        es_target_host = args.ts
    
    if args.idx:
        search_index = args.idx

    number_of_users = 20
    running_mintues = float(60/number_of_users)
    ''' 5 minutes'''
    running_time_seconds = float(running_mintues)*5
    tick = 1
    # --

    # Query
    data = {
        "track_total_hits" : True,
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

    logging.info(f"ES Cluster : {es_target_host}, Query : {json.dumps(data, indent=2)}")
    
    try:
        _seq, interval_x_axis = 1, 0
        average_response_time, sum_response_time, sum_request_count = 0, 0, 0
        chart_x = 0
        metrics, metrics_history, labels_history = [], [], []
        while True:
            if _seq >= int(running_time_seconds) * int(number_of_users):
                # If the response time is late, the number of requests within the specified time is reduced.
                # if time.time() - start >= running_time_seconds:
                break

            # with ThreadPoolExecutor() as pool:
            with ThreadPoolExecutor(max_workers=number_of_users) as pool:
                response_list = list(pool.map(post_url, make_requests(es_target_host, search_index, data, number_of_users)))

            interval_x_axis = interval_x_axis + _seq
            for response in response_list:
                chart_x += 1
                if response.status_code == 200 or response.status_code == 201:
                    print(response, response.json()['hits']['total']["value"], response.elapsed.total_seconds())
                    metrics.append("{},{}".format(interval_x_axis, response.elapsed.total_seconds()))

                    if chart_x % 10 == 0:
                        labels_history.append(str(chart_x))
                        metrics_history.append(str(response.elapsed.total_seconds()))
                    sum_response_time += response.elapsed.total_seconds()
                else:
                    print(response, response.text)

                interval_x_axis += 1
                sum_request_count += 1
                
            _seq += 1
            time.sleep(tick)

        ''' -------------- '''
        ''' Write the performance metrics to file '''
        export_files(labels_history, metrics_history)
        ''' -------------- '''

        print('\n')
        print('---')
        print(f"sum_request_count : {sum_request_count}, sum_response_time : {sum_response_time}, average_response_time : {float(sum_response_time/sum_request_count)}/s")
        print('---')
        print('\n')

    except Exception as e:
        logging.error(e)