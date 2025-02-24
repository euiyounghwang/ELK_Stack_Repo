
import time
import gradio as gr # type: ignore
import requests
import json
import os
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


js_func = """
function refresh() {
    const url = new URL(window.location);

    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""
def request_api(es_http_host):
    ''' interface es_config_api http://localhost:8004/config/get_mail_config '''
    try:
        resp = requests.get(url="http://{}:8004/config/get_mail_config".format(es_http_host), timeout=5)
                
        if not (resp.status_code == 200):
            ''' save failure node with a reason into saved_failure_dict'''
            logging.error(f"es_config_interface api do not reachable")
            return None

        # logging.info(f"get_mail_config - {resp}, {resp.json()}")
        return resp.json()
        

    except Exception as e:
        logging.error(e)
        pass


def run():

    logging.info(f"Starting")
    
  
if __name__ == '__main__':
    ''' reference : https://www.gradio.app/docs/gradio/checkbox'''
    ''' gradio ./workflow/jupyter_workflow/Alert_Update.py'''
    ''' ./workflow/jupyter_workflow/alert-update-start.sh '''
    run()