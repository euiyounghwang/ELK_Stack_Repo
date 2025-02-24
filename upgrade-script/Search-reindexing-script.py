

# -*- coding: utf-8 -*-
import sys
import json

from elasticsearch import Elasticsearch
import argparse
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd
import threading
from threading import Thread
from Search_Engine import Search
import logging
import warnings
from multiprocessing import Process
import time
from datetime import timedelta
import calendar

warnings.filterwarnings("ignore")

load_dotenv()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

lock = threading.Lock() 


def work(es_source_client, es_target_client, src_idx, dest_idx, index_type, _shards_num=None, body=None, _crawl_type=None):
    ''' 
    The best way to reindex is to use Elasticsearch's builtin Reindex API as it is well supported and resilient to known issues.
    The Elasticsaerch Reindex API uses scroll and bulk indexing in batches , and allows for scripted transformation of data. 
    In Python, a similar routine could be developed:
    '''

    global alias_dict
    global response_total_time, response_request_cnt

    StartTime = datetime.now()
   

    def get_es_api_alias(source_es_client):
        ''' get all alias and set to dict'''
        get_alias_old_cluster = source_es_client.indices.get_alias()
        # print(f"Get alias from old cluster : {json.dumps(get_alias_old_cluster, indent=2)}")

        reset_alias_dict = {}
        for k in get_alias_old_cluster.keys():
            if get_alias_old_cluster.get(k).get('aliases'):
                each_alias = list(get_alias_old_cluster.get(k).get('aliases').keys())
                # print(each_alias)
                reset_alias_dict.update({k : each_alias})
        # print(json.dumps(reset_alias_dict, indent=2))
        print(f"get_es_api_alias : {reset_alias_dict}")

        return reset_alias_dict

    
    es_source_client = es_source_client.replace('\r','')
    es_target_client = es_target_client.replace('\r','')
    src_idx = src_idx.replace('\r','')
    dest_idx = dest_idx.replace('\r','')

    logging.info(f"{es_source_client, es_target_client, src_idx, dest_idx}")

    
    # scroll_time='60s'
    scroll_time='60m'
    batch_size='1000'
    total_progressing = 0
    
    es_obj_s = Search(host=es_source_client)
    es_client = es_obj_s.get_es_instance()

    ''' get/set alias from old cluser'''
    alias_dict = get_es_api_alias(es_client)
    
    
    es_obj_t = Search(host=es_target_client)
    es_t_client = es_obj_t.get_es_instance()
    
    """
    body = {
        # "track_total_hits" : True,
        "query": { 
            "match_all" : {}
        }

        # "query": {
        #     "bool": {
        #     "must": [
        #         {
        #         "range": {
        #             "ADDTS": {
        #             "gte": "2020/12/06",
        #             "format": "yyyy/MM/dd"
        #             }
        #         }
        #         }
        #     ]
        #     }
        # }
    }
    """

    if _shards_num:
        rs = es_client.search(index=[src_idx],
            scroll=scroll_time,
            size=batch_size,
            body=body,
            preference=_shards_num
        )
    else:
        rs = es_client.search(index=[src_idx],
            scroll=scroll_time,
            size=batch_size,
            body=body
        )

    # print(f'Current Size : {len(rs["hits"]["hits"])}')
    total_progressing += int(batch_size)
    logging.info(f'[Crawl type : {_crawl_type} Ingest data .. : {str(total_progressing)}')
    
    ''' usu Search-Engine class '''
    # es_obj_t.create_index(dest_idx)
    
    # es_obj_t.buffered_df_to_es(df=pd.DataFrame.from_dict(rs['hits']['hits']), _index=dest_idx)
    es_obj_t.buffered_json_to_es(raw_json=rs['hits']['hits'], _index=dest_idx, _type=index_type)
    
    while True:
        try:
            # print(f'scroll : {rs["_scroll_id"]}')
            scroll_id = rs['_scroll_id']
            rs = es_client.scroll(scroll_id=scroll_id, scroll=scroll_time)
            if len(rs['hits']['hits']) > 0:
                # logging.info(rs['hits']['hits'])
                es_obj_t.buffered_json_to_es(raw_json=rs['hits']['hits'], _index=dest_idx, _type=index_type)
                total_progressing += int(batch_size)
                logging.info(f'Ingest data .. [_shards_num {_shards_num}]: {str(total_progressing)}')
            else:
                es_client.clear_scroll(body={'scroll_id': [scroll_id]}, ignore=(404, ))
                break;
        except Exception as e:
            logging.error(e)
            # pass
        
        # time.sleep(1)

    """
    ''' remain bulk'''
    if len(es_obj_t.actions) > 0:
        print('\n\n\n########')
        print('REMAINING...')
        print('########\n\n\n')
        ''' calcuate repsonse time '''
        Bulk_StartTime = datetime.now()
        response = es_obj_t.es_client.bulk(body=es_obj_t.actions)
        ''' es v5'''
        # if str(response['errors']).lower() == 'true':
        ''' es v8'''
        if response['errors']:
            # logging.error(response)
            print('\n\n\n\n')
            print(response)
            print('\n\n\n\n')
            pass
        else:
            logging.info("** remain indexing ** : {}".format(len(response['items'])))
            del es_obj_t.actions[:]
    
        Bulk_EndTime = datetime.now()
        ''' accumulate response_total_time'''
        response_total_time += float(str((Bulk_EndTime - Bulk_StartTime).seconds) + '.' + str((Bulk_EndTime - Bulk_StartTime).microseconds).zfill(6)[:2])
        response_request_cnt +=1
        logging.info(f"response_total_time :{response_total_time}, response_request_cnt = {response_request_cnt}")
    """

    '''
    curl -XPOST -u elastic:gsaadmin "http://localhost:9221/cp_test_omnisearch_v2/_search/?pretty" -H 'Content-Type: application/json' -d' {
        "track_total_hits" : true,
        "query": {
            "match_all": {
            }
        },
        "size" : 0
    }'
    
    ''' 
    
    ''' -------'''
    ''' Call to remain buffered '''
    es_obj_t.remained_buffered_json_to_es()
    ''' -------'''
    
    body = {
        "track_total_hits" : True,
        "query": { 
            "match_all" : {}
        }
    }

    es_t_client.indices.refresh(index=dest_idx)

    rs = es_t_client.search(index=[dest_idx],
        body=body
    )

    logging.info('-'*10)
    print(type(rs["hits"]["total"]), str(rs["hits"]["total"]))
    if isinstance(rs["hits"]["total"], int):
        logging.info(f'Validation Search Size : {rs["hits"]["total"]:,}')
    else:
        logging.info(f'Validation Search Size : {rs["hits"]["total"]["value"]:,}')
    logging.info('-'*10)

    EndTime = datetime.now()
    Delay_Time = str((EndTime - StartTime).seconds) + '.' + str((EndTime - StartTime).microseconds).zfill(6)[:2]

    logging.info('Configuration : {}, threading id : {}'.format(_crawl_type, threading.get_native_id()))
    logging.info('Running Time for thread: {} Seconds, {} Minutes'.format(Delay_Time, str(timedelta(seconds=(EndTime - StartTime).seconds))))

    global response_total_time, response_request_cnt, error_flag_list

    lock.acquire()
    response_total_time += es_obj_t.response_total_time
    response_request_cnt += es_obj_t.response_request_cnt

    ''' Update any error if reindexing threads hava an error'''
    error_flag_list.append(es_obj_t.error_flag) 
    lock.release()



