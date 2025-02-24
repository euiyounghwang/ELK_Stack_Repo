
# -*- coding: utf-8 -*-
import sys
import json

from dotenv import load_dotenv
import os
from datetime import datetime
from threading import Thread
import logging
import requests
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

path = os.path.dirname(os.path.abspath(__file__))

# read host file to make an dict in memory
def read_hosts(server_file):
    ''' read info'''
    db_url_sql_dicts = {}
    with open(server_file) as data_file:
        for line in data_file:
            db_url_sql_lists = []
            if '#' in line:
                continue
            line = line.strip().split("|")
            db_url_sql_lists.append({"db_url_wmx" : line[1], "sql" : os.getenv('DATA_PIPELINES_SQL')})
            db_url_sql_lists.append({"db_url_omx" : line[2], "sql" : os.getenv('DATA_PIPELINES_SQL')})
            db_url_sql_dicts.update({ line[0] : db_url_sql_lists})

    return db_url_sql_dicts


def db_jobs_work(db_http_host, jdbc_url_dict):

    try:
        logging.info("# HTTP Interface")

        un_returnd_env = []
        for k, v in jdbc_url_dict.items():
            for each_json in v:
                # logging.info(f"each_json : {each_json.get('db_url_wmx')}")

                db_url = each_json.get('db_url_wmx') if each_json.get('db_url_wmx') else each_json.get('db_url_omx')
                # logging.info(f"ENV : {k}, DB_URL : {db_url}, SQL : {each_json.get('sql')}")

                # ''' call to DB interface RestAPI'''
                request_body = {
                        "db_url" : db_url,
                        "sql" : each_json.get('sql')
                }

                logging.info("db_http_host : {}, env : {}, db_url : {}, sql : {}".format(db_http_host, k, db_url, each_json.get('sql')))
                resp = requests.post(url="http://{}/db/get_db_query".format(db_http_host), json=request_body, timeout=120)
                                
                if not (resp.status_code == 200):
                    ''' DB error '''
                    logging.info(f"{resp.json()['message']}")
                                
                logging.info(f"db/process_table - {resp}")
                ''' db job performance through db interface restapi'''
                # db_jobs_performance_gauge_g.labels(server_job=socket.gethostname()).set(int(resp.json["running_time"]))
                result_json_value = resp.json()["results"]
                db_transactin_time = resp.json()["running_time"]

                # logging.info(f"result_json_value : {result_json_value}, db_transactin_time : {db_transactin_time}")
                if len(list(result_json_value)) < 1:
                    un_returnd_env.append({"ENV" : k, "db_url" : db_url})
                    
        
        print('\n')
        print('------')
        print(f"un_returnd_env : {json.dumps(un_returnd_env, indent=2)}")
        print('------')
        print('\n')
        
    except Exception as e:
        logging.error(e)
        pass


if __name__ == "__main__":
    
    '''
    (.venv) ➜  python ./upgrade-script/http-db-records-script.py

    '''
    # --
    # Only One process we can use due to 'Global Interpreter Lock'
    # 'Multiprocessing' is that we can use for running with multiple process
    # --
    try:
        jdbc_url_dict = read_hosts(path + "/input/jdbc_list")
        # logging.info(f"jdbc_url_dict : {json.dumps(jdbc_url_dict, indent=2)}")
        th1 = Thread(target=db_jobs_work, args=(os.getenv('DATA_PIPELINES_HTTP_HOST'), jdbc_url_dict))
        th1.start()
        th1.join()
        
    except Exception as e:
        logging.error(e)
        pass
    