if __name__ == "__main__":
    
    '''
    (.venv) ➜  python-platform-engine git:(master) ✗ python ./Search-reindexing-script.py --es http://localhost:9200 --source_index test --ts https://localhost:9201
    '''
    parser = argparse.ArgumentParser(description="Index into Elasticsearch using this script")
    parser.add_argument('-e', '--es', dest='es', default="http://localhost:9209", help='host source')
    parser.add_argument('-t', '--ts', dest='ts', default="http://localhost:9292", help='host target')
    parser.add_argument('-s', '--source_index', dest='source_index', default="cp_recommendation_test", help='source_index')
    parser.add_argument('-y', '--type', dest='type', default="_doc", help='_type')
    # parser.add_argument('-d', '--target_index', dest='target_index', default="test", help='target_index')
    args = parser.parse_args()

    StartTime_Job = datetime.now()

    alias_dict = {}
    total_count, response_total_time, response_request_cnt = 0, 0, 0
    error_flag_list = []
    
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
    
    ''' create threads automatically by using aggregation with time field'''
    is_automate_create_threads = True
    # is_automate_create_threads = False

    thread_lists = []

    def generated_statis_threads():
        ''' search with number of shards'''
        
        global total_count

        ''' create threads as many as shards'''
        # search_shards = 1

        ''' create five multiple threads'''
        search_shards = 5

        query = {
            # "track_total_hits" : True,
            "query": { 
                "match_all" : {}
            }
        }

        es_cnt = Search(host=es_source_host)
        es_client = es_cnt.get_es_instance()

        rs = es_client.search(index=[es_source_index],body=query)
        total_count = int(rs["hits"]["total"])

        try:
            ''' create one threads and run one process for all data per index'''
            if search_shards < 2:
                th = Thread(target=work, args=(es_source_host, es_target_host, es_source_index, es_target_index, index_type, None, query, "Single Threads"))
                # th = Process(target=work, args=(es_source_host, es_target_host, es_source_index, es_target_index, index_type, None, "Single Threads")))
                th.start()
                thread_lists.append(th)
            
            else:
                ''' create five threads for each shard per index'''
                for idx in range(search_shards):
                    ''' GET index/_search?preference=_shards:0 '''
                    _shards_num="_shards:{}".format(str(idx))
                    th = Thread(target=work, args=(es_source_host, es_target_host, es_source_index, es_target_index, index_type, _shards_num, query, "Five Threads"))
                    # th = Process(target=work, args=(es_source_host, es_target_host, es_source_index, es_target_index, index_type, _shards_num, query, "Five Threads"))
                    th.start()
                    thread_lists.append(th)

            # wait for all threads to terminate
            for t in thread_lists:
                while t.is_alive():
                    t.join(0.1)
        
        except Exception as e:
            logging.error(e)
            pass


    if is_automate_create_threads:
        logging.info(f"is_automate_create_threads : {is_automate_create_threads}")

        try:
            es_aggs = Search(host=es_source_host)
            es_client = es_aggs.get_es_instance()

            is_aggs_mode = "month"
            # is_aggs_mode = "quarter"
            # is_aggs_mode = "week"
            
        
            ''' month aggregation'''
            '''
            aggs_query = {
                # "track_total_hits" : True,
                "size": 0,
                "query": {
                    "match_all": {}
                },
                "aggs": {
                    "metrics_by_day": {
                        "date_histogram": {
                            "field": "ADDTS",
                            "interval": "month"
                        }
                    }
                }
            }
            '''
            ''' quarter aggregation'''
            aggs_query = {
                # "track_total_hits" : True,
                "size": 0,
                "query": {
                    "match_all": {}
                },
                "aggs": {
                    "metrics_by_day": {
                        "date_histogram": {
                            "field": "ADDTS",
                            "interval": "%s" % is_aggs_mode
                        }
                    }
                }
            }
            
            rs = es_client.search(index=[es_source_index],body=aggs_query)
            
            date_range = []
            total_buckets_list = rs["aggregations"]["metrics_by_day"]["buckets"]
            total_count = int(rs["hits"]["total"])
            compared_total_count = 0

            if len(total_buckets_list) < 1:
                logging.info(f"is_automate_create_threads to 1 process [{len(total_buckets_list)}]")
                logging.info(f"Call to generated_statis_threads()")
                generated_statis_threads()

            else:
                logging.info(f"is_automate_create_threads to multiple process [{len(total_buckets_list)}]")
                for each_agg in rs["aggregations"]["metrics_by_day"]["buckets"]:
                    if int(each_agg.get("doc_count")) > 0:
                        date_range.append(each_agg.get("key_as_string"))
                    compared_total_count += int(each_agg.get("doc_count"))

                logging.info(f"date_range : {json.dumps(date_range, indent=2)}")
                logging.info(f"The numer of threads : [{len(date_range)}]")
                logging.info(f"total_count : {total_count}, compared_total_count = {compared_total_count}")

                if total_count != compared_total_count:
                    logging.info(f"total_count is different")
                    ''' create add threads for ADDT is null'''
                    query = {
                        "query": {
                            "bool": {
                            "must_not": [
                                {
                                    "exists": {
                                        "field": "ADDTS"
                                    }
                                }
                            ]
                            }
                        }
                    }
                    th = Thread(target=work, args=(es_source_host, es_target_host, es_source_index, es_target_index, index_type, None, query, "{}/{} threads..".format(is_aggs_mode, 'ADDTS_not_exist')))
                    th.start()
                    thread_lists.append(th)
                    # logging.info(query)
                    # sys.exit()

                ''' create numer of threads based on the buckets per index'''
                for idx in range(len(date_range)):
                    ''' GET index/_search '''
                    start_date = str(date_range[idx]).split(' ')[0]
                    t_month = start_date.split("/")[0]
                    t_year = start_date.split("/")[2]
                    input_dt = datetime(int(t_year), int(t_month), 13)
                    res = calendar.monthrange(input_dt.year, input_dt.month)
                    day = res[1]

                    from datetime import date
                    from dateutil.relativedelta import relativedelta

                    if is_aggs_mode == "month":
                        ''' month aggregation'''
                        end_date = "{}/{}/{}".format(t_month, str(day), t_year)

                    elif is_aggs_mode == "quarter":
                        ''' quarter aggregation'''
                        my_date = date(int(t_year),  int(t_month), int(day))
                        end_date = my_date + relativedelta(months=2)
                        end_date = "{}/{}/{}".format(str(end_date).split("-")[1], str(end_date).split("-")[2], str(end_date).split("-")[0])

                    elif is_aggs_mode == "week":
                        ''' week aggregation'''
                        my_date = date(int(t_year),  int(t_month), int(day))
                        end_date = my_date + relativedelta(weeks=1)
                        end_date = "{}/{}/{}".format(str(end_date).split("-")[1], str(end_date).split("-")[2], str(end_date).split("-")[0])
                    
                    query = {
                        "query": {
                            "bool": {
                                "must": [
                                    {
                                        "range": {
                                            "ADDTS": {
                                                "gte": "%s" % start_date,
                                                "lte": "%s" % end_date,
                                                "format": "MM/dd/yyyy"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    }
                    logging.info(f"{json.dumps(query, indent=2)}")
                    
                    logging.info(f"The numer of threads : [{len(date_range)}]")
                    logging.info(f"es_source_index : {es_source_index}")
                    logging.info(f"total_count : {total_count}, compared_total_count = {compared_total_count}")

                    th = Thread(target=work, args=(es_source_host, es_target_host, es_source_index, es_target_index, index_type, None, query, "{}/{} threads..".format(is_aggs_mode, len(date_range))))
                    # th = Process(target=work, args=(es_source_host, es_target_host, es_source_index, es_target_index, index_type, None, query, "[{}] : {} threads..".format(is_aggs_mode, len(date_range))))
                    th.start()
                    thread_lists.append(th)
                    

                # wait for all threads to terminate
                for t in thread_lists:
                    while t.is_alive():
                        t.join(0.1)

        except Exception as e:
            logging.error(e)
            logging.info(f"Call to generated_statis_threads()")
            generated_statis_threads()
    
    else:
        logging.info(f"Call to generated_statis_threads()")
        generated_statis_threads()


    es_script = Search(host=es_target_host)
    es_t_client = es_script.get_es_instance()

    ''' finally'''
    if es_t_client.indices.exists(es_target_index):
        ''' update settings for the number of replica to 1, refresh_interval to null/'''
        es_t_client.indices.put_settings(index=es_target_index, body= {
            "refresh_interval" : None,
            "number_of_replicas": 1
        })

        ''' set alias to target es cluster'''
        if es_target_index in alias_dict.keys():
            es_t_client.indices.put_alias(es_target_index, alias_dict.get(es_source_index))

    EndTime_Job = datetime.now()
    Delay_Time = str((EndTime_Job - StartTime_Job).seconds) + '.' + str((EndTime_Job - StartTime_Job).microseconds).zfill(6)[:2]

    '''' --------------------------'''
    ''' performance metrics'''
    logging.info("\n")
    logging.info("---")
    logging.info("Performance Metrics")
    logging.info('*Running Time for main job: {} Seconds, {} Minutes'.format(Delay_Time, str(timedelta(seconds=(EndTime_Job - StartTime_Job).seconds))))
    logging.info('*Response Time : {}, Request : {}'.format(response_total_time, response_request_cnt))
    ''' This script privides to calculate throughput by dividing the total number of docs reindexed by time, or The total number of docs indexes divided by 1 second. '''
    ''' throughput calcuate : https://blog.naver.com/PostView.nhn?blogId=indy9052&logNo=220948106201'''

    ''' running time on main job '''    
    runnig_time = total_count/(EndTime_Job - StartTime_Job).seconds if (EndTime_Job - StartTime_Job).seconds > 0 else total_count
    ''' Throughput is a measure of how many units of information a system can process in a given amount of time. '''
    logging.info(f'**Total Count: {total_count:,}, Throughput rate : {str(round(float(runnig_time),2))}/s')
    
    ''' response_total_time <- Seconds'''
    avg_response_time = round(float(response_total_time/response_request_cnt), 4)
    logging.info('*Average response time : {}/s'.format(avg_response_time))
    # avg_response_time_ms = "{}/ms".format(str(round(avg_response_time*1000.0, 3))) if avg_response_time < 1 else "{}/ms".format(str(round(avg_response_time, 3)))
    # logging.info('*Average response time : {}/s, *Average response time : {}'.format(avg_response_time))
    logging.info("---")
    logging.info("\n")
    # logging.info(error_flag_list)
    logging.info(f"The number of theads with object for Search-Engine : {len(error_flag_list)}")
    logging.info(f"Verify if reindexing script for index : {es_target_index} has an error {any(error_flag_list)}")
    logging.info("\n")
    '''' --------------------------'''
  